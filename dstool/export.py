"""COCOフォーマットでエクスポート"""

import random

import pylabel
from pylabel import importer
import pandas as pd

from dstool.common import *

def _import_as_importer(root, dataitems, cat_names):
    """Import as pylabel.importer"""
    datadir = os.path.join(root, DATADIR)

    df_array = []
    for d in dataitems:
        imgdir = os.path.join(datadir, d["path"], d["img_dir"])
        anndir = os.path.join(datadir, d["path"], d["ann_dir"])
        dataset = pylabel.importer.ImportVOC(path=anndir, path_to_images=imgdir, name="tmp_dataset")

        df = dataset.df.copy(deep=True)
        # mod img_folder, img_filename (folder, file_name in coco)
        df.img_folder = '.'
        # final "" is added so that prefix ends with "/"
        prefix = os.path.join(d["path"], d["img_dir"], "")
        df.img_filename = prefix + df.img_filename
        df_array.append(df)

    ### 本来は ImportVOCは一度だけ呼ぶべきだが、concatしているので
    ### dfの必要な部分を修正する
    # re index to avoid id duplication    
    df_all = pd.concat(df_array).sort_values('img_filename').reset_index()
    # overwrite id since each ImportVOC has diffirent order class list
    df_all["cat_id"] = df_all["cat_name"].map(lambda e : cat_names.index(e))
    # id
    df_all["id"] = df_all.index
    # img_id
    #df_all["img_id"] = df_all.groupby('img_filename').ngroup()  # assign group index
    df_all["img_id"] = df_all.groupby('img_filename')['id'].transform('max')  # assign max(row id)

    #print( df_all.head(15) )
    #print( df_all.tail(15) )
    dataset.df = df_all
    return dataset

def export_coco_test(root, dataitems, cat_names, outdir):
    dataset = _import_as_importer(root, dataitems, cat_names)

    #update dataset
    dataset.export.ExportToCoco(os.path.join(outdir, "test.json"))

def export_coco_train_valid(root, dataitems, cat_names, outdir):
    # import data
    dataset = _import_as_importer(root, dataitems, cat_names)
    df = dataset.df
    dfg = df.groupby("img_filename")
    # split by img_filename (e.g. A/B/C.jpg)
    files = sorted([e for e in dfg.groups])
    random.seed(0)
    random.shuffle(files)
    RATIO = 0.8
    NUM_TRAIN = int(len(files) * RATIO)
    trains = sorted(files[:NUM_TRAIN])
    valids = sorted(files[NUM_TRAIN:])
    # split df
    df_train = pd.concat([dfg.get_group(img_filename) for img_filename in trains])
    df_train = df_train.reset_index()
    df_valid = pd.concat([dfg.get_group(img_filename) for img_filename in valids])
    df_valid = df_valid.reset_index()
    print("-----train dataframe\n", df_train.head())
    print("\n-----valid dataframe\n", df_valid.head())
    # export
    dataset.df = df_train
    dataset.export.ExportToCoco(os.path.join(outdir, "train.json"))
    dataset.df = df_valid
    dataset.export.ExportToCoco(os.path.join(outdir, "valid.json"))
