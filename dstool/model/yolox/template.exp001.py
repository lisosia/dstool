"""Yolox exp001.py python tempalte file"""

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os

from dstool.model.yolox.yolox_base import Exp as MyExp


class Exp(MyExp):
    def __init__(self):
        super(Exp, self).__init__()
        self.depth = 0.33
        self.width = 0.50
        self.exp_name = os.path.split(os.path.realpath(__file__))[1].split(".")[0]

        # Define yourself dataset path
        self.data_dir = "../../$data_dir/"  # yolox loads: datadir / <name> / <filename in ann>
        self.train_ann = "train.json"  # yolox loads: datadir / "annotations" / + self.train_ann
        self.val_ann = "valid.json"

        self.num_classes = $num_class

        self.max_epoch = 10
        self.data_num_workers = 4
        self.eval_interval = 1
