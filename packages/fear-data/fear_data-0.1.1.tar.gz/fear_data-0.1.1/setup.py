# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fear_data']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pingouin>=0.5.2,<0.6.0',
 'ruamel.yaml>=0.17.21,<0.18.0',
 'scipy>=1.8.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'fear-data',
    'version': '0.1.1',
    'description': 'Python package for data analysis collected from Med-Associates VideoFreeze software.',
    'long_description': "# fear_data\n\nPython package used to analyze files generated from Med-Associates VideoFreeze software.\nAn example notebook is provided in `docs/`.\n\n## Installation\n\nThe easiest way to install fear_data is with `pip`. First, clone the\nrepository.\n\n``` {.bash}\ngit clone https://github.com/kpuhger/fear_data.git\n```\n\nNext, navigate to the cloned repo and type the following into your terminal:\n\n``` {.bash}\npip install .\n```\n\n**Note:** The installation method currently is not likely to work.\nFor the time being it is recommended to add a .pth file to your `site-packages` folder to add the repo to your system's path.\n\n1. Use the terminal to navigate to your `site-packages` folder (e.g., `cd opt/miniconda3/lib/python3.10/site-packages`)\n2. Add `.pth` file pointing to your repo path\n\n    ```{.bash}\n    > touch `fear_data.pth` # create pth file\n    > open `fear_data.pth` # add path to repo in this file\n    ```\n\n## Features\n\n### Experiment configuration files\n\nThe recomended way to set up an experiment is to use a `expt_config.yaml` file ([see here](https://www.redhat.com/en/topics/automation/what-is-yaml) for an overview of YAML).\nThis allows you to use a template notebook to analyze data from different experiments by simply providing the path to the `expt_config.yaml` file. An example configuration file can be found in `docs/expt_config.yaml`.\n\nThe function `fd.create_expt_config(...)` can be used to automatically generate an `expt_config.yaml` file from template.\n\nThe function `fd.update_expt_config(update_dict, ...)` allows you to update an expt_config with information provided in update_dict.\n\n**NOTE:** The keys in update_dict should be identical to expt_config.\n\n### Loading data\n\nTo load Video Freeze data:\n\n1. Define `config_path` variable.\n2. Load data using `fd.load_tfc_data(...)`\n3. Group labels can be added via `fd.add_group_labels(...)`\n\n### Visualizing data\n\n* Plot aesthetics are applied via @style_plot decorator.\n  * Can pass arguments to modify axes info (e.g., labels, labelsize, title, fig_size, ranges (xlim/ylim) -- check docs for more info.\n  * Set `save_fig=True` to apply @savefig decorator and save figure, can set `fig_path` if desired (default set to Desktop).\n* `plot_fc_bins` : pointplot across time for every 'Component'\n  * `session` sets plot aes (label tone bins for train/tone, label shock for train)\n\n* `plot_fc_phase` : use `kind` for two ways to plot data by phase (baseline, tone, trace, iti)\n    1. `kind='point'` : pointplot by phase.\n    2. `kind='bar'` : barplot by phase.\n        * adds swarmplot of subject data by default set `pts=False` to remove.\n\n### Analyzing data\n\nUse the [pingouin python package](https://pingouin-stats.org/) for statistcal analysis.\nAn example analysis can be found in `docs/stats-eample_analysis.ipynb`.\n",
    'author': 'Kyle',
    'author_email': 'krpuhger@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kpuhger/fear_data',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
