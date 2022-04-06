#!/usr/bin/env python

import click
from github import Github
from datetime import timedelta


@click.command()
@click.option('--token', help='Github Token.')
def generate_change_logs(token):
    """."""
    
    # Settings
    g = Github(token)
    repo = g.get_repo("rero/rero-ils")
    staging = repo.get_branch('staging')
    main = repo.get_branch('master')

    from_date = main.commit.commit.committer.date
    to_date = staging.commit.commit.committer.date
    ignore_labels = ["stale", "duplicate", "wontfix", "translations", "task"]
    issues = repo.get_issues(state='closed', since=from_date, sort='updated')
    out_issues = []
    out_prs = []
    for issue in get_all(issues):
        if issue.closed_at > to_date + timedelta(minutes=1):
            click.secho(f'{issue.title} {issue.closed_at} {to_date} end after', fg='yellow')
            continue
        if issue.pull_request:
            pr = repo.get_pull(issue.number)
            if pr.merged:
                out_prs.append(issue)
        else:
            ignore_issue = 0
            for label in issue.labels:
                if label.name in ignore_labels:
                    ignore_issue = 1
                    break
                else:
                    ignore_issue = 0
            if ignore_issue == 0:
                out_issues.append(issue)

# TODO: filter pull requests that are linked to issues: either using GarphQL or by using closed_at

# TODO: Structure from labels

    print("# Issues \n")
    for issue in out_issues:
        # number = issue.html_url.split('/').pop()
        print(f'* {issue.title} [\#{issue.number}]({issue.html_url})')

    print("# Pull Requests \n")
    for issue in out_prs:
        number = issue.html_url.split('/').pop()
        print(f'* {issue.title} [\#{issue.number}]({issue.html_url}) [{issue.user.login}]({issue.user.html_url})')


def get_all(results):
    n = 0
    current_page = results.get_page(n)
    while current_page:
        for r in current_page:
            yield r
        n += 1
        current_page = results.get_page(n)

if __name__ == '__main__':
    generate_change_logs()

