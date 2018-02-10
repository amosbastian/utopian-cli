import click
import json
import requests
import urllib.parse

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
            if account == "":
                account = moderator["account"]
            if supervisor:
                if ("supermoderator" in moderator 
                    and moderator["supermoderator"] == True
                    and account in moderator["account"]):
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
    return urllib.parse.urlencode(parameters)

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
@click.option("--category", default="blog", help="Category of the contribution.",
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