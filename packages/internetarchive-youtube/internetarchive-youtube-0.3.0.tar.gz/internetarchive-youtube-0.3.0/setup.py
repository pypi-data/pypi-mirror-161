# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['internetarchive_youtube']

package_data = \
{'': ['*']}

install_requires = \
['internetarchive>=3.0.0',
 'loguru>=0.6.0',
 'pymongo[srv]>=4.0.2',
 'python-dotenv>=0.20',
 'requests>=2.27',
 'tqdm>=4.60.0',
 'yt-dlp>=2022.5.18']

entry_points = \
{'console_scripts': ['ia-yt = internetarchive_youtube:cli.main',
                     'ia_yt = internetarchive_youtube:cli.main',
                     'internetarchive-youtube = '
                     'internetarchive_youtub:cli.main',
                     'internetarchive_youtube = '
                     'internetarchive_youtub:cli.main']}

setup_kwargs = {
    'name': 'internetarchive-youtube',
    'version': '0.3.0',
    'description': 'Archives YouTube channels by automatically uploading their videos to archive.org',
    'long_description': '# Internetarchive-YouTube\n\n[![Poetry-build](https://github.com/Alyetama/internetarchive-youtube/actions/workflows/poetry-build.yml/badge.svg)](https://github.com/Alyetama/internetarchive-youtube/actions/workflows/poetry-build.yml) [![Supported Python versions](https://img.shields.io/badge/Python-%3E=3.7-blue.svg)](https://www.python.org/downloads/) [![PEP8](https://img.shields.io/badge/Code%20style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/) \n\n🚀 GitHub Action and CLI tool to archive YouTube channels by automatically uploading an entire YouTube channel to [archive.org](https://archive.org) in few clicks.\n\n## 📌 Global Requirements\n\n- All you need is an [Internet Archive account](https://archive.org/account/signup).\n\n## 🔧 Usage\n\n- ⚡️ To use this tool as a GitHub Action, jump to [GitHub Action: Getting Started](<#%EF%B8%8F-github-action-getting-started> "GitHub Action: Getting Started").\n- 🧑\u200d💻 To use this tool as a command line interface (CLI), jump to [CLI: Getting Started](<#-cli-getting-started> "CLI: Getting Started").\n\n---\n\n### ⚡️ GitHub Action: Getting Started\n\n<details>\n  <summary>Using internetarchive-youtube as a GitHub Action instructions</summary>\n\n1. **[Fork this repository](https://github.com/Alyetama/yt-archive-sync/fork).**\n\n2. **Enable the workflows in your fork.**\n\n<img src="https://i.imgur.com/J1udGei.jpeg"  width="720" alt=""> \n<img src="https://i.imgur.com/WhyFjWy.jpeg"  width="720" alt=""> \n\n3. **[Create a backend database (or JSON bin)](<#%EF%B8%8F-creating-a-backend-database> "Creating a backend database").**\n\n4. **Add your *Archive.org* credentials to the repository\'s actions secrets:**\n  - `ARCHIVE_USER_EMAIL`\n  - `ARCHIVE_PASSWORD`\n\n5. **Add a list of the channels you want to archive as a `CHANNELS` secret to the repository\'s actions secrets:**\n\nThe `CHANNELS` secret should be formatted like this example:\n\n```YAML\nCHANNEL_NAME: CHANNEL_URL\nFOO: FOO_CHANNEL_URL\nFOOBAR: FOOBAR_CHANNEL_URL\nSOME_CHANNEL: SOME_CHANNEL_URL\n```\n\nDon\'t add any quotes around the name or the URL, and make sure to keep one space between the colon and the URL.\n\n6. **Add the database secret(s) to the repository\'s *Actions* secrets:**\n\nIf you picked **option 1 (MongoDB)**, add this secret:\n  - `MONGODB_CONNECTION_STRING`\nThe value of the secret is the database conneciton string.\n\nIf you picked **option 2 (JSON bin)**, add this additional secret:\n  - `JSONBIN_KEY`  \nThe value of this secret is the *MASTER KEY* token you copied from JSONbin.\n\n7. (optional) You can add command line options other than the defaults by creating a secret called `CLI_OPTIONS` and adding the options to the secret. See the [CLI: Getting Started](<#-cli-getting-started> "CLI: Getting Started") for a list of all the available options.\n\n8. **Run the workflow under `Actions` manually, or wait for it to run automatically every 6 hours.**\n\nThat\'s it! 🎉\n\n</details>\n\n\n### 🧑\u200d💻 CLI: Getting Started\n\n<details>\n  <summary>Using internetarchive-youtube as a CLI tool instructions</summary>\n\n#### Requirements:\n\n- 🐍 [Python>=3.7](https://www.python.org/downloads/)\n\n#### ⬇️ Installation:\n\n```sh\npip install internetarchive-youtube\n```\n\nThen login to internetarchive:\n\n```sh\nia configure\n```\n\n#### 🗃️ Backend database:\n\n- [Create a backend database (or JSON bin)](<#%EF%B8%8F-creating-a-backend-database> "Creating a backend database") to track the download/upload overall progress.\n\n- If you choose **MongoDB**, export the connection string as an environment variable:\n\n```sh\nexport MONGODB_CONNECTION_STRING=mongodb://username:password@host:port\n\n# or add it to your shell configuration file:\necho "MONGODB_CONNECTION_STRING=$MONGODB_CONNECTION_STRING" >> "$HOME/.$(basename $SHELL)rc"\nsource "$HOME/.$(basename $SHELL)rc"\n```\n\n- If you choose **JSONBin**, export the master key as an environment variable:\n\n```sh\nexport JSONBIN_KEY=xxxxxxxxxxxxxxxxx\n\n# or add it to your shell configuration file:\necho "JSONBIN_KEY=$JSONBIN_KEY" >> "$HOME/.$(basename $SHELL)rc"\nsource "$HOME/.$(basename $SHELL)rc"\n```\n\n#### ⌨️ Usage:\n\n```\nusage: cli.py [-h] [-p PRIORITIZE] [-s SKIP_LIST] [-f] [-t TIMEOUT] [-n] [-a] [-c CHANNELS_FILE] [-S] [-C] [-m] [-T THREADS] [-k] [-i IGNORE_VIDEO_IDS]\n\noptions:\n  -h, --help            show this help message and exit\n  -p PRIORITIZE, --prioritize PRIORITIZE\n                        Comma-separated list of channel names to prioritize when processing videos.\n  -s SKIP_LIST, --skip-list SKIP_LIST\n                        Comma-separated list of channel names to skip.\n  -f, --force-refresh   Refresh the database after every video (Can slow down the workflow significantly, but is useful when running multiple concurrent\n                        jobs).\n  -t TIMEOUT, --timeout TIMEOUT\n                        Kill the job after n hours (default: 5.5).\n  -n, --no-logs         Don\'t print any log messages.\n  -a, --add-channel     Add a channel interactively to the list of channels to archive.\n  -c CHANNELS_FILE, --channels-file CHANNELS_FILE\n                        Path to the channels list file to use if the environment variable `CHANNELS` is not set (default: ~/.yt_channels.txt).\n  -S, --show-channels   Show the list of channels in the channels file.\n  -C, --create-collection\n                        Creates/appends to the backend database from the channels list.\n  -m, --multithreading  Enables processing multiple videos concurrently.\n  -T THREADS, --threads THREADS\n                        Number of threads to use when multithreading is enabled. Defaults to the optimal maximum number of workers.\n  -k, --keep-failed-uploads\n                        Keep the files of failed uploads on the local disk.\n  -i IGNORE_VIDEO_IDS, --ignore-video-ids IGNORE_VIDEO_IDS\n                        Comma-separated list or a path to a file containing a list of video ids to ignore.\n```\n\n</details>\n\n---\n\n## 🏗️ Creating A Backend Database\n\n<details>\n  <summary>Creating A Backend Database instructions</summary>\n\n- **Option 1:**  MongoDB (recommended).\n  - Self-hosted (see: [Alyetama/quick-MongoDB](https://github.com/Alyetama/quick-MongoDB) or [dockerhub image](https://hub.docker.com/_/mongo)).\n  - Free cloud database on [Atlas](https://www.mongodb.com/database/free).\n- **Option 2:** JSON bin (if you want a quick start).\n  - Sign up to JSONBin [here](https://jsonbin.io/login).\n  - Click on `VIEW MASTER KEY`, then copy the key.\n  \n</details>\n\n\n## 📝 Notes\n\n- Information about the `MONGODB_CONNECTION_STRING` can be found [here](https://www.mongodb.com/docs/manual/reference/connection-string/).\n- Jobs can run for a maximum of 6 hours, so if you\'re archiving a large channel, the job might die, but it will resume in a new job when it\'s scheduled to run.\n- Instead of raw text, you can pass a file path or a file URL with a list of channels formatted as `CHANNEL_NAME: CHANNEL_URL`. You can also pass raw text or a file of the channels in JSON format `{"CHANNEL_NAME": "CHANNEL_URL"}`.\n',
    'author': 'Mohammad Alyetama',
    'author_email': 'malyetama@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
