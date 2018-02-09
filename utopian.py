import click
import json
import requests

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

@cli.command()
@click.option("--category", default="all", help="Category of the contribution.",
    type=click.Choice(["all", "blog", "ideas", "sub-projects", "development",
        "bug-hunting", "translations", "graphics", "analysis", "social",
        "documentation", "tutorials", "video-tutorials", "copywriting"]))
@click.option("--limit", default=20,
    help="Limit of amount of contributions to retrieve.")
@click.option("--tags", default="utopian-io",
    help="Tags to filter the contributions by.")
def contribution(category, limit, tags):
    response = requests.get("{}posts/?limit={}&status=any&type={}".format(
        API_BASE_URL, limit, category)).json()

    if tags == "utopian-io":
        tags = tags.split()
    else:
        tags = tags.split(",")

    for contribution in response["results"]:
        if not set(tags).isdisjoint(contribution["json_metadata"]["tags"]):
            click.echo(contribution["title"])
