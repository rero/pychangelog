# pychangelog

## About Pychangelog

Pychangelog is a Python script that can generate a changelog from your Github 
**issues** and **pull requests**, filtering and organizing them by **tag**.

Most changelog generators use a Git commit history to fetch changes. But what 
if the project is managed with issues, labels and pull requests, or the commit messages 
are not standardized? This is where Pychangelog comes in.

Inspired by [github-changelog-generator](https://github.com/github-changelog-generator/github-changelog-generator).

### Features

* Generates a markdown file with a list of Github issues and pull requests that 
have been closed between two selected tags.
* Can ignore issues with certain labels (customizable)
* Automatically ignores pull requests that closed an existing issue, so that 
the same change isn't listed twice.
* Structures the changelog with certain labels as categories : `New features`, 
`Enhancements`, `Fixes`, `Other changes`.

## Getting started

### Requirements

- Python
- [Poetry](https://python-poetry.org/)
- A Github repo with a repo access token

### Install

1. Clone this repo : `git clone https://github.com/rero/pychangelog.git`.
2. Run `poetry install` to install dependencies.

## Usage

1. Edit `config.ini` according to your needs:
   1. `repo` and `user`: The repo you want a changelog for and its user (can be
   an owner or an organization).
   2. `ignore_labels`: Issues and PRs with labels from this list will be ignored
   3. `from_tag` and `to_tag`: The two git tags to compare changes between. 
   `to_tag` doesn't need to exist in Github yet. If it doesn't, the changelog
will compare changes between `from_tag` and today.
   1. `merging_branch`: Only PRs merged to this branch will be used for the
   changelog
2. Run `poetry run ./changelog.py --token <your-github-token>`
3. Check `PYCHANGELOG.md` for your changelog

## Roadmap

Pychangelog is a side project developed for the use case of the [rero](https://github.com/rero) 
projects. It can generate a changelog using Github issues and PRs that have 
been closed between two tags (releases). If you need to generate a changelog 
from your Git history, check one of the many other existing projects that do 
this. Pychangelog's scope is to only use pull requests and issues from Github.

* [x] Print a changelog from issues and PRs
* [x] Add ability to ignore some labels
* [x] Ignore pull requests that are linked to a closed issue
* [x] Generate the changelog in a `markdown` file
* [x] Categorize the issues in the changelog according to specific labels 
(`bugs`, `enhancements`, etc.)
* [x] Generate a changelog from release tags instead of branches
* [ ] Generate a complete changelog
* [ ] Update an existing `markdown` file

## Contributing

Do not hesitate to make a pull request or open an issue if you want to enhance 
or correct the project.

## License

Distributed under [GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/gpl-3.0.html), see `LICENSE` for more details.

## Contact

* Pascal Repond - [pascal.repond@rero.ch](mailto:pascal.repond@rero.ch)
* Johnny Mariéthoz - [johnny.mariethoz@rero.ch](mailto:johnny.mariethoz@rero.ch)
