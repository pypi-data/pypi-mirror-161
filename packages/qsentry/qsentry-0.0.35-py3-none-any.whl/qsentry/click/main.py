import click

from .utils import comma_separated_string_to_array
from .. import __version__


def add_shared_options(options):
    def _add_shared_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_shared_options


# The shared_options idea is borrowed from https://github.com/pallets/click/issues/108
shared_options = [
    click.option(
        "--attrs",
        default="",
        callback=comma_separated_string_to_array,
        help="""The argument to this option should be a comma separated string.
                For example, "id,name".""",
    ),
    click.option(
        "--auth-token",
        required=True,
        envvar="QSENTRY_AUTH_TOKEN",
        help="""The auth token for invoking sentry apis. Can read from the
                QSENTRY_AUTH_TOKEN env variable.""",
    ),
    click.option(
        "--host-url",
        required=True,
        envvar="QSENTRY_HOST_URL",
        default="https://sentry.io/",
        show_default=True,
        help="""The host URL for the sentry service. Can read from the
                QSENTRY_HOST_URL env variable.""",
    ),
    click.option(
        "--org",
        required=True,
        envvar="QSENTRY_ORG_SLUG",
        help="""The organization slug. Can read from the QSENTRY_ORG_SLUG env
                variable.""",
    ),
    click.option(
        "--count/--no-count",
        is_flag=True,
        default=False,
        help="Show the count of objects (members, teams and etc.)",
    ),
]


@click.group()
@click.version_option(version=__version__)
def main():
    pass
