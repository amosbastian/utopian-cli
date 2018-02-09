import click
import json
import requests
import urllib.parse

API_BASE_URL = "https://api.utopian.io/api/"

@click.group()
def cli():
    pass

@cli.command()
@click.option("--supervisor", is_flag=True)
@click.option("--moderated", default=0,
    help="Minimum amount of contributions moderated.")
def moderators(supervisor, moderated):
    response = requests.get("{}moderators".format(API_BASE_URL)).json()

    for moderator in response["results"]:
        if moderator["total_moderated"] > moderated:
            if supervisor:
                if ("supermoderator" in moderator 
                    and moderator["supermoderator"] == True):
                    click.echo(moderator["account"])
            else:
                click.echo(moderator["account"])

def query_string(limit, category, author, post_filter):
    """
    Returns a query string created from the given query parameters.
    """
    parameters = {
        "limit" : limit,
        "section" : "all",
        "type" : category,
        "filterBy" : post_filter
    }
    if not author == "":
        parameters["author"] = author
        parameters["section"] = "author"
    return urllib.parse.urlencode(parameters)

@cli.command()
@click.option("--category", default="all", help="Category of the contribution.",
    type=click.Choice(["all", "blog", "ideas", "sub-projects", "development",
        "bug-hunting", "translations", "graphics", "analysis", "social",
        "documentation", "tutorials", "video-tutorials", "copywriting"]))
@click.option("--limit", default=20,
    help="Limit of amount of contributions to retrieve.")
@click.option("--tags", default="utopian-io",
    help="Tags to filter the contributions by.")
@click.option("--author", default="",
    help="Username to filter the contributions by.")
@click.option("--reviewed/--unreviewed", default=True,
    help="Show only reviewed or unreviewed contributions.")
def contribution(category, limit, tags, author, reviewed):
    if reviewed:
        post_filter = "any"
    else:
        post_filter = "review"

    query = query_string(limit, category, author,
        post_filter)
    print("{}posts/{}".format(API_BASE_URL, query))
    response = requests.get("{}posts/?{}".format(API_BASE_URL, query)).json()

    if tags == "utopian-io":
        tags = tags.split()
    else:
        tags = tags.split(",")

    for contribution in response["results"]:
        if not set(tags).isdisjoint(contribution["json_metadata"]["tags"]):
            click.echo(contribution["title"])
