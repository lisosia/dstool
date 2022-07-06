"""メインロジック"""

from dstool.common import *
from dstool.config import *

class AppCtx:
    def __init__(self):
        self.root = search_root()
        self.appdata = AppData(self.root)

    def list_registered_paths(self):
        return [e["path"] for e in self.appdata.list_registered()]

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
        if not is_dataitem_dir:
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
    raise Exception('not dstool repo')

IMAGE_EXT_ARR = ['.jpg', '.png']

def is_image_path(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in IMAGE_EXT_ARR

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

