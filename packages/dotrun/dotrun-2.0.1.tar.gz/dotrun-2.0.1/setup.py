# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['dotrun']
install_requires = \
['docker==5.0.3',
 'dockerpty==0.4.1',
 'python-dotenv==0.20.0',
 'python-slugify==6.1.2']

entry_points = \
{'console_scripts': ['dotrun = dotrun:cli']}

setup_kwargs = {
    'name': 'dotrun',
    'version': '2.0.1',
    'description': 'A tool for developing Node.js and Python projects',
    'long_description': '![dotrun](https://assets.ubuntu.com/v1/9dcb3655-dotrun.png?w=200)\n\n# A tool for developing Node.js and Python projects\n\n`dotrun` makes use of a [Docker image](https://github.com/canonical/dotrun-image/) to provide a predictable sandbox for running Node and Python projects.\n\nFeatures:\n\n- Make use of standard `package.json` script entrypoints:\n  - `dotrun` runs `yarn run start` within the Docker container\n  - `dotrun foo` runs `yarn run foo` within the Docker container\n- Detect changes in `package.json` and only run `yarn install` when needed\n- Detect changes in `requirements.txt` and only run `pip3 install` when needed\n- Run scripts using environment variables from `.env` and `.env.local` files\n- Keep python dependencies in `.venv` in the project folder for easy access\n\n## Usage\n\n```bash\n$ dotrun          # Install dependencies and run the `start` script from package.json\n$ dotrun clean    # Delete `node_modules`, `.venv`, `.dotrun.json`, and run `yarn run clean`\n$ dotrun install  # Force install node and python dependencies\n$ dotrun exec     # Start a shell inside the dotrun environment\n$ dotrun exec {command}          # Run {command} inside the dotrun environment\n$ dotrun {script-name}           # Install dependencies and run `yarn run {script-name}`\n$ dotrun -s {script}             # Run {script} but skip installing dependencies\n$ dotrun --env FOO=bar {script}  # Run {script} with FOO environment variable\n```\n\n## Installation\n\nTo install dotrun run:\n```\nsudo pip3 install dotrun\n```\n\n### Requirements\n\n- Linux / macOS\n- Docker ([Get Docker](https://docs.docker.com/get-docker/))\n- Python > 3.6 and PIP\n\n### macOS performance\n\nFor optimal performance on Docker we recommend enabling a new experimental file sharing implementation called virtiofs. Virtiofs is only available to users of the following macOS versions:\n- macOS 12.2 and above (for Apple Silicon)\n- macOS 12.3 and above (for Intel)\n\n[How to enable virtiofs](https://www.docker.com/blog/speed-boost-achievement-unlocked-on-docker-desktop-4-6-for-mac/)\n\n\n## Add dotrun on new projects\n\nTo fully support dotrun in a new project you should do the following:\n\n- For Python projects, ensure [Talisker](https://pypi.org/project/talisker/) is at `0.16.0` or greater in `requirements.txt`\n- Add `.dotrun.json` and `.venv` to `.gitignore`\n- Create a `start` script in `package.json` to do everything needed to set up local development. E.g.:\n  `"start": "concurrently --raw \'yarn run watch\' \'yarn run serve\'"`\n  - The above command makes use of [concurrently](https://www.npmjs.com/package/concurrently) - you might want to consider this\n- Older versions of Gunicorn [are incompatible with](https://forum.snapcraft.io/t/problems-packaging-app-that-uses-gunicorn/11749) strict confinement so we need Gunicorn >= 20\n  - The update [landed in Talisker](https://github.com/canonical-ols/talisker/pull/502) but at the time of writing hasn\'t made it into a new version\n  - If there\'s no new version of Talisker, simply add `gunicorn==20.0.4` to the bottom of `requirements.txt`\n\nHowever, once you\'re ready to completely switch over to `dotrun`, simply go ahead and remove the `run` script.\n\n### Automated tests of pull requests\n\n[The "PR" action](.github/workflows/pr.yaml) builds the Python package and runs a project with dotrun. This will run against every pull request.\n\n### Publish\n\nAll the changes made to the main branch will be automatically published as a new version on PyPI.\n',
    'author': 'Canonical Web Team',
    'author_email': 'webteam@canonical.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
