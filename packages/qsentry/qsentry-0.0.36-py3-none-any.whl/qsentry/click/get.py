import click


from .main import (
    add_shared_options,
    shared_options,
    main,
)
from .utils import add_shared_options
from ..commands import (
    ClientKeysCommand,
    MembersCommand,
    ProjectsCommand,
    TeamsCommand,
    UsersCommand,
)


shared_get_options = [
    click.option(
        "--one",
        is_flag=True,
        default=False,
        help="""Get one json formated example of the requested resource.""",
    ),
    click.option(
        "--search-by",
        help="""Search a resource by a term. The term should be in
        "<attribute>=<value>" form, for example "id=1234" or
        "email=foo@example.com", etc.
        """,
    ),
]


@main.group()
def get():
    """Display resources such as members, teams, organizations and etc."""
    pass


@get.command()
@add_shared_options(shared_options)
@add_shared_options(shared_get_options)
@click.option(
    "--team",
    help="""Show the members of a given team. Should be used with --role option
            to filter by roles.""",
)
@click.option(
    "--role", default="admin", show_default=True, help="The role of the member."
)
def members(**kwargs):
    """Get the members"""
    attrs = kwargs["attrs"] if kwargs.get("attrs") else ["id", "email"]
    if kwargs.get("one"):
        MembersCommand(**kwargs).get_and_print_one()
    elif kwargs.get("search_by"):
        MembersCommand(**kwargs).search_by(kwargs["search_by"])
    else:
        if kwargs.get("team"):
            MembersCommand(**kwargs).get_and_print_all_by_team(
                attrs, kwargs.get("team"), kwargs.get("role")
            )
        else:
            MembersCommand(**kwargs).get_and_print_all(attrs)


@get.command()
@add_shared_options(shared_options)
@add_shared_options(shared_get_options)
def teams(**kwargs):
    """Get the teams

    List the team's slug by default. Use the --attrs option to change what
    attributes to show.
    """
    attrs = kwargs["attrs"] if kwargs.get("attrs") else ["slug"]
    if kwargs.get("one"):
        TeamsCommand(**kwargs).get_and_print_one()
    elif kwargs.get("search_by"):
        TeamsCommand(**kwargs).search_by(kwargs["search_by"])
    else:
        TeamsCommand(**kwargs).get_and_print_all(attrs)


@get.command()
@add_shared_options(shared_options)
@add_shared_options(shared_get_options)
@click.option(
    "--team",
    help="""Get the projects of the given team""",
)
def projects(**kwargs):
    """Get the projects

    List the project's id, name and slug by default. Use the --attrs option to
    change what attributes to show.
    """
    attrs = kwargs["attrs"] if kwargs.get("attrs") else ["id", "name", "slug"]
    if kwargs.get("team"):
        if kwargs.get("one"):
            ProjectsCommand(**kwargs).get_and_print_one_by_team(kwargs["team"])
        else:
            ProjectsCommand(**kwargs).get_and_print_all_by_team(attrs, kwargs["team"])
    else:
        if kwargs.get("one"):
            ProjectsCommand(**kwargs).get_and_print_one()
        elif kwargs.get("search_by"):
            ProjectsCommand(**kwargs).search_by(kwargs["search_by"])
        else:
            ProjectsCommand(**kwargs).get_and_print_all(attrs)


@get.command()
@add_shared_options(shared_options)
@add_shared_options(shared_get_options)
def users(**kwargs):
    """Get all users of the given organization.

    List the user's id and email by default. Use the --attrs option to change
    what attributes to show.
    """
    attrs = kwargs["attrs"] if kwargs.get("attrs") else ["id", "email"]
    if kwargs.get("one"):
        UsersCommand(**kwargs).get_and_print_one()
    elif kwargs.get("search_by"):
        UsersCommand(**kwargs).search_by(kwargs["search_by"])
    else:
        UsersCommand(**kwargs).get_and_print_all(attrs)


@get.command()
@add_shared_options(shared_options)
@add_shared_options(shared_get_options)
@click.option(
    "--project",
    required=True,
    help="""The project slug""",
)
def client_keys(**kwargs):
    """Get all client keys of the given project.

    List the key's id, dsn and rate limit by default. Use the --attrs option to
    change what attributes to show.
    """
    attrs = kwargs["attrs"] if kwargs.get("attrs") else ["id", "dsn", "rateLimit"]
    if kwargs.get("one"):
        ClientKeysCommand(**kwargs).get_and_print_one(kwargs["project"])
    else:
        ClientKeysCommand(**kwargs).get_and_print_all(attrs, kwargs["project"])
