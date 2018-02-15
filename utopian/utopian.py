import click
import datetime
import json
import requests
from dateutil.parser import parse
from collections import Counter
from prettytable import PrettyTable

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
@click.option("--supervisor", is_flag=True,
    help="Flag for only showing supervisors.")
@click.option("--j", is_flag=True, help="Print moderator in JSON format.")
@click.option("--account", default="", help="Specific moderator account.")
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

def build_url(api, query_parameters=None):
    URL = "{}{}/?{}".format(API_BASE_URL, api, urlencode(query_parameters))
    return URL

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
@click.option("--account", default="", help="Sponsor's account name.")
def sponsors(j, account):
    response = requests.get("{}sponsors".format(API_BASE_URL)).json()
    for sponsor in response["results"]:
        if j and account in sponsor["account"]:
            click.echo(json.dumps(sponsor, indent=4, sort_keys=True))
        elif account in sponsor["account"]:
            click.echo(sponsor["account"])

class Date(click.ParamType):
    """
    A custom type for the performance command.
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

def percentage(accepted, rejected):
    if rejected == 0:
        return 100
    elif accepted == 0:
        return 0
    else:
        return round(float(accepted) / (accepted + rejected) * 100)

def contributor_dictionary(response, date):
    contributed_categories = {}
    moderators = {}
    for contribution in response:
        if date < parse(contribution["created"]):
            moderator = contribution["moderator"]
            category = contribution["json_metadata"]["type"]
            reward = round(
                float(contribution["pending_payout_value"].split(" ")[0]))
            if reward == 0:
                author = float(contribution["total_payout_value"].split(" ")[0])
                curator = float(
                    contribution["curator_payout_value"].split(" ")[0])
                reward = round(author + curator)
            contributed_categories.setdefault(category, {
                    "accepted" : 0,
                    "rejected" : 0,
                    "reward" : 0,
                    "total" : 0
                })
            moderators.setdefault(moderator, {
                    "accepted" : 0,
                    "rejected" : 0,
                    "total" : 0
                })
            if contribution["flagged"]:
                contributed_categories[category]["rejected"] += 1
                moderators[moderator]["rejected"] += 1
            else:
                contributed_categories[category]["accepted"] += 1
                moderators[moderator]["accepted"] += 1
            contributed_categories[category]["total"] += 1
            contributed_categories[category]["reward"] += reward
            moderators[moderator]["total"] += 1

    return contributed_categories, moderators

def moderator_dictionary(response, date):
    reviewed_categories = {}
    authors = {}
    for contribution in response:
        if date < parse(contribution["created"]):
            author = contribution["author"]
            category = contribution["json_metadata"]["type"]
            reviewed_categories.setdefault(category, {
                    "accepted" : 0,
                    "rejected" : 0,
                    "total" : 0
                })
            authors.setdefault(author, {
                    "accepted" : 0,
                    "rejected" : 0,
                    "total" : 0
                })
            if contribution["flagged"]:
                reviewed_categories[category]["rejected"] += 1
                authors[author]["rejected"] += 1
            else:
                reviewed_categories[category]["accepted"] += 1
                authors[author]["accepted"] += 1

            reviewed_categories[category]["total"] += 1
            authors[author]["total"] += 1
    return reviewed_categories, authors

def moderator_table(reviewed_categories):
    total_points = 0
    total_accepted = 0
    total_rejected = 0
    table = PrettyTable(["Category", "Reviewed", "Accepted", "Rejected", "%",
        "Points"])

    for key, value in reviewed_categories.items():
        reviewed = value["total"]
        accepted = value["accepted"]
        rejected = value["rejected"]
        accepted_pct = "{}%".format(percentage(accepted, rejected))
        points = category_points(key, reviewed)
        table.add_row([key, reviewed, accepted, rejected, accepted_pct, points])
        total_points += points
        total_accepted += accepted
        total_rejected += rejected

    accepted_pct = "{}%".format(percentage(total_accepted, total_rejected))
    table.add_row(["all", total_accepted + total_rejected, total_accepted,
        total_rejected, accepted_pct, total_points])
    table.align = "r"
    table.align["Category"] = "l"
    return table

def contributor_table(contributed_categories):
    total_accepted = 0
    total_reward = 0
    total_rejected = 0
    table = PrettyTable(["Category", "Contributed", "Accepted", "Rejected", "%",
        "Reward"])

    for key, value in contributed_categories.items():
        reviewed = value["total"]
        accepted = value["accepted"]
        reward = value["reward"]
        rejected = value["rejected"]
        accepted_pct = "{}%".format(percentage(accepted, rejected))
        post_reward = "{}$".format(reward)

        table.add_row([key, reviewed, accepted, rejected, accepted_pct,
            post_reward])
        total_accepted += accepted
        total_reward += reward
        total_rejected += rejected

    accepted_pct = "{}%".format(percentage(total_accepted, total_rejected))
    total_reward = "{}$".format(total_reward)
    table.add_row(["all", total_accepted + total_rejected, total_accepted,
        total_rejected, accepted_pct, total_reward])

    table.align = "r"
    table.align["Category"] = "l"
    return table

def contributor_details(moderators, limit):
    total_accepted = 0
    total_rejected = 0

    table = PrettyTable(["Moderator", "Reviewed", "Accepted", "Rejected", "%"])
    for key, value in sorted(moderators.items(), key=lambda x: x[1]["total"],
        reverse=True)[:limit]:
        accepted = value["accepted"]
        rejected = value["rejected"]
        reviewed = accepted + rejected
        accepted_pct = "{}%".format(percentage(accepted, rejected))
        table.add_row([key, reviewed, accepted, rejected, accepted_pct])
        total_accepted += accepted
        total_rejected += rejected

    accepted_pct = "{}%".format(percentage(total_accepted, total_rejected))
    table.add_row(["all", total_accepted + total_rejected, total_accepted,
        total_rejected, accepted_pct])

    table.align = "r"
    table.align["Moderator"] = "l"
    return table

def moderator_details(authors, limit):
    total_accepted = 0
    total_rejected = 0

    table = PrettyTable(["Author", "Reviewed", "Accepted", "Rejected", "%"])
    for key, value in sorted(authors.items(), key=lambda x: x[1]["total"],
        reverse=True)[:limit]:
        accepted = value["accepted"]
        rejected = value["rejected"]
        reviewed = accepted + rejected
        accepted_pct = "{}%".format(percentage(accepted, rejected))
        table.add_row([key, reviewed, accepted, rejected, accepted_pct])
        total_accepted += accepted
        total_rejected += rejected

    accepted_pct = "{}%".format(percentage(total_accepted, total_rejected))
    table.add_row(["all", total_accepted + total_rejected, total_accepted,
        total_rejected, accepted_pct])

    table.align = "r"
    table.align["Author"] = "l"
    return table

@cli.command()
@click.argument("account", type=str)
@click.option("--date", type=DATE,
    help="See performance for the time period [NOW] - [DATE]")
@click.option("--days", type=int,
    help="See performance for the last N days.")
@click.option("--contributor", "account_type", flag_value="contributor",
    default=True, help="See performance as a contributor.")
@click.option("--moderator", "account_type", flag_value="moderator",
    help="See performance as a moderator.")
@click.option("--details", is_flag=True,
    help="See more details about who you have reviewed/has reviewed you.")
@click.option("--limit", default=10,
    help="Limit the --details table to the top N authors/moderators.")
def performance(account_type, account, date, days, details, limit):
    """
    Takes a given account and either shows the account's performance as a 
    contributor or as a moderator (if applicable) in a given time period.
    """
    if (date and days) or (not date and not days):
        click.echo("Choose either an amount of days or a specific date.")
        return
    if date and datetime.datetime.now() < date:
        click.echo("Argument date must be in the past...")
        return
    if not date and days:
        date = datetime.datetime.now() - datetime.timedelta(days=days)

    if account_type == "moderator" and not is_moderator(account):
        click.echo("{} is not a moderator".format(account))
        return
    elif account_type == "moderator" and is_moderator(account):
        total = requests.get(build_url("posts",
            {"moderator" : account, "limit" : 1})).json()["total"]
        response = requests.get(build_url("posts", {"moderator" : account,
            "limit" : total})).json()["results"]
        
        # Loop over all reviewed contributions and build dictionary
        reviewed_categories, authors = moderator_dictionary(response, date)
        if not details:
            table = moderator_table(reviewed_categories)
        else:
            table = moderator_details(authors, limit)
        click.echo(table)
    elif account_type == "contributor":
        total_accepted = requests.get(build_url("posts", {"section" : "author", 
            "limit" : 1, "author" : account})).json()["total"]
        accepted = requests.get(build_url("posts", {"section" : "author", 
            "limit" : total_accepted, "author" : account})).json()["results"]
        total_rejected = requests.get(build_url("posts", {"section" : "author", 
            "limit" : 1, "author" : account, "status" : "flagged"}
            )).json()["total"]
        rejected = requests.get(build_url("posts", {"section" : "author", 
            "limit" : total_accepted, "author" : account, "status" : "flagged"}
            )).json()["results"]

        accepted.extend(rejected)
        contributed_categories, moderators = contributor_dictionary(accepted,
            date)
        if not details:
            table = contributor_table(contributed_categories)
        else:
            table = contributor_details(moderators, limit)

        click.echo(table)
