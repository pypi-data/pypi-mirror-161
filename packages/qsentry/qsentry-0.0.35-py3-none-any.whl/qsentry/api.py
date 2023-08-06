import requests

from urllib.parse import urljoin


class SentryApi:
    def __init__(self, host_url, org_slug, auth_token):
        self.host_url = host_url
        self.org_slug = org_slug
        self.headers = {"Authorization": f"Bearer {auth_token}"}

    def page_iterator(self, url):
        """Return an iterator that goes through the paginated results.

        See https://docs.sentry.io/api/pagination/ for Sentry's pagination API.
        """
        while True:
            res = requests.get(url, headers=self.headers)
            if res.status_code == requests.codes.ok:
                yield res.json()
                if res.links and res.links["next"]["results"] == "true":
                    url = res.links["next"]["url"]
                else:
                    break
            else:
                res.raise_for_status()

    def org_members_api(self):
        url = urljoin(self.host_url, f"/api/0/organizations/{self.org_slug}/members/")
        return self.page_iterator(url)

    def org_projects_api(self):
        url = urljoin(self.host_url, f"/api/0/organizations/{self.org_slug}/projects/")
        return self.page_iterator(url)

    def org_users_api(self):
        url = urljoin(self.host_url, f"/api/0/organizations/{self.org_slug}/users/")
        return self.page_iterator(url)

    def org_teams_api(self):
        url = urljoin(self.host_url, f"/api/0/organizations/{self.org_slug}/teams/")
        return self.page_iterator(url)

    def team_members_api(self, team_slug):
        url = urljoin(
            self.host_url, f"/api/0/teams/{self.org_slug}/{team_slug}/members/"
        )
        return self.page_iterator(url)

    def team_projects_api(self, team_slug):
        url = urljoin(
            self.host_url, f"/api/0/teams/{self.org_slug}/{team_slug}/projects/"
        )
        return self.page_iterator(url)

    def project_keys_api(self, project_slug):
        url = urljoin(
            self.host_url, f"/api/0/projects/{self.org_slug}/{project_slug}/keys/"
        )
        return self.page_iterator(url)

    def update_project_client_key(self, project_slug, key_id, data):
        url = urljoin(
            self.host_url,
            f"/api/0/projects/{self.org_slug}/{project_slug}/keys/{key_id}/",
        )

        # PUT requests require a proper "Content-Type" header, thus we make one
        # from self.headers.
        headers = self.headers.copy()
        headers.update({"Content-Type": "application/json"})

        res = requests.put(url, headers=headers, data=data)
        if res.status_code == requests.codes.ok:
            return True
        else:
            res.raise_for_status()
