# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sc2_datasets',
 'sc2_datasets.lightning',
 'sc2_datasets.lightning.datamodules',
 'sc2_datasets.replay_data',
 'sc2_datasets.replay_parser',
 'sc2_datasets.replay_parser.details',
 'sc2_datasets.replay_parser.game_events',
 'sc2_datasets.replay_parser.game_events.events',
 'sc2_datasets.replay_parser.game_events.events.nested',
 'sc2_datasets.replay_parser.header',
 'sc2_datasets.replay_parser.init_data',
 'sc2_datasets.replay_parser.message_events',
 'sc2_datasets.replay_parser.message_events.events',
 'sc2_datasets.replay_parser.metadata',
 'sc2_datasets.replay_parser.toon_player_desc_map',
 'sc2_datasets.replay_parser.tracker_events',
 'sc2_datasets.replay_parser.tracker_events.events',
 'sc2_datasets.replay_parser.tracker_events.events.player_stats',
 'sc2_datasets.torch',
 'sc2_datasets.torch.datasets',
 'sc2_datasets.transforms',
 'sc2_datasets.transforms.pandas',
 'sc2_datasets.transforms.pytorch',
 'sc2_datasets.utils',
 'sc2_datasets.validators']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.3,<2.0.0',
 'pytorch-lightning>=1.6.5,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'sc2-datasets',
    'version': '1.0.0',
    'description': 'Library providing PyTorch and PyTorch Lightning API for pre-processed StarCraft II dataset SC2EGSetDataset and other datasets.',
    'long_description': '# StarCraft II Datasets\n\nLibrary can be used to interface with datasets that were pre-processed with our pipeline\nas described in:\n- [SC2DatasetPreparator](https://github.com/Kaszanas/SC2DatasetPreparator)\n\nCurrently we have exposed PyTorch and PyTorch Lightning API. Our goal is to provide\ninfrastructure used for StarCraft&nbsp;II analytics.\n\n## Supported Datasets\n\n### SC2EGSet: StarCraft II Esport Game State Dataset\n\nThis project contains official API implementation for the [SC2EGSet: StarCraft II Esport Game State Dataset](https://doi.org/10.5281/zenodo.5503997), which is built based on [SC2ReSet: StarCraft II Esport Replaypack Set](https://doi.org/10.5281/zenodo.5575796).\nContents of this library provide PyTorch and PyTorch Lightning API for pre-processed StarCraft II dataset.\n\n## Installation\n\n1. Manually install PyTorch with minimal version of ```^1.11.0+cu116```.\n2. Perform the following command:\n\n```bash\n$ pip install sc2_datasets\n```\n\n## Usage\n\nBasic example usage can be seen below. For advanced interactions with the datasets\nplease refer to the documentation.\n\nUse [SC2EGSet](https://doi.org/10.5281/zenodo.5503997) with PyTorch:\n```python\nfrom sc2_datasets.torch.sc2_egset_dataset import SC2EGSetDataset\nfrom sc2_datasets.available_replaypacks import EXAMPLE_SYNTHETIC_REPLAYPACKS\n\nif _name_ == "_main_":\n    # Initialize the dataset:\n    sc2_egset_dataset = SC2EGSetDataset(\n        unpack_dir="./unpack_dir_path",           # Specify existing directory path, where the data will be unpacked.\n        download_dir="./download_dir_path",       # Specify existing directory path, where the data will be downloaded.\n        download=True,\n        names_urls=EXAMPLE_SYNTHETIC_REPLAYPACKS, # Use a synthetic replaypack containing 1 replay.\n    )\n\n    # Iterate over instances:\n    for i in range(len(sc2_egset_dataset)):\n        sc2_egset_dataset[i]\n```\n\nUse [SC2EGSet](https://doi.org/10.5281/zenodo.5503997) with PyTorch Lightning:\n```python\nfrom sc2_datasets.lightning.sc2egset_datamodule import SC2EGSetDataModule\nfrom sc2_datasets.available_replaypacks import EXAMPLE_SYNTHETIC_REPLAYPACKS\n\nif _name_ == "_main_":\n    sc2_egset_datamodule = SC2EGSetDataModule(\n                unpack_dir="./unpack_dir_path",            # Specify existing directory path, where the data will be unpacked.\n                download_dir="./download_dir_path",        # Specify existing directory path, where the data will be downloaded.\n                download=False,\n                replaypacks=EXAMPLE_SYNTHETIC_REPLAYPACKS, # Use a synthetic replaypack containing 1 replay.\n            )\n```\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Contributor License Agreement (CLA) and a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`sc2egset_dataset` was created by Andrzej Białecki. It is licensed under the terms of the GNU General Public License v3.0 license.\n\n## Citations\n\n### This Repository\n\nIf you wish to cite the official API for the SC2EGSet: StarCraft II Esport Game State Dataset.\n\n```bibtex\n@software{bialecki_andrzej_2022_6629006,\n  author       = {Białecki, Andrzej and\n                  Białecki, Piotr and\n                  Szczap, Andrzej and\n                  Krupiński, Leszek},\n  title        = {{Kaszanas/SC2EGSet\\_Dataset: 0.9.0 SC2EGSet\\_Dataset \n                   Release}},\n  month        = jun,\n  year         = 2022,\n  publisher    = {Zenodo},\n  version      = {0.9.0},\n  doi          = {10.5281/zenodo.6629005},\n  url          = {https://doi.org/10.5281/zenodo.6629005}\n}\n```\n\n### [Dataset Description Pre-print](https://arxiv.org/abs/2207.03428)\n\nTo cite the article that introduces [SC2ReSet](https://doi.org/10.5281/zenodo.5575796) and [SC2EGSet](https://doi.org/10.5281/zenodo.5503997) use this:\n\n```bibtex\n@misc{https://doi.org/10.48550/arxiv.2207.03428,\n  doi       = {10.48550/ARXIV.2207.03428},\n  url       = {https://arxiv.org/abs/2207.03428},\n  author    = {Białecki, Andrzej and Jakubowska, Natalia and Dobrowolski, Paweł and Białecki, Piotr and Krupiński, Leszek and Szczap, Andrzej and Białecki, Robert and Gajewski, Jan},\n  keywords  = {Machine Learning (cs.LG), Artificial Intelligence (cs.AI), Machine Learning (stat.ML), FOS: Computer and information sciences, FOS: Computer and information sciences},\n  title     = {SC2EGSet: StarCraft II Esport Replay and Game-state Dataset},\n  publisher = {arXiv},\n  year      = {2022},\n  copyright = {Creative Commons Attribution 4.0 International}\n}\n\n```\n\n### [SC2ReSet: StarCraft II Esport Replaypack Set](https://doi.org/10.5281/zenodo.5575796)\n\nTo cite the replay collection that was used to generate the dataset use this:\n\n```bibtex\n@dataset{bialecki_andrzej_2022_5575797,\n  author       = {Białecki, Andrzej},\n  title        = {SC2ReSet: StarCraft II Esport Replaypack Set},\n  month        = jun,\n  year         = 2022,\n  publisher    = {Zenodo},\n  version      = {1.0.0},\n  doi          = {10.5281/zenodo.5575797},\n  url          = {https://doi.org/10.5281/zenodo.5575797}\n}\n```\n\n### [SC2EGSet: StarCraft II Esport Game State Dataset](https://doi.org/10.5281/zenodo.5503997)\n\nTo cite the data itself use this:\n\n```bibtex\n@dataset{bialecki_andrzej_2022_6629349,\n  author       = {Białecki, Andrzej and\n                  Jakubowska, Natalia and\n                  Dobrowolski, Paweł and\n                  Szczap, Andrzej and\n                  Białecki, Robert and\n                  Gajewski, Jan},\n  title        = {SC2EGSet: StarCraft II Esport Game State Dataset},\n  month        = jun,\n  year         = 2022,\n  publisher    = {Zenodo},\n  version      = {1.0.0},\n  doi          = {10.5281/zenodo.6629349},\n  url          = {https://doi.org/10.5281/zenodo.6629349}\n}\n```\n',
    'author': 'Andrzej Białecki',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
