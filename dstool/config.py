""".dstool/ 下のファイルを管理する"""

import os
import yaml
import shutil

from dstool.common import *

class AppData():
    def __init__(self, root):
        self.root = root
        self.regs = self._load()

    def list_registered(self):
        return self.regs
    
    def list_mark(self, path):
        reg = self.find_reg(path)
        assert reg
        return reg["mark"]

    def add_dataitem(self, path, img_dir, ann_dir):
        assert os.path.isdir(os.path.join(self.root, DATADIR, path))
        assert type(self.regs) is list
        toadd = {'path': path,
                 'img_dir': img_dir,
                 'ann_dir': ann_dir,
                 'mark': []}
        self.regs += [toadd]
        self._save()
    
    def find_reg(self, path):
        """Find dataitem by path"""
        founds = [reg for reg in self.regs if reg["path"] == path]
        if len(founds) == 0:
            return None
        elif len(founds) > 1:
            error_exit("internal error. multiple same name dataitem found")
        else:
            return founds[0]

    def delete_dataitem(self, path : str):
        """Delete item using relative_path from data/"""
        reg = self.find_reg(path)
        if not reg:
            error_exit(f'Not found: {path}')
        self.regs.remove(reg)
        self._save()

    def mark(self, path, mark_name):
        """Mark dataitem with strnig. If already marked do nothing"""
        reg = self.find_reg(path)
        if not reg:
            error_exit(f'Not found: {path}')
        if not mark_name in POSSIBLE_MARKS:
            error_exit(f'unknown mark name. possbile mark names are {POSSIBLE_MARKS}')
        if mark_name in reg["mark"]:
            print(f'already marked as {mark_name}')
            return
        reg["mark"] += [mark_name]
        self._save()

    def unmark(path, mark_name):
        """Mark dataitem with strnig. If not marked return False, else return True"""
        reg = self.find_reg(path)
        if not reg:
            error_exit(f'Not found: {path}')
        if not mark_name in POSSIBLE_MARKS:
            error_exit(f'unknown mark name. possbile mark names are {POSSIBLE_MARKS}')
        if not mark_name in reg["mark"]:
            print(f'{path} not marked as {mark_name}')
            return
        reg["mark"].remove(mark_name)
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
