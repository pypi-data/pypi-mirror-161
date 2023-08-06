# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['volume_segmantics',
 'volume_segmantics.data',
 'volume_segmantics.model',
 'volume_segmantics.model.operations',
 'volume_segmantics.scripts',
 'volume_segmantics.utilities']

package_data = \
{'': ['*']}

install_requires = \
['albumentations<=1.1.0',
 'h5py>=3.0.0,<4.0.0',
 'imagecodecs',
 'matplotlib>=3.3.0,<4.0.0',
 'numpy>=1.18.0,<2.0.0',
 'segmentation-models-pytorch>=0.2.1,<0.3.0',
 'termplotlib>=0.3.6,<0.4.0',
 'torch>=1.7.1']

entry_points = \
{'console_scripts': ['model-predict-2d = '
                     'volume_segmantics.scripts.predict_2d_model:main',
                     'model-train-2d = '
                     'volume_segmantics.scripts.train_2d_model:main']}

setup_kwargs = {
    'name': 'volume-segmantics',
    'version': '0.2.6',
    'description': 'A toolkit for semantic segmentation of volumetric data using pyTorch deep learning models',
    'long_description': '# Volume Segmantics\n\nA toolkit for semantic segmentation of volumetric data using PyTorch deep learning models.\n\n![example workflow](https://github.com/DiamondLightSource/volume-segmantics/actions/workflows/tests.yml/badge.svg) ![example workflow](https://github.com/DiamondLightSource/volume-segmantics/actions/workflows/release.yml/badge.svg)\n\nGiven a 3d image volume and corresponding dense labels (the segmentation), a 2d model is trained on image slices taken along the x, y, and z axes. The method is optimised for small training datasets, e.g a single dataset in between $128^3$ and $512^3$ pixels. To achieve this, all models use pre-trained encoders and image augmentations are used to expand the size of the training dataset.\n\nThis work utilises the abilities afforded by the excellent [segmentation-models-pytorch](https://github.com/qubvel/segmentation_models.pytorch) library in combination with augmentations made available via [Albumentations](https://albumentations.ai/). Also the metrics and loss functions used make use of the hard work done by Adrian Wolny in his [pytorch-3dunet](https://github.com/wolny/pytorch-3dunet) repository. \n\n## Requirements\n\nA machine capable of running CUDA enabled PyTorch version 1.7.1 or greater is required. This generally means a reasonably modern NVIDIA GPU. The exact requirements differ according to operating system. For example on Windows you will need Visual Studio Build Tools as well as CUDA Toolkit installed see [the CUDA docs](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html) for more details. \n\n## Installation\n\nThe easiest way to install the package is to first create a new conda environment or virtualenv with python (ideally >= version 3.8) and also pip, then activate the environment and `pip install volume-segmantics`. If a CUDA-enabled build of PyTorch is not being installed by pip, you can try `pip install volume-segmantics --extra-index-url https://download.pytorch.org/whl` this particularity seems to be an issue on Windows. \n\n## Configuration and command line use\n\nAfter installation, two new commands will be available from your terminal whilst your environment is activated, `model-train-2d` and `model-predict-2d`.\n\nThese commands require access to some settings stored in YAML files. These need to be located in a directory named `volseg-settings` within the directory where you are running the commands. The settings files can be copied from [here](https://github.com/DiamondLightSource/volume-segmantics/releases/download/v0.2.5/volseg-settings.zip). \n\nThe file `2d_model_train_settings.yaml` can be edited in order to change training parameters such as number of epochs, loss functions, evaluation metrics and also model and encoder architectures. The file `2d_model_predict_settings.yaml` can be edited to change parameters such as the prediction "quality" e.g "low" quality refers to prediction of the volume segmentation by taking images along a single axis (images in the (x,y) plane). For "medium" and "high" quality, predictions are done along 3 axes and in 12 directions (3 axes, 4 rotations) respectively, before being combined by maximum probability. \n\n### For training a 2d model on a 3d image volume and corresponding labels\nRun the following command. Input files can be in HDF5 or multi-page TIFF format.\n\n```shell\nmodel-train-2d --data path/to/image/data.h5 --labels path/to/corresponding/segmentation/labels.h5\n```\n\nPaths to multiple data and label volumes can be added after the `--data` and `--labels` flags respectively. A model will be trained according to the settings defined in `/volseg-settings/2d_model_train_settings.yaml` and saved to your working directory. In addition, a figure showing "ground truth" segmentation vs model segmentation for some images in the validation set will be saved. \n\n### For 3d volume segmentation prediction using a 2d model\nRun the following command. Input image files can be in HDF5 or multi-page TIFF format.\n\n```shell\nmodel-predict-2d path/to/model_file.pytorch path/to/data_for_prediction.h5\n```\n\nThe input data will be segmented using the input model following the settings specified in `volseg-settings/2d_model_predict_settings.yaml`. An HDF5 file containing the segmented volume will be saved to your working directory.\n\n### Tutorial using example data\n\nA tutorial is available [here](training_data/README.md) that provides a walk-through of how to segment blood vessels from synchrotron X-ray micro-CT data collected on a sample of human placental tissue.\n\n## Currently supported model architectures and encoders\n\nThe model architectures which are currently available and tested are: \n- U-Net\n- U-Net++\n- FPN\n- DeepLabV3\n- DeepLabV3+\n- MA-Net\n- LinkNet.\n\nThe pre-trained encoders that can be used with these architectures are: \n- ResNet-34\n- ResNet50\n- ResNeXt-50_32x4d.\n\n## Using the API\n\nYou can use the functionality of the package in your own program via the API, this is [documented here](https://diamondlightsource.github.io/volume-segmantics/). This interface is the one used by [SuRVoS2](https://github.com/DiamondLightSource/SuRVoS2), a client/server GUI application that allows fast annotation and segmentation of volumetric data. \n\n## Contributing\n\nWe welcome contributions from the community. Please take a look at out [contribution guidelines](https://github.com/DiamondLightSource/volume-segmantics/blob/main/CONTRIBUTING.md) for more information.\n\n## References\n\n**Albumentations**\n\nBuslaev, A., Iglovikov, V.I., Khvedchenya, E., Parinov, A., Druzhinin, M., and Kalinin, A.A. (2020). Albumentations: Fast and Flexible Image Augmentations. Information 11. [https://doi.org/10.3390/info11020125](https://doi.org/10.3390/info11020125)\n\n**Segmentation Models PyTorch**\n\nYakubovskiy, P. (2020). Segmentation Models Pytorch. [GitHub](https://github.com/qubvel/segmentation_models.pytorch)\n\n**PyTorch-3dUnet**\n\nWolny, A., Cerrone, L., Vijayan, A., Tofanelli, R., Barro, A.V., Louveaux, M., Wenzl, C., Strauss, S., Wilson-Sánchez, D., Lymbouridou, R., et al. (2020). Accurate and versatile 3D segmentation of plant tissues at cellular resolution. ELife 9, e57613. [https://doi.org/10.7554/eLife.57613](https://doi.org/10.7554/eLife.57613)\n',
    'author': 'Oliver King',
    'author_email': 'olly.king@diamond.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DiamondLightSource/volume-segmantics',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
