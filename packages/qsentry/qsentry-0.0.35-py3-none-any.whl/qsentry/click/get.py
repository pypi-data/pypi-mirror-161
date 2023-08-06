import click


from .main import (
    add_shared_options,
    shared_options,
    main,
)
from ..commands import (
    MembersCommand,
    OrgsCommand,
    ProjectsCommand,
    TeamsCommand,
)


@main.group()
def get():
    """Display resources such as members, teams, organizations and etc."""
    pass


@get.command()
@add_shared_options(shared_options)
@click.option(
    "--team",
    help="""Show the members of a given team. Should be used with --role option
            to filter by roles.""",
)
@click.option(
    "--role", default="admin", show_default=True, help="The role of the member."
)
@click.option(
    "--search-by",
    help="""Search a member by a term.

    The term should be in "<attribute>=<value>" form, for example "id=1234" or
    "email=foo@example.com", etc.
    """,
)
def members(**kwargs):
    """Get the members"""
    if kwargs.get("search_by"):
        MembersCommand(**kwargs).search_by(kwargs["search_by"])
    else:
        MembersCommand(**kwargs).list_command(**kwargs)


@get.command()
@add_shared_options(shared_options)
def teams(**kwargs):
    """Get the teams

    List the team's slug by default. Use the --attrs option to change what
    attributes to show.
    """
    attrs = kwargs["attrs"] if kwargs.get("attrs") else ["slug"]
    TeamsCommand(**kwargs).list_command(attrs)


@get.command()
@add_shared_options(shared_options)
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
        TeamsCommand(**kwargs).list_projects(kwargs["team"], attrs)
    else:
        OrgsCommand(**kwargs).list_projects(attrs)


@get.command()
@add_shared_options(shared_options)
def users(**kwargs):
    """Get all users of the given organization.

    List the user's id and email by default. Use the --attrs option to change
    what attributes to show.
    """
    attrs = kwargs["attrs"] if kwargs.get("attrs") else ["id", "email"]
    OrgsCommand(**kwargs).list_users(attrs)


@get.command()
@add_shared_options(shared_options)
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
    ProjectsCommand(**kwargs).list_keys(kwargs["project"], attrs)
