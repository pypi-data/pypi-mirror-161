import jmespath
import logging
import pprint

from .api import SentryApi

logger = logging.getLogger(__name__)


def multiselect_hash_string(attributes):
    """Construct and return a jmespath multiselect hash."""
    return "{" + ", ".join([f"{attr}: {attr}" for attr in attributes]) + "}"


class Command:
    def __init__(self, **kwargs):
        self.host_url = kwargs.get("host_url")
        self.org_slug = kwargs.get("org")
        self.auth_token = kwargs.get("auth_token")
        self.print_count = kwargs.get("count")
        self.count = 0

    def call_api_and_print_attrs(self, api, jmes_filter, *args, **kwargs):
        sentry = SentryApi(self.host_url, self.org_slug, self.auth_token)
        for page in getattr(sentry, api)(*args, **kwargs):
            for item in jmespath.search(jmes_filter, page):
                print(", ".join([str(val) for val in item.values()]))
                self.count += 1
        if self.print_count:
            print(f"Count: {self.count}")


class MembersCommand(Command):
    def list_command(self, **kwargs):
        if kwargs["team"]:
            self.handle_the_team_option(kwargs["team"], kwargs["role"])
        else:
            if kwargs.get("attrs"):
                self.handle_the_list_all_option(attrs=kwargs["attrs"])
            else:
                self.handle_the_list_all_option(attrs=["id", "email"])

    def search_by(self, search_by_term):
        key, value = search_by_term.split("=")
        for page in SentryApi(
            self.host_url, self.org_slug, self.auth_token
        ).org_members_api():
            for member in page:
                if member.get(key) == value:
                    pprint.pprint(member)
                    return None

    def handle_the_list_all_option(self, attrs):
        self.call_api_and_print_attrs(
            "org_members_api", f"[].{ multiselect_hash_string(attrs) }"
        )

    def handle_the_team_option(self, team_slug, role):
        self.call_api_and_print_attrs(
            "team_members_api",
            f"[?role == '{role}' && flags.\"sso:linked\"].{ multiselect_hash_string(['id', 'name', 'email']) }",
            team_slug,
        )


class OrgsCommand(Command):
    def list_projects(self, attrs):
        self.call_api_and_print_attrs(
            "org_projects_api", f"[].{ multiselect_hash_string(attrs) }"
        )

    def list_users(self, attrs):
        self.call_api_and_print_attrs(
            "org_users_api", f"[].{ multiselect_hash_string(attrs) }"
        )
        logger.warn(
            "Warning: This command may not list all users because the org_users "
            "api does not paginate. Use the get members command instead for full "
            "list of members."
        )


class TeamsCommand(Command):
    def list_command(self, attrs):
        self.call_api_and_print_attrs(
            "org_teams_api", f"[].{ multiselect_hash_string(attrs) }"
        )

    def list_projects(self, team_slug, attrs):
        self.call_api_and_print_attrs(
            "team_projects_api", f"[].{ multiselect_hash_string(attrs) }", team_slug
        )


class ProjectsCommand(Command):
    def list_keys(self, project_slug, attrs):
        self.call_api_and_print_attrs(
            "project_keys_api", f"[].{ multiselect_hash_string(attrs) }", project_slug
        )

    def update_key(self, project_slug, key_id, data):
        if SentryApi(
            self.host_url, self.org_slug, self.auth_token
        ).update_project_client_key(project_slug, key_id, data):
            print(f"Key {key_id} successfully updated.")
