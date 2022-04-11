# pychangelog

## About Pychangelog

Pychangelog is a script that can generate a changelog from your Github **issues** and **pull requests**, filtering and organizing them by **tag**.

Most changelog generators use a Git commit history to create a changelog. But what if, for whatever reason, the project is managed on the basis of issues and pull requests? This is where Pychangleog comes in.

Inspired by [github-changelog-generator](https://github.com/github-changelog-generator/github-changelog-generator).

## Getting started

### Requirements

- Python >3
- [Poetry](https://python-poetry.org/)
- A Github repo and a token with repo access

### Install

1. Clone this repo : `git clone https://github.com/PascalRepond/pychangelog.git`.
2. Run `poetry install` to install dependencies.

## Usage

1. Change the following variables in `changelog.py` according to your needs:
   1. `repo` : The repo you want a changelog for
   2. `staging` and `master` : The two branches to compare changes between
   3. `ignore_labels` : Issues and PRs with the labels from this list will be ignored
2. Run `poetry run ./changelog.py --token <your-github-token>`

## Roadmap

Pychangelog is in early development. For now, it can only generate a changelog with a list of issues and PRs by comparing the state of two branches.

* [x] Print a changelog from issues and PRs
* [x] Add ability to ignore some labels
* [x] Ignore pull requests that are linked to a closed issue
* [ ] Generate the changelog in a `markdown` file
* [ ] Categorize the issues in the changelog according to sepcific labels (`bugs`, `enhancements`, etc.)
* [ ] Generate a changelog from release tags
* [ ] Generate a complete changelog
* [ ] Update an existing `markdown` file

## Contributing

Do not hesitate to make a pull request if you want to enhance or correct the project.

## License

Distributed under [GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/gpl-3.0.html), see `LICENSE` for more details.

## Contact

Pascal Repond - [pascal.repond@rero.ch](mailto:https://www.gnu.org/licenses/gpl-3.0.html)
Johnny Mariéthoz - [johnny.mariethoz@rero.ch](johnny.mariethoz@rero.ch)
