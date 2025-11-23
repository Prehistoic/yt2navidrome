# yt2navidrome

[![Release](https://img.shields.io/github/v/release/prehistoic/yt2navidrome)](https://img.shields.io/github/v/release/prehistoic/yt2navidrome)
[![Build status](https://img.shields.io/github/actions/workflow/status/prehistoic/yt2navidrome/main.yml?branch=main)](https://github.com/prehistoic/yt2navidrome/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/prehistoic/yt2navidrome/branch/main/graph/badge.svg)](https://codecov.io/gh/prehistoic/yt2navidrome)
[![Commit activity](https://img.shields.io/github/commit-activity/m/prehistoic/yt2navidrome)](https://img.shields.io/github/commit-activity/m/prehistoic/yt2navidrome)
[![License](https://img.shields.io/github/license/prehistoic/yt2navidrome)](https://img.shields.io/github/license/prehistoic/yt2navidrome)

CLI tool to download YT videos and playlists with metadata required for Navidrome

- **Github repository**: <https://github.com/prehistoic/yt2navidrome/>
- **Documentation** <https://prehistoic.github.io/yt2navidrome/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:prehistoic/yt2navidrome.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

> [!IMPORTANT]
> Make sure to have both Poetry and its [Shell plugin](https://github.com/python-poetry/poetry-plugin-shell) installed !
>
> ```
> pipx install poetry
> pipx inject poetry poetry-plugin-shell
> ```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

---
