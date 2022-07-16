"""メインロジック"""

import glob
import datetime
import string
import subprocess

from dstool.common import *
from dstool.config import *
from dstool.export import *
from dstool.util import *
from dstool.voc_export import *

class AppCtx:
    def __init__(self):
        self.root = search_root()
        self.appdata = AppData(self.root)

    def list_registered_paths(self):
        """return list(str)"""
        return [e["path"] for e in self.appdata.list_registered()]

    def list_registered(self):
        """return list(DataItem)"""
        return [DataItem(e["path"], e["img_dir"], e["ann_dir"])
                for e in self.appdata.list_registered()]

    def status(self):
        candidates = self._list_dataitem()
        registered = self.list_registered()

        # mapping path -> item
        registered_map = dict([[e.path, e] for e in registered])
        candidate_map = dict([[e.path, e] for e in candidates])
        # set op
        set_can = set([e.path for e in candidates])
        set_reg = set([e.path for e in registered])

        reg_ok = set_reg & set_can
        reg_err = set_reg - set_can
        can_ok = set_can - set_reg
        # REGISTERED
        print(f"[registered] {len(reg_ok)} folder")
        for s in sorted(list(reg_ok)):
            marks = self.appdata.list_mark(s)
            marks_str = ''.join([f'({mark})' for mark in marks])
            info = inspect_dataitem(self.root, registered_map[s])
            num_with_ann = len(info["annotated"])
            num_without_ann = len(info["not_annotated"])
            num_total = num_with_ann + num_without_ann
            print(f'    {s:20s}    {num_with_ann:4d} ann / {num_total:4d} img    {marks_str}')
        # CANDIDATE
        print('')
        print(f"[non-registered] {len(can_ok)} folder")
        for s in sorted(list(can_ok)):
            info = inspect_dataitem(self.root, candidate_map[s])
            num_with_ann = len(info["annotated"])
            num_without_ann = len(info["not_annotated"])
            num_total = num_with_ann + num_without_ann
            print(f'    {s:20s}    {num_with_ann:4d} ann / {num_total:4d} img')
        # ERR
        if len(reg_err) > 0:
            print('')
            print("[WARN] following registered item seems to be not dataitem dir")
            print("[WARN] the data was removed?")
            for s in sorted(list(reg_err)):
                print(f'    {s:20s}')

        #print("candidates", candidates)
        #print("registered", registered)
        #print("appdata", app._load_appdata())

    def register(self, path):
        # assertion
        path = os.path.abspath(path)
        assert os.path.isdir(path)
        # relative path
        relative_path = self._get_dataitem_path(path)
        # check already registered
        if relative_path in self.list_registered_paths():
            print('already registered')
            return
        # check path in possible list
        is_dataitem, img_dir, ann_dir, _ = is_dataitem_dir(path)
        if not is_dataitem:
            error_exit('it is not dataitem dir')
        # register
        print('register')
        self.appdata.add_dataitem(relative_path, img_dir, ann_dir)

    def unregister(self, path):
        # assertion
        path = os.path.abspath(path)
        assert os.path.isdir(path)
        # relative path
        relative_path = self._get_dataitem_path(path)
        # check already registered
        tmpdata = copy.deepcopy(self.appdata)
        dataitem_list_registered = self.list_registered_paths()
        if not relative_path in [e for e in dataitem_list_registered]:
            print('not registered dir')
            return
        # unregister
        print('register')
        self.appdata.delete_dataitem(relative_path)

    def mark(self, path, mark):
        path = os.path.abspath(path)
        relative_path = self._get_dataitem_path(path)
        self.appdata.mark(relative_path, mark)

    def unmark(self, path, mark):
        path = os.path.abspath(path)
        relative_path = self._get_dataitem_path(path)
        self.appdata.unmark(relative_path, mark)

    def annotate(self, path):
        """Start annotation"""
        path = os.path.abspath(path)
        is_dataitem, img_dir, ann_dir, _ = is_dataitem_dir(path)
        if not is_dataitem:
            error_exit(f'not dataitem dir')
        # launch
        img_dir_full = os.path.join(path, img_dir)
        ann_dir_full = os.path.join(path, ann_dir)
        cls_file = os.path.join(self.root, DATADIR, 'classes.txt')
        if not os.path.exists(cls_file):
            error_exit(f'please define class file file in {cls_file}')
        cmd = ['labelImg', img_dir_full, cls_file, ann_dir_full]

        # print commnad insteamd of launching process
        # to avoid qt error (temporary workaround)
        print('run below command to start training')
        print(' '.join(cmd))
        #subprocess.Popen(cmd)

    def load_classes(self):
        l = open(os.path.join(self.root, DATADIR, 'classes.txt')).read()
        return [e for e in l.splitlines() if e != '']

    def _gen_export_name(self):
        yyyymmdd = datetime.date.today().strftime("%Y%m%d")
        for alpha in string.ascii_uppercase:
            export_name = yyyymmdd + '-' + alpha
            search_path = os.path.join(self.root, EXPORTDIR, export_name + '*')
            # if export/yyyymmdd-<alphabet>* does not exist, use yyyymmdd-<alphabet>
            if len(glob.glob(search_path)) == 0:
                return export_name
        error_exit(f'path exists in model dir: {export_name}')

    def export(self, separate_testset=False, export_name_suffix=''):
        """Export registered data as COCO dataset
        
        Split into train/valld/test. test is dataitems marked as testset

        :param separate_testset: if True, split into train/valid/test using "testset" mark. if False, split into train/valid using all data
        :param export_name_suffix: name suffix
        """
        # cat_names
        cat_names = self.load_classes()
        print('cat names: ', cat_names)

        # export-dir
        export_name = self._gen_export_name() + export_name_suffix
        export_dir = os.path.join(self.root, 'export', export_name, 'annotations')
        os.makedirs(export_dir)

        dataitems = self.appdata.list_registered()
        if separate_testset:
            print('split into train/valid using all data. testset mark will be ignored.')
            dataitems_trainval = [e for e in dataitems if not 'testset' in e["mark"]]
            dataitems_test = [e for e in dataitems if 'testset' in e["mark"]]
            if len(dataitems_test) == 0:
                error_exit('--separate_testset specified but no data is markded as testset')
            print(f'trainval folders {len(dataitems_trainval)}')
            print(f'test folders {len(dataitems_test)}')
            # export trainval / test
            export_coco_train_valid(self.root, dataitems_trainval, cat_names, export_dir)
            export_coco_test(self.root, dataitems_test, cat_names, export_dir)
        else:
            print('split into train/valid/test using "testset" mark.')
            export_coco_train_valid(self.root, dataitems, cat_names, export_dir)

        # link to data dir
        os.symlink('../../data', os.path.join(self.root, 'export', export_name, 'data'))

        print(f'annotation set is exported to {EXPORTDIR}/{export_name}')
        return export_name

    def _gen_train_name(self):
        yyyymmdd = datetime.date.today().strftime("%Y%m%d")
        for alpha in string.ascii_uppercase:
            train_name = yyyymmdd + '-' + alpha
            if not os.path.exists(os.path.join(self.root, MODELDIR, train_name)):
                return train_name
        error_exit(f'path exists in model dir: {train_name}')

    def train(self, exported_datadir=None):
        """Train
        
        :param exported_datadir: exported dir which includes data/ and annotations/*.json
        """
        # export automatically if export_dir not specified
        if not exported_datadir:
            export_name = self.export(export_name_suffix='-autogen')
            exported_datadir = os.path.join(self.root, EXPORTDIR, export_name)

        yolox_s_weight_path = os.path.join(self.root, MODELDIR, 'yolox_s.pth')
        if not os.path.exists(yolox_s_weight_path):
            print('download yolox-s weight')
            import requests
            URL = "https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth"
            response = requests.get(URL)
            with open(yolox_s_weight_path, "wb") as f:
                f.write(response.content)

        exported_datadir = os.path.abspath(exported_datadir)
        relative_dir = os.path.relpath(exported_datadir, self.root)
        print(relative_dir)
        import dstool.model.yolox as myolox

        classes = self.load_classes()

        train_name = self._gen_train_name()
        train_dir = os.path.join(self.root, 'model', train_name)
        assert not os.path.exists(train_dir), f"dir should not exists {train_dir}"
        os.makedirs(train_dir)

        print(f'Train dir is {train_dir}')

        m = myolox.Model(classes)
        m.train(relative_dir, train_dir)

    def infer(self, model_dir, img_path):
        """Test inference using model in model_dir"""
        import dstool.model.yolox as myolox
        classes = self.load_classes()
        m = myolox.Model(classes)
        dets = m.infer(model_dir, img_path)
        show_inference(img_path, dets, classes)

    def auto_annotate(self, path, model_dir):
        """Auto annotate not annotated imgs in path using model in train_dir"""
        # model
        import dstool.model.yolox as myolox
        classes = self.load_classes()
        m = myolox.Model(classes)
        # check datadir
        is_dataitem, img_dir, ann_dir, _ = is_dataitem_dir(path)
        if not is_dataitem:
            error_exit('it is not dataitem dir')
        img_dir_full = os.path.join(path, img_dir)
        ann_dir_full = os.path.join(path, ann_dir)
        # mark as auto-annotate
        self.mark(path, "auto-annotated")
        # start annotation
        for f in os.scandir(img_dir_full):
            if f.is_dir(): continue
            if not is_image_path(f.name): continue
            ann_name = os.path.splitext(f.name)[0] + '.xml'
            ann_path = os.path.join(ann_dir_full, ann_name)
            if os.path.exists(ann_path):
                print(f'skip alrady annotated {ann_name}')
                continue
            dets = m.infer(model_dir, f.path)
            voc_export(f.path, ann_path, classes, dets)
        print('auto-annotate finished')

    def _normalize_datapath(self, path):
        """Given path and return normalized path and relative path from ./data"""
        path = os.path.abspath(path)
        relative_path = self._get_dataitem_path(path)
        return path, relative_path

    def _get_dataitem_path(self, path):
        """get relative path from <dsroot>/data"""
        return os.path.relpath(path, os.path.join(self.root, DATADIR))

    def _list_dataitem(self):
        return scan_dataitem(self.root)

DSROOT_REGISTER_INIT = """\
[]
"""

def dsroot_init():
    os.makedirs('.dstool')
    with open(APPDATA, 'w') as f:
        f.write(DSROOT_REGISTER_INIT)
    for d in [DATADIR, 'model', 'export', 'backup']:
        os.makedirs(d, exist_ok=True)

def search_root():
    """goto parent dir recusively to find dstool repo root which contains .dstool"""
    cur = os.getcwd()
    while True:
        # if no directory permission, break
        if not os.access(cur, os.R_OK | os.X_OK):
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
    error_exit('not dstool repo')

IMAGE_EXT_ARR = ['.jpg', '.png']

def is_image_path(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in IMAGE_EXT_ARR

def is_ann_path(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in ['.xml']

IMG_DIR_NAMES = ['image', 'images', 'img', 'imgs']
ANN_DIR_NAMES = ['label', 'labels', 'annotation', 'annotations', 'ann', 'anns']

def is_dataitem_dir(dataroot):
    """Check if the DataItem dir which includes img_dir and ann_dir
    
    Return is_datadir, img_dir, ann_dir, child_dirs(excluding dir starts with '.')
    If dataitem contains images & labels, imd_dir is '' and ann_dir is ''
    """
    # search child
    childs = []
    for f in os.scandir(dataroot):
        if f.is_dir() and not f.name.startswith('.'):
            childs.append(f.name)

    if len(childs) == 0:
        # 1. Is the last child. if image file exists, it is datadir
        if any([is_image_path(p) for p in os.listdir(dataroot)]):
            return True, '', '', childs
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
            return True, img_dir, ann_dir, childs

    return False, None, None, childs

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
    is_dataitem, img_dir, ann_dir, childs = is_dataitem_dir(dataroot)

    if is_dataitem:
        itemdir = os.path.relpath(dataroot, path_from)
        return [DataItem(itemdir, img_dir, ann_dir)]
    else:
        # if dataroot is not dateitem, search childs recursively
        dataitem_list = []
        for child in childs:
            dataitem_list += _scan_dataitem(
                    os.path.join(dataroot, child), path_from)
        return dataitem_list

def inspect_dataitem(root, d : DataItem):
    img_dir_full = os.path.join(root, DATADIR, d.path, d.img_dir)
    imgs = [e.name for e in os.scandir(img_dir_full) if is_image_path(e)]
    ann_dir_full = os.path.join(root, DATADIR, d.path, d.ann_dir)
    anns = set([e.name for e in os.scandir(ann_dir_full) if is_ann_path(e)])

    noext_withext_map = dict([e[:-4], e] for e in imgs)
    imgs_set = set([e[:-4] for e in imgs])
    anns_set = set([e[:-4] for e in anns])
    annotated_set = imgs_set & anns_set
    not_annotated_set = imgs_set - anns_set

    return {
        "annotated": sorted([noext_withext_map[e] for e in annotated_set]),
        "not_annotated": sorted([noext_withext_map[e] for e in not_annotated_set]),
    }