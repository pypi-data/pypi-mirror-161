# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torchok',
 'torchok.callbacks',
 'torchok.constructor',
 'torchok.data',
 'torchok.data.datasets',
 'torchok.data.datasets.classification',
 'torchok.data.datasets.detection',
 'torchok.data.datasets.examples',
 'torchok.data.datasets.representation',
 'torchok.data.datasets.segmentation',
 'torchok.data.transforms',
 'torchok.losses',
 'torchok.losses.common',
 'torchok.losses.representation',
 'torchok.losses.segmentation',
 'torchok.metrics',
 'torchok.models',
 'torchok.models.backbones',
 'torchok.models.heads',
 'torchok.models.heads.classification',
 'torchok.models.heads.detection',
 'torchok.models.heads.representation',
 'torchok.models.heads.segmentation',
 'torchok.models.modules',
 'torchok.models.modules.blocks',
 'torchok.models.modules.bricks',
 'torchok.models.necks',
 'torchok.models.necks.classification',
 'torchok.models.necks.detection',
 'torchok.models.necks.segmentation',
 'torchok.models.poolings',
 'torchok.models.poolings.classification',
 'torchok.models.poolings.representation',
 'torchok.optim',
 'torchok.optim.optimizers',
 'torchok.optim.schedulers',
 'torchok.tasks']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=1.2,<1.3',
 'faiss-cpu==1.7.2',
 'hydra-core>=1.2,<1.3',
 'lxml==4.9.0',
 'mlflow>=1.22,<1.23',
 'numpy>=1.22,<1.23',
 'opencv-python>=4.6,<4.7',
 'pillow>=9.1,<9.2',
 'pytorch-lightning>=1.6,<1.7',
 'ranx>=0.2,<0.3',
 'torch>=1.9,<=1.12',
 'torchmetrics>=0.8,<0.9',
 'torchvision>=0.10,<=0.13']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['pandas>=1.3,<1.4'],
 ':python_version >= "3.8" and python_version < "3.11"': ['pandas>=1.4,<1.5']}

setup_kwargs = {
    'name': 'torchok',
    'version': '0.4.5',
    'description': 'The toolkit for fast Deep Learning experiments in Computer Vision',
    'long_description': '<div align="center">\n\n<img src="https://i.imgur.com/cpwsBrY.png" alt="TorchOk" style="width:300px; horizontal-align:middle"/>\n\n**The toolkit for fast Deep Learning experiments in Computer Vision**\n\n</div>\n\n## A day-to-day Computer Vision Engineer backpack\nTorchOk is based on [PyTorch](https://github.com/pytorch/pytorch) and utilizes [PyTorch Lightning](https://github.com/PyTorchLightning/pytorch-lightning) for training pipeline routines.\n\nThe toolkit consists of:\n- Neural Network models which are proved to be the best not only on [PapersWithCode](https://paperswithcode.com/) but in practice. All models are under plug&play interface that easily connects backbones, necks and heads for reuse across tasks\n- Out-of-the-box support of common Computer Vision tasks: classification, segmentation, image representation and detection coming soon\n- Commonly used datasets, image augmentations and transformations (from [Albumentations](https://albumentations.ai/))\n- Fast implementations of retrieval metrics (with the help of [FAISS](https://github.com/facebookresearch/faiss) and [ranx](https://github.com/AmenRa/ranx)) and lots of other metrics from [torchmetrics](https://torchmetrics.readthedocs.io/)\n- Export models to ONNX and the ability to test the exported model without changing the datasets\n- All components can be customized by inheriting the unified interfaces: Lightning\'s training loop, tasks, models, datasets, augmentations and transformations, metrics, loss functions, optimizers and LR schedulers\n- Training, validation and testing configurations are represented by YAML config files and managed by [Hydra](https://hydra.cc/)\n- Only straightforward training techniques are implemented. No whistles and bells\n\n## Installation\n### pip\nInstallation via pip can be done in two steps:\n1. Install PyTorch that meets your hardware requirements via [official instructions](https://pytorch.org/get-started/locally/)\n2. Install TorchOk by running `pip install --upgrade torchok`\n### Conda\nTo remove the previous installation of TorchOk environment, run:\n```bash\nconda remove --name torchok --all\n```\nTo install TorchOk locally, run:\n```bash\nconda env create -f environment.yml\n```\nThis will create a new conda environment **torchok** with all dependencies.\n### Docker\nAnother way to install TorchOk is through Docker. The built image supports SSH access, Jupyter Lab and Tensorboard ports exposing. If you don\'t need any of this, just omit the corresponding arguments. Build the image and run the container:\n```bash\ndocker build -t torchok --build-arg SSH_PUBLIC_KEY="<public key>" .\ndocker run -d --name <username>_torchok --gpus=all -v <path/to/workdir>:/workdir -p <ssh_port>:22 -p <jupyter_port>:8888 -p <tensorboard_port>:6006 torchok\n```\n\n## Getting started\nThe folder `examples/configs` contains YAML config files with some predefined training and inference configurations.\n### Train\nFor a training example, we can use the default configuration `examples/configs/classification_cifar10.yml`, where the CIFAR-10 dataset and the classification task are specified. The CIFAR-10 dataset will be automatically downloaded into your `~/.cache/torchok/data/cifar10` folder (341 MB).\n\n**To train on all available GPU devices (default config):**\n```bash\npython -m torchok -cp ../examples/configs -cn classification_cifar10\n```\n**To train on all available CPU cores:**\n```bash\npython -m torchok -cp ../examples/configs -cn classification_cifar10 trainer.accelerator=\'cpu\'\n```\nDuring the training you can access the training and validation logs by starting a local TensorBoard:\n```bash\ntensorboard --logdir ~/.cache/torchok/logs/cifar10\n```\n### Export to ONNX\nTODO\n### Run ONNX model\nFor the ONNX model run, we can use the `examples/configs/onnx_infer.yaml`.\nBut first we need to define the field `path_to_onnx`.\n\n**To test ONNX model:**\n```bash\npython test.py -cp examples/configs -cn onnx_infer +entrypoint=test\n```\n\n**To predict ONNX model:**\n```bash\npython test.py -cp examples/configs -cn onnx_infer +entrypoint=predict\n```\n\n## Run tests\n```bash\npython -m unittest discover -s tests/ -p "test_*.py"\n```\n## To be added soon (TODO)\nTasks\n- MOBY (unsupervised training)\n- DetectionTask\n- InstanceSegmentationTask\n\nBackbones\n- Swin-v2\n- HRNet\n- ViT\n- EfficientNet\n- MobileNetV3\n\nSegmentation models\n- HRNet neck + OCR head\n- U-Net neck\n\nDetection models\n- YOLOR neck + head\n- DETR neck + head\n\nDatasets\n- Stanford Online Products\n- Cityscapes\n- COCO\n\nLosses\n- Pytorch Metric Learning losses\n- NT-ext (for unsupervised training)\n\nMetrics\n- Segmentation IoU\n- Segmentation Dice\n- Detection metrics\n',
    'author': 'Vlad Vinogradov',
    'author_email': 'vladvin@eora.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eora-ai/torchok',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
