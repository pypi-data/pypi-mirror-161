import json
import jmespath
import logging
import random

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

    def search_by(self, search_by_term, *args, **kwargs):
        sentry = SentryApi(self.host_url, self.org_slug, self.auth_token)
        search_key, search_val = search_by_term.split("=")

        items = []
        for page in getattr(sentry, self.search_by_api)(*args, **kwargs):
            for item in page:
                value = item.get(search_key)
                if type(value) == bool:
                    if bool(search_val) == value:
                        items.append(item)
                else:
                    if search_val == value:
                        items.append(item)

        print(json.dumps(items, indent=4))

    def get_and_print_all(self, attrs, *args, api=None, jmes_filter="", **kwargs):
        sentry = SentryApi(self.host_url, self.org_slug, self.auth_token)

        # By default the jmes filter is formed by using attrs. We allow the default
        # filter to be overriden by the calling function.
        if jmes_filter == "":
            jmes_filter = f"[].{ multiselect_hash_string(attrs) }"

        api = self.get_and_print_all_api if api is None else api

        for page in getattr(sentry, api)(*args, **kwargs):
            for item in jmespath.search(jmes_filter, page):
                print(", ".join([str(val) for val in item.values()]))
                self.count += 1
        if self.print_count:
            print(f"Count: {self.count}")

    def get_and_print_one(self, *args, api=None, **kwargs):
        sentry = SentryApi(self.host_url, self.org_slug, self.auth_token)

        api = self.get_and_print_one_api if api is None else api
        for page in getattr(sentry, api)(*args, **kwargs):
            print(json.dumps(random.choice(page), indent=4))
            return None


class MembersCommand(Command):
    def __init__(self, **kwargs):
        self.get_and_print_all_api = "org_members_api"
        self.get_and_print_one_api = "org_members_api"
        self.search_by_api = "org_members_api"
        super().__init__(**kwargs)

    def get_and_print_all_by_team(self, attrs, team_slug, role):
        self.get_and_print_all(
            "",
            team_slug,
            jmes_filter=f"[?role == '{role}' && flags.\"sso:linked\"].{ multiselect_hash_string(attrs) }",
            api="team_members_api",
        )


class TeamsCommand(Command):
    def __init__(self, **kwargs):
        self.get_and_print_all_api = "org_teams_api"
        self.get_and_print_one_api = "org_teams_api"
        self.search_by_api = "org_teams_api"
        super().__init__(**kwargs)


class ProjectsCommand(Command):
    def __init__(self, **kwargs):
        self.get_and_print_all_api = "org_projects_api"
        self.get_and_print_one_api = "org_projects_api"
        self.search_by_api = "org_projects_api"
        super().__init__(**kwargs)

    def get_and_print_all_by_team(self, attrs, team_slug):
        self.get_and_print_all(attrs, team_slug, api="team_projects_api")

    def get_and_print_one_by_team(self, team_slug):
        self.get_and_print_one(team_slug, api="team_projects_api")


class UsersCommand(Command):
    def __init__(self, **kwargs):
        self.get_and_print_all_api = "org_users_api"
        self.get_and_print_one_api = "org_users_api"
        self.search_by_api = "org_users_api"
        super().__init__(**kwargs)

    def get_and_print_all(self, attrs):
        super().get_and_print_all(attrs)
        logger.warn(
            "Warning: This command may not list all users because the org_users "
            "api does not paginate. Use the get members command instead for full "
            "list of members."
        )


class ClientKeysCommand(Command):
    def __init__(self, **kwargs):
        self.get_and_print_all_api = "project_keys_api"
        self.get_and_print_one_api = "project_keys_api"
        self.search_by_api = "project_keys_api"
        super().__init__(**kwargs)

    def update_key(self, project_slug, key_id, data):
        if SentryApi(
            self.host_url, self.org_slug, self.auth_token
        ).update_project_client_key(project_slug, key_id, data):
            print(f"Key {key_id} successfully updated.")
