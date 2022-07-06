import os
import yaml
import shutil


DSROOT = '.dstool'
APPDATA = os.path.join(DSROOT, 'appdata.yaml')
APPDATA_TMP = os.path.join(DSROOT, 'appdata.yaml.tmp')

class AppConfig():
    def __init__(self, root):
        self.root = root
        self.d = self._load()

    def list_registered(self):
        return self.d["register"]

    def add_dataitem(self, path):
        assert type(self.d["register"]) is list
        toadd = {'path': path,
                 'mark': []}
        self.d["register"] += [toadd]
        self._save()

    def delete_dataitem(self, path : str):
        """delete item using relative_path from data/"""
        before = self.d["register"] 
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
            print('Exception occurred while loading YAML...', file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)
        return obj

    def _save(self):
        tmp = os.path.join(self.root, APPDATA_TMP)
        target = os.path.join(self.root, APPDATA)
        with open(tmp, 'w') as tmpfile:
            yaml.dump(self.d, tmpfile)
        shutil.move(tmp, target)
