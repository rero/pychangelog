#!/usr/bin/env python

import click
from github import Github
from datetime import timedelta


@click.command()
@click.option('--token', help='Github Token.', )
def generate_change_logs(token):
    """."""
    
    # Settings
    # TODO: update settings, branches etc
    g = Github(token)
    repo = g.get_repo("rero/rero-ils")
    staging = repo.get_branch('staging')
    main = repo.get_branch('master')

    from_date = main.commit.commit.committer.date
    to_date = staging.commit.commit.committer.date
    ignore_labels = ["stale", "duplicate", "wontfix", "translations", "task"]
    all_closed_issues = repo.get_issues(state='closed', sort='updated')
    click.secho('Fetching all closed issues and PRs...')

    issues = []
    click.secho(f'Filtering issues closed between {from_date.strftime("%d-%m-%Y")} to {to_date.strftime("%d-%m-%Y")}...')
    for issue in get_all(all_closed_issues):
        if issue.closed_at > from_date + timedelta(minutes=1) and issue.closed_at <= to_date + timedelta(minutes=1):
            issues.append(issue)
        else :
            continue

    out_issues = []
    out_prs = []

    for issue in issues:
        if issue.pull_request:
            pr = repo.get_pull(issue.number)
            if pr.merged and pr.base.label == "rero:staging":
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

# Filter pull requests that are linked to issues by comparing their closed_at date
    final_prs = []
    for pr in out_prs:
        linked_pr = False
        for issue in out_issues:
            if issue.closed_at == pr.closed_at:
                click.secho(f'PR {pr.number} closed with issue {issue.number}. Ignoring.', fg='yellow')
                linked_pr = True
                break
        if not linked_pr:
            final_prs.append(pr)

# TODO: Structure from labels

    print("# Issues \n")
    for issue in out_issues:
        print(f'* {issue.title} [\#{issue.number}]({issue.html_url})')

    print("# Pull Requests \n")
    for issue in final_prs:
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
