"""共通コード"""

import copy
from collections import namedtuple
import os
import sys
import shutil
import yaml
from enum import Enum

DSROOT = '.dstool'
APPDATA = os.path.join(DSROOT, 'appdata.yaml')
APPDATA_TMP = os.path.join(DSROOT, 'appdata.yaml.tmp')
DATADIR = 'data'
MODELDIR = 'model'
EXPORTDIR = 'export'
POSSIBLE_MARKS = ['auto-annotated', 'testset']

DataItem = namedtuple('DataItem', ('path', 'img_dir', 'ann_dir'))

def error_exit(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

#TODO: use it 
class DataItemState(Enum):
    ANNOTATED = 1
    PARTIALLY_ANNOTATED = 2
    NOT_ANNOTATED = 3

