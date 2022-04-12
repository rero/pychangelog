#!/usr/bin/env python

import click
import configparser
from github import Github
from datetime import timedelta

# Read config
config = configparser.ConfigParser()
config.read('config.ini')

@click.command()
@click.option('--token', help='Github Token.', )
def generate_change_logs(token):
    """."""
    
    # Settings
    g = Github(token)
    repo_name = f"{config['conf']['user']}/{config['conf']['repo']}"
    repo = g.get_repo(repo_name)
    new_release = repo.get_branch(config['conf']['new_release_branch'])
    latest_release = repo.get_branch(config['conf']['latest_release_branch'])
    ignore_labels = config['conf']['ignore_labels'].split(",")

    from_date = latest_release.commit.commit.committer.date
    to_date = new_release.commit.commit.committer.date
    
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
            if pr.merged and (pr.base.label == config['conf']['user'] + ':' + config['conf']['new_release_branch']):
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

    final_issues = final_prs + out_issues

    export_file(final_issues)


def get_all(results):
    n = 0
    current_page = results.get_page(n)
    while current_page:
        for r in current_page:
            yield r
        n += 1
        current_page = results.get_page(n)

def write_issue(issue):
    '''Takes an issue or PR and returns summary as string.'''
    if issue.pull_request:
        return f'* {issue.title} [\#{issue.number}]({issue.html_url}) ([{issue.user.login}]({issue.user.html_url}))\n'
    else:
        return f'* {issue.title} [\#{issue.number}]({issue.html_url})\n'

def get_labels(issue):
    '''Yields all labels of an issue.'''
    for label in issue.labels:
        yield label.name

def export_file(issues):
    '''Categorizes a list of issues and writes the structure into a markdown file'''

    features = []
    enhancements = []
    bugs = []
    other = []

    for issue in issues:
        #TODO: use config variables for categories
        is_other = True
        for label in get_labels(issue):
            if label in ['new feature', 'user story']:
                features.append(issue)
                is_other = False
                break
            elif label in ['enhancement']:
                enhancements.append(issue)
                is_other = False
                break
            elif label in ['bug', 'bug (critical)', 'correction']:
                bugs.append(issue)
                is_other = False
                break
        if is_other:
            other.append(issue)

    with open('PYCHANGELOG.md', 'w') as f:
        f.write('# Changelog\n')
        if features:
            f.write('\n**New features:**\n')
            for issue in features:
                f.write(write_issue(issue))
        if enhancements:
            f.write('\n**Enhancements:**\n')
            for issue in enhancements:
                f.write(write_issue(issue))
        if bugs:
            f.write('\n**Fixed bugs:**\n')
            for issue in bugs:
                f.write(write_issue(issue))
        f.write('\n**Other changes:**\n')
        for issue in other:
            f.write(write_issue(issue))

if __name__ == '__main__':
    generate_change_logs()
