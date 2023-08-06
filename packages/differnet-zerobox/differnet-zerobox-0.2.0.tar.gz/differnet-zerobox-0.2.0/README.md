# Summary
This module is used for training a model from captured images for classification(good or bad). 

The goal is to allow other projects to reuse this code and be able to train a model, validate a model(test_model) and predict(good or bad).

# Usage
For updating this project itself please read [developer_guide](./developer_guide.md)

## Install
```py
# from pypi
pip install differnet-zerobox

# from github
pip install -e git+https://github.com/zerobox-ai/pydiffernet#egg=differnet-zerobox

```

## Create your configuration and create DiffernetUtil

```py
conf = settings.DIFFERNET_CONF
logger.info(f"working folder: {conf.get('differnet_work_dir')}")

differnetutil = DiffernetUtil(conf, "pink1")
```

configuration like this. Any value not set will be read from default

```py
#common settings.
DIFFERNET_CONF = {
    "differnet_work_dir": "./work",
    "device": "cuda",  # cuda or cpu
    "device_id": 5,
    "verbose": True,
    # "rotation_degree": 0,
    # "crop_top": 0.10,
    # "crop_left": 0.10,
    # "crop_bottom": 0.10,
    # "crop_right": 0.10,
    # training setting
    "meta_epochs": 5,
    "sub_epochs": 8,
    # # output settings
    "grad_map_viz": False,
    # "save_model": True,
    "save_transformed_image": False,
    # "visualization": False,
    # "target_tpr": 0.76,
    "test_anormaly_target": 10,
}
```
## Prepare the training and testing data
The data structure under work folder looks like this. The model folder will save trained model.
For experiment purpose, you would like to give test and validate folder with proper labled data. While, for zerobox 
it only requires train folder and data. The minimum images is 16 based on the differnet paper.

```
pink1/
├── model
├── test
│   ├── defect
│   └── good
├─── validate
│    ├── defect
│    └── good
└── train
    └── good
        ├── 01.jpg
        ├── 02.jpg
        ├── 03.jpg
        ├── 04.jpg
        ├── 05.jpg
        ├── 06.jpg
        ├── 07.jpg
        ├── 08.jpg
        ├── 09.jpg
        ├── 10.jpg
        ├── 11.jpg
        ├── 12.jpg
        ├── 13.jpg
        ├── 14.jpg
        ├── 15.jpg
        └── 16.jpg
```

## Call the the fuctions

```py
import time
import logging.config
import cv2
import os
from differnet.differnet_util import DiffernetUtil
import time
import conf as settings

# import logging
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)
#...

# load cutomized conf
conf = settings.DIFFERNET_CONF
differnetutil = DiffernetUtil(conf, "black1")
differnetutil.train_model()

# validate model
differnetutil = DiffernetUtil(conf, "black1")
t1 = time.process_time()
differnetutil.test_model()
t2 = time.process_time()
elapsed_time = t2 - t1
logger.info(f"elapsed time: {elapsed_time}")

# predict
t0 = time.process_time()
differnetutil = DiffernetUtil(conf, "black1")
# a. load model
differnetutil.load_model()
t1 = time.process_time()

elapsed_time = t1 - t0
logger.info(f"Model load elapsed time: {elapsed_time}")
img = cv2.imread(
    os.path.join(
        differnetutil.test_dir, "defect", "Camera0_202009142018586_product.png"
    ),
    cv2.IMREAD_UNCHANGED,
)
t1 = time.process_time()
# b. detect
ret = differnetutil.detect(img, 10)
t2 = time.process_time()
elapsed_time = t2 - t1
logger.info(f"Detection elapsed time: {elapsed_time}")
self.assertTrue(ret)

img = cv2.imread(
    os.path.join(
        differnetutil.test_dir, "good", "Camera0_202009142018133_product.png"
    ),
    cv2.IMREAD_UNCHANGED,
)
t2 = time.process_time()
ret = differnetutil.detect(img, 10)
t3 = time.process_time()
elapsed_time = t3 - t2
logger.info(f"Detection elapsed time: {elapsed_time}")
self.assertFalse(ret)


```

# Developer's Tips
## Dependencies
Python 3.9 + torch 1.8.1 + torchvision 0.9.1 are required. In order to make proper use of cuda or cpu you may need install torch and torch vision based on instructions from [pytroch.org](https://pytorch.org/get-started/locally/)

Notice: Older version of torch does not work with python 3.9

Other dependencies will be installed by pip command
```
scikit-learn>=0.22
scipy>=1.3.2
numpy>=1.17.4
torch==1.8.1
torchvision==0.9.1
matplotlib>=3.0.3
tqdm>=4.59.2
opencv-python>=4.5.1
```
