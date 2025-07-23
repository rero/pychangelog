#!/usr/bin/env python

import configparser
import re
from datetime import datetime

import click
from github import Github

# Read and parse config
config = configparser.ConfigParser()
config.read("./pychangelog/config.ini")

conf = config["conf"]
ignore_labels = conf["ignore_labels"].split(",")
repo_slug = f"{conf['user']}/{conf['repo']}"
token = conf.get("github_token")


@click.command()
@click.option(
    "--token",
    help="Github Token.",
)
def generate_change_logs(token):
    """Generate change logs."""
    g = Github(token)
    repo = g.get_repo(repo_slug)
    merging_branch = repo.get_branch(conf["merging_branch"])

    from_date = get_tag_date(conf["from_tag"], repo) or datetime.min
    to_date = get_tag_date(conf["to_tag"], repo) or datetime.now()

    # Get all closed issues and PRs
    click.secho("Fetching closed issues and PRs...", fg="cyan")
    closed_issues = get_all(
        repo.get_issues(
            state="closed",
            sort="updated",
            since=from_date,
        ),
    )

    # Get only issues that were closed in the selected timeframe
    issues = []
    with click.progressbar(
        closed_issues,
        label="Filtering issues by close date...",
    ) as bar:
        issues.extend(
            issue
            for issue in bar
            if issue.closed_at > from_date and issue.closed_at <= to_date
        )

    click.secho(f"Found {len(issues)} changes.", fg="green")
    # Separate issues and PRs in two distinct lists. Filter issues by
    # ignored_label and PRs by base_branch
    out_issues = []
    out_prs = []

    with click.progressbar(
        issues,
        label="Separating and filtering issues and PRs...",
    ) as bar:
        for issue in bar:
            if issue.pull_request:
                pr = repo.get_pull(issue.number)
                if pr.merged and (
                    pr.base.label == f"{conf['user']}:{merging_branch.name}"
                ):
                    out_prs.append(issue)
            else:
                ignore_issue = 0
                for label in issue.labels:
                    if label.name in ignore_labels:
                        ignore_issue = 1
                        break
                    ignore_issue = 0
                if ignore_issue == 0:
                    out_issues.append(issue)

    click.secho(f"{len(out_issues)} remaining issues.", fg="green")
    click.secho(f"{len(out_prs)} remaining pull requests.", fg="green")
    # Filter pull requests that are linked to issues by looking in the PR
    # body for an issue-closing keyword and the issue number
    click.secho("Filtering pull requests linked to issues...", fg="cyan")
    final_prs = []
    for pr in out_prs:
        linked_pr = False
        for issue in out_issues:
            regex = (
                f"([cC]lose.?.|[fF]ix.?.|[rR]esolve.).*{re.escape(str(issue.number))}"
            )
            if re.search(regex, str(pr.body)):
                click.secho(
                    f"Ignoring PR {pr.number}: '{pr.title}': closed with issue {issue.number}: '{issue.title}'",  # noqa
                    fg="yellow",
                )
                linked_pr = True
                break
        if not linked_pr:
            final_prs.append(pr)

    final_issues = final_prs + out_issues

    click.secho(f"{len(final_issues)} remaining changes.", fg="green")
    click.secho(
        "Structured changelog exported to `PYCHANGELOG.md`!",
        fg="cyan",
        bold=True,
    )

    export_file(final_issues, conf["from_tag"], conf["to_tag"], repo_slug)


def get_all(results):
    """Take a Github API paginated response and iterate through the results."""
    n = 0
    while current_page := results.get_page(n):
        yield from current_page
        n += 1


def get_tag_date(tag_name, repo):
    """Take a tag name and return its latest commit date in the provided repo."""
    for tag in get_all(repo.get_tags()):
        if tag.name == tag_name:
            return tag.commit.commit.committer.date
    return None


def write_issue(issue):
    """Take an issue or PR and return summary as string."""
    if issue.pull_request:
        return f"- {issue.title} [#{issue.number}]({issue.html_url}) (by @{issue.user.login})\n"  # noqa

    if issue.assignees:
        assignees = ", ".join(f"@{assignee.login}" for assignee in issue.assignees)
        return f"- {issue.title} [#{issue.number}]({issue.html_url}) (by {assignees})\n"

    return f"- {issue.title} [#{issue.number}]({issue.html_url})\n"


def get_labels(issue):
    """Yield all labels of an issue."""
    for label in issue.labels:
        yield label.name


def export_file(issues, from_tag, to_tag, repo_slug):
    """Output a list markdown list of issues."""
    features = []
    enhancements = []
    bugs = []
    other = []

    for issue in issues:
        is_other = True
        for label in get_labels(issue):
            if label in ["new feature", "user story"]:
                features.append(issue)
                is_other = False
                break
            if label in ["enhancement"]:
                enhancements.append(issue)
                is_other = False
                break
            if label in ["bug", "bug (critical)", "correction"]:
                bugs.append(issue)
                is_other = False
                break
        if is_other:
            other.append(issue)

    with open("PYCHANGELOG.md", "w") as f:
        f.write(
            f"""# Changelog

## [{to_tag}](https://github.com/{repo_slug}/tree/{to_tag}) ({datetime.date(datetime.now())})

[Full Changelog](https://github.com/{repo_slug}/compare/{from_tag}...{to_tag})
"""  # noqa
        )
        if features:
            f.write("\n**New features:**\n\n")
            for issue in features:
                f.write(write_issue(issue))
        if enhancements:
            f.write("\n**Enhancements:**\n\n")
            for issue in enhancements:
                f.write(write_issue(issue))
        if bugs:
            f.write("\n**Fixes:**\n\n")
            for issue in bugs:
                f.write(write_issue(issue))
        f.write("\n**Other changes:**\n\n")
        for issue in other:
            f.write(write_issue(issue))


if __name__ == "__main__":
    generate_change_logs()
