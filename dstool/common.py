import copy
from collections import namedtuple
import os
import sys
import shutil
import yaml

DSROOT = '.dstool'
APPDATA = os.path.join(DSROOT, 'appdata.yaml')
APPDATA_TMP = os.path.join(DSROOT, 'appdata.yaml.tmp')
DATADIR = 'data'

DataItem = namedtuple('DataItem', ('path', 'img_dir', 'ann_dir'))

class AppCtx:
    def __init__(self):
        self.root = search_root()
        self.appdata = self._load_appdata()

    def _list_registered(self):
        return self.appdata['register']

    def register(self, path):
        # assertion
        path = os.path.abspath(path)
        assert os.path.isdir(path)
        # relative path
        relative_path = self._get_dataitem_path(path)
        # check path in possible list
        dataitem_list = self._list_dataitem()
        if relative_path not in [e.path for e in dataitem_list]:
            raise Exception(f'Not DataItem dir: {path}')
        # check already registered
        tmpdata = copy.deepcopy(self.appdata)
        dataitem_list_registered = tmpdata['register']
        if relative_path in [e for e in dataitem_list_registered]:
            print('already registered')
            return
        # register
        tmpdata['register'] += [relative_path]
        print('register')
        self._save_appdata(tmpdata)

    def unregister(self, path):
        # assertion
        path = os.path.abspath(path)
        assert os.path.isdir(path)
        # relative path
        relative_path = self._get_dataitem_path(path)
        # check already registered
        tmpdata = copy.deepcopy(self.appdata)
        dataitem_list_registered = tmpdata['register']
        if not relative_path in [e for e in dataitem_list_registered]:
            print('not registered dir')
            return
        # unregister
        tmpdata['register'].remove(relative_path)
        print('register')
        self._save_appdata(tmpdata)

    def _save_appdata(self, data):
        tmp = os.path.join(self.root, APPDATA_TMP)
        target = os.path.join(self.root, APPDATA)
        with open(tmp, 'w') as tmpfile:
            yaml.dump(data, tmpfile)
        shutil.move(tmp, target)


    def _get_dataitem_path(self, path):
        """get relative path from <dsroot>/data"""
        return os.path.relpath(path, os.path.join(self.root, DATADIR))

    def _load_appdata(self):
        yamlpath = os.path.join(os.path.join(self.root, DSROOT, 'appdata.yaml'))
        try:
            with open(yamlpath) as f:
                obj = yaml.safe_load(f)
        except Exception as e:
            print('Exception occurred while loading YAML...', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)
        self.appdata = obj
        return obj

    def _list_dataitem(self):
        return scan_dataitem(self.root)

DSROOT_APPDATA_INIT = """\
appname: dsroot
version: "0.1"
register: []
"""

def dsroot_init():
    os.makedirs('.dstool')
    with open(APPDATA, 'w') as f:
        f.write(DSROOT_APPDATA_INIT)
    for d in [DATADIR, 'model', 'export', 'backup']:
        os.makedirs(d, exist_ok=True)

def search_root():
    """goto parent dir recusively to find dstool repo root which contains .dstool"""
    cur = os.getcwd()
    while True:
        # if no directory permission, break
        if not os.access(cur, os.R_OK & os.X_OK):
            break
        # if found, return the dir which contains .dstool/
        if os.access(os.path.join(cur, DSROOT), os.F_OK):
            return os.path.abspath(cur)
        # get parent
        newcur = os.path.dirname(cur)
        # reached root if same
        if newcur == cur:
            break
        # update
        cur = newcur
    # error if not found
    raise Exception('not dstool repo')

IMAGE_EXT_ARR = ['.jpg', '.png']

def is_image_path(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in IMAGE_EXT_ARR

IMG_DIR_NAMES = ['image', 'images', 'img', 'imgs']
ANN_DIR_NAMES = ['label', 'labels', 'annotation', 'annotations', 'ann', 'anns']

def scan_dataitem(root):
    dataroot = os.path.join(root, DATADIR)
    return _scan_dataitem(dataroot, dataroot)

def _scan_dataitem(dataroot, path_from):
    """Search datadir in root

    Search dir which contains images and optional VOC labels
    recognize the following folder structure
    - pattern1: X/(image|images) and X/(annotation|annotations|label|labels)
    - pattern2: not pattern1 and last child directory which contains .jpg or .png
    """

    # search child
    childs = []
    for f in os.scandir(dataroot):
        if f.is_dir() and not f.name.startswith('.'):
            childs.append(f.name)

    if len(childs) == 0:
        # 1. Is the last child. if image file exists, it is datadir
        if any([is_image_path(p) for p in os.listdir(dataroot)]):
            itemdir = os.path.relpath(dataroot, path_from)
            return [DataItem(itemdir, '', '')]
    else:
        # 2. check image dir and annotation dir exit
        img_dir = None
        ann_dir = None
        for sub in IMG_DIR_NAMES:
            candidate = os.path.join(dataroot, sub)
            if os.path.isdir(candidate):
                img_dir = sub
                break
        for sub in ANN_DIR_NAMES:
            candidate = os.path.join(dataroot, sub)
            if os.path.isdir(candidate):
                ann_dir = sub
                break
        if img_dir and ann_dir:
            itemdir = os.path.relpath(dataroot, path_from)
            return [DataItem(itemdir, img_dir, ann_dir)]
        # 3. if dataroot is not dateitem, search childs recursively
        dataitem_list = []
        for child in childs:
            dataitem_list += _scan_dataitem(
                    os.path.join(dataroot, child), path_from)
        return dataitem_list

