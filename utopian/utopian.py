import click
import datetime
import json
import requests
from dateutil.parser import parse
from collections import Counter

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

API_BASE_URL = "https://api.utopian.io/api/"
BASE_URL = "https://utopian.io/utopian-io/@{}/{}"

@click.group()
def cli():
    pass

@cli.command()
@click.option("--supervisor", is_flag=True)
@click.option("--j", is_flag=True)
@click.option("--account", default="")
@click.option("--reviewed", default=0,
    help="Minimum amount of contributions reviewed.")
def moderators(supervisor, reviewed, j, account):
    response = requests.get("{}moderators".format(API_BASE_URL)).json()
    for moderator in response["results"]:
        if moderator["total_moderated"] > reviewed:
            if supervisor:
                if ("supermoderator" in moderator 
                    and moderator["supermoderator"] == True):
                    if j:
                        click.echo(json.dumps(moderator, indent=4,
                            sort_keys=True))
                    else:
                        click.echo(moderator["account"])
            elif account in moderator["account"]:
                if j:
                    click.echo(json.dumps(moderator, indent=4,
                        sort_keys=True))
                else:
                    click.echo(moderator["account"])

def query_string(limit, skip, category, author, post_filter):
    """
    Returns a query string created from the given query parameters.
    """
    parameters = {
        "limit" : limit,
        "skip" : skip,
        "section" : "all",
        "type" : category,
        "filterBy" : post_filter
    }
    if not author == "":
        parameters["author"] = author
        parameters["section"] = "author"
    return urlencode(parameters)

def build_response(limit, category, author, post_filter):
    """
    Returns all contributions that match the given parameters.
    """
    skip = 0
    if limit < 1000:
        query = query_string(limit, skip, category, author, post_filter)
        responses = requests.get("{}posts/?{}".format(API_BASE_URL,
            query)).json()["results"]
    else:
        responses = []
        while skip < limit:
            if limit - skip < 1000:
                remainder = limit - skip
                query = query_string(remainder, skip, category, author,
                    post_filter)
            else:
                query = query_string(1000, skip, category, author, post_filter)
            response = requests.get("{}posts/?{}".format(API_BASE_URL,
                query)).json()
            if response["total"] < limit:
                limit = response["total"]
            responses.extend(response["results"])
            skip += 1000
    return responses

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
@click.option("--title", default="",
    help="String that should be in title of the contribution.")
def contributions(category, limit, tags, author, reviewed, title):
    if reviewed:
        post_filter = "any"
    else:
        post_filter = "review"

    contributions = build_response(limit, category, author, post_filter)
    if tags == "utopian-io":
        tags = tags.split()
    else:
        tags = tags.split(",")

    for contribution in contributions:
        if (not set(tags).isdisjoint(contribution["json_metadata"]["tags"])
            and title in contribution["title"]):
            author = contribution["author"]
            permlink = contribution["permlink"]
            click.echo(BASE_URL.format(author, permlink))

@cli.command()
@click.option("--category", default="blog", help="Contribution category.",
    type=click.Choice(["blog", "ideas", "sub-projects", "development",
        "bug-hunting", "translations", "graphics", "analysis", "social",
        "documentation", "tutorials", "video-tutorials", "copywriting"]))
def stats(category):
    response = requests.get("{}/stats".format(API_BASE_URL)).json()["stats"]
    if category:
        for c in response["categories"]:
            if category == c:
                click.echo(json.dumps(response["categories"][c], indent=4,
                    sort_keys=True))

@cli.command()
@click.option("--j", is_flag=True, help="Print sponsor in JSON format.")
@click.option("--account", default="", help="Print sponsor with given name.")
def sponsors(j, account):
    response = requests.get("{}sponsors".format(API_BASE_URL)).json()
    for sponsor in response["results"]:
        if j and account in sponsor["account"]:
            click.echo(json.dumps(sponsor, indent=4, sort_keys=True))
        elif account in sponsor["account"]:
            click.echo(sponsor["account"])

class Date(click.ParamType):
    """
    A custom type for the approved command.
    """
    name = "date"

    def convert(self, value, param, ctx):
        try:
            return parse(value) 
        except ValueError:
            self.fail("{} is not a valid date!".format(value, param, ctx))

DATE = Date()

def is_moderator(account):
    """
    Function that checks if the given account is a moderator or not.
    """
    moderators = requests.get("{}moderators".format(API_BASE_URL)).json()
    return account in [m["account"] for m in moderators["results"]]

def category_points(category, reviewed):
    """
    Convert category to points.
    """
    if category == "translations":
        multiplier = 1.25
    elif (category == "development" or category == "video-tutorials"):
        multiplier = 1.0
    elif (category == "graphics" or category == "tutorials"
        or category == "analysis" or category == "blog"
        or category == "bug-hunting"):
        multiplier = 0.75
    else:
        multiplier = 0.5
    return multiplier * reviewed

@cli.command()
@click.argument("date", type=DATE)
@click.argument("account", type=str)
def points(date, account):
    if datetime.datetime.now() < date:
        click.echo("Argument date must be in the past...")
        return
    if not is_moderator(account):
        click.echo("{} is not a moderator".format(account))
    else:
        # Get total amount of reviewed posts by moderator
        total = requests.get("{}posts/?limit=1&moderator={}".format(
            API_BASE_URL, account)).json()["total"]\
        # Use this as query
        query = "{}posts/?limit={}&moderator={}".format(API_BASE_URL, total,
            account)

        response = requests.get(query).json()["results"]
        reviewed_categories = {}
        authors = []
        # Loop over all reviewed contributions and build dictionary
        for contribution in response:
            if date < parse(contribution["created"]):
                category = contribution["json_metadata"]["type"]
                reviewed_categories.setdefault(category, {
                        "accepted" : 0,
                        "rejected" : 0,
                        "total" : 0
                    })
                if contribution["flagged"]:
                    reviewed_categories[category]["rejected"] += 1
                else:
                    reviewed_categories[category]["accepted"] += 1
                reviewed_categories[category]["total"] += 1

        moderation_points = 0
        total_moderated = 0
        # Print the moderator's overview in the given time period
        for key, value in reviewed_categories.items():
            click.echo(key)
            click.echo("\tReviewed:\t{} ({} / {})".format(value["total"],
                value["accepted"], value["rejected"]))
            c_points = category_points(key, value["total"])
            click.echo("\tPoints:\t\t{}".format(c_points))
            moderation_points += c_points
            total_moderated += value["total"]
        click.echo("Overall")
        click.echo("\tReviewed:\t{}".format(total_moderated))
        click.echo("\tPoints:\t\t{}".format(moderation_points))