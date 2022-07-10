"""COCOフォーマットでエクスポート"""

import pylabel
from pylabel import importer
import pandas as pd

from dstool.common import *

def export_coco(root, dataitems, cat_names, outpath):
    datadir = os.path.join(root, DATADIR)

    df_array = []
    for d in dataitems:
        imgdir = os.path.join(datadir, d["path"], d["img_dir"])
        anndir = os.path.join(datadir, d["path"], d["ann_dir"])
        dataset = pylabel.importer.ImportVOC(path=anndir, path_to_images=imgdir, name="tmp_dataset")

        df = dataset.df.copy(deep=True)
        # mod img_folder, img_filename (folder, file_name in coco)
        df.img_folder = '.'
        prefix = os.path.join(d["path"], d["img_dir"])
        df.img_filename = prefix + df.img_filename
        df_array.append(df)

    ### 本来は ImportVOCは一度だけ呼ぶべきだが、concatしているので
    ### dfの必要な部分を修正する
    # re index to avoid id duplication    
    df_all = pd.concat(df_array).reset_index()
    # overwrite id since each ImportVOC has diffirent order class list
    df_all["cat_id"] = df_all["cat_name"].map(lambda e : cat_names.index(e))
    # id
    df_all["id"] = df_all.index
    # img_id
    #df_all["img_id"] = df_all.groupby('img_filename').ngroup()  # assign group index
    df_all["img_id"] = df_all.groupby('img_filename')['id'].transform('max')  # assign max(row id)

    #print( df_all.head(5).to_string() )
    print( df_all.head(15) )
    print( df_all.tail(15) )

    #update dataset
    dataset.df = df_all
    dataset.export.ExportToCoco(outpath)