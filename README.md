# pychangelog

## About Pychangelog

Pychangelog is a Python script that can generate a changelog from your Github **issues** and **pull requests**, filtering and organizing them by **tag**.

Most changelog generators use a Git commit history to fetch changes. But what if the project is managed with issues and pull requests, or the commit messages are not standardized? This is where Pychangelog comes in.

Inspired by [github-changelog-generator](https://github.com/github-changelog-generator/github-changelog-generator).

## Getting started

### Requirements

- Python
- [Poetry](https://python-poetry.org/)
- A Github repo with a repo access token

### Install

1. Clone this repo : `git clone https://github.com/PascalRepond/pychangelog.git`.
2. Run `poetry install` to install dependencies.

## Usage

1. Change the following variables in `changelog.py` according to your needs:
   1. `repo` and `user`: The repo you want a changelog for and its user
   2. `new_release_branch` and `latest_release_branch`: The two branches to compare changes between
   3. `ignore_labels`: Issues and PRs with labels from this list will be ignored
2. Run `poetry run ./changelog.py --token <your-github-token>`
3. Check `PYCHANGELOG.md` for your changelog

## Roadmap

Pychangelog is a side project in early development developed for the use case of the [rero](https://github.com/rero) projects. For now, it can only generate a changelog by comparing the state of two branches. If you need to generate a changelog from your Git history, check one of the many other existing projects that do this. Pychangelog's scope is to use pull requests and issues.

* [x] Print a changelog from issues and PRs
* [x] Add ability to ignore some labels
* [x] Ignore pull requests that are linked to a closed issue
* [x] Generate the changelog in a `markdown` file
* [x] Categorize the issues in the changelog according to specific labels (`bugs`, `enhancements`, etc.)
* [ ] Generate a changelog from release tags instead of branches
* [ ] Generate a complete changelog
* [ ] Update an existing `markdown` file

## Contributing

Do not hesitate to make a pull request or open an issue if you want to enhance or correct the project.

## License

Distributed under [GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/gpl-3.0.html), see `LICENSE` for more details.

## Contact

Pascal Repond - [pascal.repond@rero.ch](mailto:pascal.repond@rero.ch)
Johnny Mariéthoz - [johnny.mariethoz@rero.ch](mailto:johnny.mariethoz@rero.ch)
