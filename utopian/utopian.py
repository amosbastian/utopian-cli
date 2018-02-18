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

UTOPIAN_API = "https://api.utopian.io/api/"
GITHUB_API = "https://api.github.com/"
BASE_URL = "https://utopian.io/utopian-io/@{}/{}"
UTOPIAN_TEAM = "https://utopian.team/users/team.json"

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
    response = requests.get("{}moderators".format(UTOPIAN_API)).json()
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
    URL = "{}{}/?{}".format(UTOPIAN_API, api, urlencode(query_parameters))
    return URL

def build_response(limit, category, author, post_filter):
    """
    Returns all contributions that match the given parameters.
    """
    skip = 0
    if limit < 1000:
        query = query_string(limit, skip, category, author, post_filter)
        responses = requests.get("{}posts/?{}".format(UTOPIAN_API,
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
            response = requests.get("{}posts/?{}".format(UTOPIAN_API,
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
    response = requests.get("{}/stats".format(UTOPIAN_API)).json()["stats"]
    if category:
        for c in response["categories"]:
            if category == c:
                click.echo(json.dumps(response["categories"][c], indent=4,
                    sort_keys=True))

@cli.command()
@click.option("--j", is_flag=True, help="Print sponsor in JSON format.")
@click.option("--account", default="", help="Sponsor's account name.")
def sponsors(j, account):
    response = requests.get("{}sponsors".format(UTOPIAN_API)).json()
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
    Function that checks if the given account(s) are moderators or not.
    """
    moderators = requests.get("{}moderators".format(UTOPIAN_API)).json()
    return set(account).issubset([m["account"] for m in moderators["results"]])

def is_supervisor(account):
    """
    Function that checks if the given account(s) are supervisors or not.
    """
    moderators = requests.get("{}moderators".format(UTOPIAN_API)).json()
    return set(account).issubset([m["account"] for m in moderators["results"]
        if "supermoderator" in m.keys()])

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
        if not "moderator" in contribution.keys():
            continue
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

def details_table(users, limit, sort, column):
    total_accepted = 0
    total_rejected = 0

    table = PrettyTable([column, "Reviewed", "Accepted", "Rejected", "%"])
    for key, value in sorted(users.items(), key=lambda x: x[1][sort],
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
    table.align[column] = "l"
    return table

def date_validator(date, days):
    if (date and days) or (not date and not days):
        click.echo("Choose either an amount of days or a specific date.")
        return
    if date and datetime.datetime.now() < date:
        click.echo("Argument date must be in the past...")
        return
    if days and days < 1:
        click.echo("Unfortunately we can't look into the future...")
    if not date and days:
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        return date

def filter_by_author(contributions, authors):
    """
    Filter the given contributions by the given authors.
    """
    filtered_contributions = []
    for contribution in contributions:
        if contribution["author"] in authors:
            filtered_contributions.append(contribution)
    return filtered_contributions

def filter_by_category(contributions, categories):
    """
    Filter the given contributions by the given categories.
    """
    filtered_contributions = []
    for contribution in contributions:
        if contribution["json_metadata"]["type"] in categories:
            filtered_contributions.append(contribution)
    return filtered_contributions

def supervisor_team(account):
    accounts = []
    teams = requests.get(UTOPIAN_TEAM).json()["results"]
    for a in account:
        for member in teams[a]["members"]:
            accounts.append(member["account"])
    return tuple(accounts)

@cli.command()
@click.option("--account", "-a", type=str, multiple=True, required=True)
@click.option("--date", type=DATE,
    help="See performance for the time period [NOW] - [DATE]")
@click.option("--days", type=int,
    help="See performance for the last N days.")
@click.option("--contributor", "account_type", flag_value="contributor",
    default=True, help="See performance as a contributor.")
@click.option("--moderator", "account_type", flag_value="moderator",
    help="See performance as a moderator.")
@click.option("--supervisor", "account_type", flag_value="supervisor",
    help="See performance of a supervisor's team.")
@click.option("--details", is_flag=True,
    help="See more details about who you have reviewed/has reviewed you.")
@click.option("--limit", default=10,
    help="Limit the --details table to the top N authors/moderators.")
@click.option("--sort", default="total", help="Value to sort the table by.",
    type=click.Choice(["total", "accepted", "rejected"]))
def performance(account_type, account, date, days, details, limit, sort):
    """
    Takes a given account and either shows the account's performance as a 
    contributor or as a moderator (if applicable) in a given time period.
    """
    date = date_validator(date, days)
    if not date:
        return

    if account_type == "moderator" and not is_moderator(account):
        if len(account) == 1:
            click.echo("{} is not a moderator.".format("".join(account)))
        else:
            click.echo("{} aren't all moderators.".format(", ".join(account)))
        return
    elif account_type == "supervisor" and not is_supervisor(account):
        if len(account) == 1:
            click.echo("{} is not a supervisor.".format("".join(account)))
        else:
            click.echo("{} aren't all supervisors.".format(", ".join(account)))
    elif ((account_type == "moderator" and is_moderator(account)) or
        (account_type == "supervisor" and is_supervisor(account))):
        if account_type == "supervisor":
            account = supervisor_team(account)
        responses = []
        with click.progressbar(account) as bar:
            for user in bar:
                total = requests.get(build_url("posts",
                    {"moderator" : user, "limit" : 1})).json()["total"]
                response = requests.get(build_url("posts", {"moderator" : user,
                    "limit" : total})).json()["results"]
                responses.extend(response)
        
        # Loop over all reviewed contributions and build dictionary
        reviewed_categories, authors = moderator_dictionary(responses, date)
        if not details:
            table = moderator_table(reviewed_categories)
        else:
            table = details_table(authors, limit, sort, "Author")
        click.echo(table)
    elif account_type == "contributor":
        responses = []
        for a in account:
            total_accepted = requests.get(build_url("posts", {"section" : "author", 
                "limit" : 1, "author" : a})).json()["total"]
            accepted = requests.get(build_url("posts", {"section" : "author", 
                "limit" : total_accepted, "author" : a})).json()["results"]
            total_rejected = requests.get(build_url("posts", {"section" : "author", 
                "limit" : 1, "author" : a, "status" : "flagged"}
                )).json()["total"]
            rejected = requests.get(build_url("posts", {"section" : "author", 
                "limit" : total_accepted, "author" : a, "status" : "flagged"}
                )).json()["results"]
            responses.extend(rejected)
            responses.extend(accepted)
        
        contributed_categories, moderators = contributor_dictionary(responses,
            date)
        if not details:
            table = contributor_table(contributed_categories)
        else:
            table = details_table(moderators, limit, sort, "Moderator")

        click.echo(table)


def project_dictionary(contributions, date):
    reviewed_categories = {}
    authors = {}
    for contribution in contributions:
        if not "moderator" in contribution.keys():
            continue
        if date < parse(contribution["created"]):
            author = contribution["author"]
            category = contribution["json_metadata"]["type"]
            reward = round(
                float(contribution["pending_payout_value"].split(" ")[0]))
            if reward == 0:
                author_reward = float(
                    contribution["total_payout_value"].split(" ")[0])
                curator_reward = float(
                    contribution["curator_payout_value"].split(" ")[0])
                reward = round(author_reward + curator_reward)
            reviewed_categories.setdefault(category, {
                    "accepted" : 0,
                    "rejected" : 0,
                    "total" : 0,
                    "reward" : 0
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
            reviewed_categories[category]["reward"] += reward
            authors[author]["total"] += 1
    return reviewed_categories, authors

@cli.command()
@click.argument("repository", type=str)
@click.option("--date", type=DATE,
    help="See performance for the time period [NOW] - [DATE]")
@click.option("--days", type=int,
    help="See performance for the last N days.")
@click.option("--details", is_flag=True,
    help="See more details about who you have reviewed/has reviewed you.")
@click.option("--limit", default=10,
    help="Limit the --details table to the top N authors/moderators.")
@click.option("--sort", default="total", help="Value to sort the table by.",
    type=click.Choice(["total", "accepted", "rejected"]))
@click.option("--author", "-a", type=str, multiple=True,
    help="Author to filter the table by.")
@click.option("--category", "-c", type=click.Choice(["all", "blog", "ideas", 
    "sub-projects", "development", "bug-hunting", "translations", "graphics",
    "analysis", "social", "documentation", "tutorials", "video-tutorials",
    "copywriting"]), multiple=True)
def project(author, category, date, days, details, limit,
    repository, sort):

    date = date_validator(date, days)
    if not date:
        return
    response = requests.get("{}repos/{}".format(GITHUB_API, repository)).json()
    if "id" in response.keys():
        repository_id = response["id"]
    else:
        click.echo("Please enter a valid GitHub repository.")
        return

    query_parameters = {
        "section" : "project",
        "platform" : "github",
        "projectId" : repository_id,
        "limit" : 1,
        "status" : "any"
    }
    all_contributions = []

    total_accepted = requests.get(build_url("posts",
        query_parameters)).json()["total"]
    query_parameters["status"] = "flagged"
    total_rejected = requests.get(build_url("posts",
        query_parameters)).json()["total"]
    if total_accepted + total_rejected == 0:
        click.echo("No contributions have been made to this project...")
        return
    else:
        if total_rejected > 0:
            query_parameters["limit"] = total_rejected
            rejected = requests.get(build_url("posts",
                query_parameters)).json()["results"]
            all_contributions.extend(rejected)
        if total_accepted > 0:
            query_parameters["limit"] = total_accepted
            query_parameters["status"] = "any"
            accepted = requests.get(build_url("posts",
                query_parameters)).json()["results"]
            all_contributions.extend(accepted)
        if author:
            all_contributions = filter_by_author(all_contributions, author)
        if category:
            all_contributions = filter_by_category(all_contributions, category)
        project_categories, authors = project_dictionary(all_contributions,
            date)
        if not details:
            table = contributor_table(project_categories)
        else:
            table = details_table(authors, limit, sort, "Author")
        click.echo(table)