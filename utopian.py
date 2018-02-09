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
@click.option("--category", default="all", help="Category of the contribution.")
@click.option("--limit", default=20,
    help="Limit of amount of contributions to retrieve.")
def contribution(category, limit):
    response = requests.get("{}posts/?limit={}&status=any&type={}".format(
        API_BASE_URL, limit, category)).json()
    for contribution in response["results"]:
        click.echo(contribution["title"])