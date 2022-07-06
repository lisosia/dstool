""".dstool/ 下のファイルを管理する"""
import os
import yaml
import shutil

from dstool.common import *

class AppConfig():
    def __init__(self, root):
        self.root = root
        self.regs = self._load()

    def list_registered(self):
        return self.regs

    def add_dataitem(self, path, img_dir, ann_dir):
        assert type(self.regs) is list
        toadd = {'path': path,
                 'img_dir': img_dir,
                 'ann_dir': ann_dir,
                 'mark': []}
        self.regs += [toadd]
        self._save()

    def delete_dataitem(self, path : str):
        """delete item using relative_path from data/"""
        before = self.regs 
        indexes = [i for i, e in enumerate(before) if e["path"] == path]
        if len(indexes) > 1:
            raise Exception('Internal error')
        if len(indexes) == 0:
            raise Exception(f'Not found: {path}')
        before.pop(indexes[0])
        self._save()

    def _load(self):
        yamlpath = os.path.join(os.path.join(self.root, DSROOT, 'appdata.yaml'))
        try:
            with open(yamlpath) as f:
                obj = yaml.safe_load(f)
        except Exception as e:
            error_exit('Exception occurred while loading YAML: ' + e)
        return obj

    def _save(self):
        tmp = os.path.join(self.root, APPDATA_TMP)
        target = os.path.join(self.root, APPDATA)
        with open(tmp, 'w') as tmpfile:
            yaml.dump(self.regs, tmpfile)
        shutil.move(tmp, target)
