# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fiberphotopy',
 'fiberphotopy.plotting',
 'fiberphotopy.preprocess',
 'fiberphotopy.stats']

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
    'name': 'fiberphotopy',
    'version': '0.2.2',
    'description': 'Package for loading and processing fiber photometry data',
    'long_description': "\n# fiberphotopy\n\nCode for analyzing fiber photometry data collected on the Doric Fiber\nPhotometery acquisition system.\n\nImport the package as follows:\n\n``` {.python}\nimport fiberphotopy as fp\n```\n\n## Installation\n\nThe easiest way to install fiberphotopy is with `pip`. First, clone the\nrepository.\n\n``` {.bash}\ngit clone https://github.com/kpuhger/fiberphotopy.git\n```\n\nNext, navigate to the cloned repo and type the following into your\nterminal:\n\n``` {.bash}\npip install .\n```\n\n**Note:** The installation method currently is not likely to work.\nFor the time being it is recommended to add a .pth file to your `site-packages` folder to add the repo to your system's path.\n\n1. Use the terminal to navigate to your `site-packages` folder (e.g., `cd opt/miniconda3/lib/python3.10/site-packages`)\n2. Add `.pth` file pointing to repo path\n\n    ```{.bash}\n    > touch `fiberphotopy.pth` # create pth file\n    > open `fiberphotopy.pth` # add fiberphotopy path to file\n    ```\n\n## Features\n\n### Loading data\n\nWhole session data should be stored in a directory and can be loaded\nlike this:\n\n``` {.python}\nfp.load_session_data(...)\n```\n\n- Args can be used to modify the name of the signal and reference\n    wavelengths as well as to specify the input channel on the\n    photoreceiver and the output channel for the two excitation LEDs.\n- By default, this function calls `trim_ttl_data` which looks for a\n    TTL pulse that indicates the start and end of a behavioral session.\n    This is optional and be turned off by setting `TTL_trim=False`.\n- By default, this function also downsamples the data to 10 Hz. This\n    is controlled by the `downsample=True` argument and the associated\n    `freq` argument.\n- By default, this function uses the standard method of motion\n    correction for photometry data. It fits a linear model to the\n    reference channel (e.g., 405nm) to predict the fluoresence in the\n    signal channel (e.g., 465nm). Next, it calculates a dFF as:\n    `100*(Y-Y_pred)/Y_pred`\n- By default, the 'Animal' column will be populated with the name of\n    the associated data file. This column can be renamed by creating a\n    dict of `{'filename': 'subject_id'}` mappings and passed into\n    `load_session_data` with the `subject_dict` argument.\n\n### Visualizing session data\n\nThe entire session can be visualized by running:\n\n``` {.python}\nfp.plot_fp_session(...)\n```\n\nThis generates a two-panel plot. The top panel plot the raw reference\nand signal fluorescene values on the same plot, and the bottom panel\nplots the dFF calculated from those reference and signal values.\n\n### Trial-level data\n\nThese functions have only been tested on auditory fear conditioning\nexperiments (trace or delay FC). Please check the function documentation\nfor more information.\n\nFor trace fear condtioning (TFC) experiments, you can get trial-level\ndata by calling\n\n``` {.python}\nfp.tfc_trials_df(...)\n```\n\n- This function takes a DataFrame as input (e.g., from\n    `load_session_data`) and creates a trial-level DataFrame with a new\n    column 'Trial' containing the trial number and 'time_trial'\n    containing a standardized time array for extracting identical events\n    across trials.\n- By default, this function provides two methods of trial-normalized\n    data:\n    1. `'dFF_znorm'`: z-score values computed across the entire trial\n        period.\n    2. `'dFF_baseline_norm'`: baseline-normalized values. Computed as\n        (x - mean(baseline))/std(baseline)\n\n### Visualizing trial data\n\nThere are 3 main functions to visualize trial-level data:\n\n``` {.python}\nfp.plot_trial_avg(...)\n```\n\nThis will plot the trial-average for the specified yvar. Data is\naveraged across trials for each subject, and these subject\ntrial-averages are used to calculate the trial-level error for plotting.\n\n``` {.python}\nfp.plot_trial_indiv(...)\n```\n\nThis will generate a figure with `m x n` subplots. The shape of the\nfigure is controlled with the `subplot_params` argument to indicate how\nmany rows and columns to use for the figure.\n\n``` {.python}\nfp.plot_trial_heatmap(...)\n```\n\nThis will generate a heatmap of the data across trials. If the input\nDataFrame contains multiple subjects it will calculate the average\nvalues for each time bin before generating the heatmap.\n",
    'author': 'kpuhger',
    'author_email': 'krpuhger@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kpuhger/fiberphotopy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
