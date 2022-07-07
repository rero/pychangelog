#!/usr/bin/env python

import click
import configparser
from github import Github
from datetime import datetime, timedelta
import re

# Read and parse config
config = configparser.ConfigParser()
config.read('config.ini')

conf = config['conf']
ignore_labels = conf['ignore_labels'].split(",")
repo_slug = f"{conf['user']}/{conf['repo']}"

@click.command()
@click.option('--token', help='Github Token.',)
def generate_change_logs(token):
    """Main command to generate change logs."""

    # Settings
    g = Github(token)
    repo = g.get_repo(repo_slug)
    merging_branch = repo.get_branch(conf['merging_branch'])

    if get_tag_date(conf['from_tag'], repo):
        from_date = get_tag_date(conf['from_tag'], repo)
    else:
        from_date = datetime.min

    if get_tag_date(conf['to_tag'], repo):
        to_date = get_tag_date(conf['to_tag'], repo)
    else:
        to_date = datetime.now()

    # Get all closed issues and PRs
    click.secho('Fetching all closed issues and PRs...', fg='cyan')
    all_closed_issues = get_all(repo.get_issues(state='closed', sort='updated'))

    # Get only issues closed in the selected timeframe
    issues = []
    with click.progressbar(all_closed_issues, label=f'Filtering issues closed between {from_date.strftime("%d-%m-%Y")} to {to_date.strftime("%d-%m-%Y")}...') as bar:
        for issue in bar:
            if issue.closed_at > from_date + timedelta(minutes=1) and issue.closed_at <= to_date + timedelta(minutes=1):
                issues.append(issue)
    click.secho(f'Found {len(issues)} changes.', fg='green')


# Separate issues and PRs in two distinct lists. Filter issues by
# ignored_label and PRs by base_branch
    out_issues = []
    out_prs = []

    with click.progressbar(issues, label=f'Separating and filtering issues and PRs...') as bar:
        for issue in bar:
            if issue.pull_request:
                pr = repo.get_pull(issue.number)
                if pr.merged and (pr.base.label == f"{conf['user']}:{merging_branch.name}"):
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

    click.secho(f'{len(out_issues)} remaining issues.', fg='green')
    click.secho(f'{len(out_prs)} remaining pull requests.', fg='green')

# Filter pull requests that are linked to issues by looking in the PR
# body for an issue-closing keyword and the issue number
    click.secho(f'Filtering pull requests linked to issues...', fg='cyan')
    final_prs = []
    for pr in out_prs:
        linked_pr = False
        for issue in out_issues:

            regex = r"([cC]lose.?.|[fF]ix.?.|[rR]esolve.).*" + re.escape(str(issue.number))
            match = re.search(regex, str(pr.body))

            if match :
                click.secho(f'Ignoring PR {pr.number}: \'{pr.title}\': closed with issue {issue.number}: \'{issue.title}\'', fg='yellow')
                linked_pr = True
                break
        if not linked_pr:
            final_prs.append(pr)

    final_issues = final_prs + out_issues

    click.secho(f'{len(final_issues)} remaining changes.', fg='green')
    click.secho(f'Structured changelog exported to `PYCHANGELOG.md`!', fg='cyan', bold=True)

    export_file(final_issues, conf['from_tag'], conf['to_tag'], repo_slug)


def get_all(results):
    '''Takes a Github API paginated response and iterates through the results.'''
    n = 0
    current_page = results.get_page(n)
    while current_page:
        for r in current_page:
            yield r
        n += 1
        current_page = results.get_page(n)

def get_tag_date(tag_name, repo):
    '''Takes a tag name and returns its latest commit date if it exists in the provided repo'''

    for tag in get_all(repo.get_tags()):
        if tag.name == tag_name:
            return tag.commit.commit.committer.date

def write_issue(issue):
    '''Takes an issue or PR and returns summary as string.'''
    if issue.pull_request:
        return f'* {issue.title} [\#{issue.number}]({issue.html_url}) (by @{issue.user.login})\n'

    elif issue.assignees:
        assignees = ""
        for assignee in issue.assignees:
            assignees += "@"+assignee.login+", "
        return f'* {issue.title} [\#{issue.number}]({issue.html_url}) (by {assignees.rstrip(", ")})\n'

    else:
        return f'* {issue.title} [\#{issue.number}]({issue.html_url})\n'

def get_labels(issue):
    '''Yields all labels of an issue.'''

    for label in issue.labels:
        yield label.name

def export_file(issues, from_tag, to_tag, repo_slug):
    '''Categorizes a list of issues and outputs it into a structured 
    markdown changelog'''

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
        f.write(f'''# Changelog

## [{to_tag}](https://github.com/{repo_slug}/tree/{to_tag}) ({datetime.date(datetime.now())})

[Full Changelog](https://github.com/{repo_slug}/compare/{from_tag}...{to_tag})
''')
        if features:
            f.write('\n**New features:**\n')
            for issue in features:
                f.write(write_issue(issue))
        if enhancements:
            f.write('\n**Enhancements:**\n')
            for issue in enhancements:
                f.write(write_issue(issue))
        if bugs:
            f.write('\n**Fixes:**\n')
            for issue in bugs:
                f.write(write_issue(issue))
        f.write('\n**Other changes:**\n')
        for issue in other:
            f.write(write_issue(issue))

if __name__ == '__main__':
    generate_change_logs()
