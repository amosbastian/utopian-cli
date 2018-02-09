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