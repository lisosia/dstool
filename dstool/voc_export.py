"""VOCフォーマットでエクスポートする"""

from string import Template
import xml.etree.ElementTree as ET

import cv2

from dstool.common import *
from dstool import model

VOC_FILE_INIT = """\
<annotation>
<folder></folder>
<filename></filename>
<path></path>
<source>
    <database>Unknown</database>
</source>
<size>
    <width>0</width>
    <height>0</height>
    <depth>3</depth>
</size>
<segmented>0</segmented>
</annotation>
"""

OBJECT_TEMPLATE = Template("""
<object>
    <name>$class_name</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
        <xmin>$xmin</xmin>
        <ymin>$ymin</ymin>
        <xmax>$xmax</xmax>
        <ymax>$ymax</ymax>
    </bndbox>
</object>
""")

def voc_export(img_path, ann_path, classes, detect_output_list):
    """Create voc format annotation file given list of DetectOutput"""
    if os.path.exists(ann_path):
        error_exit(f'file exists {ann_path}')

    # load
    root = ET.fromstring(VOC_FILE_INIT)

    # filename
    root.find('filename').text = os.path.basename(img_path)

    # shape
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    if len(img.shape) >= 3:
        c = img.shape[2]
    else:
        c = 1
    root.find('size/height').text = str(h)
    root.find('size/width').text = str(w)
    root.find('size/depth').text = str(c)

    # objects
    for o in detect_output_list:
        sub = ET.fromstring(OBJECT_TEMPLATE.substitute(
            class_name = classes[o.cls],
            xmin = int(o.box[0]),
            ymin = int(o.box[1]),
            xmax = int(o.box[2]),
            ymax = int(o.box[3]),
        ))
        root.append(sub)
    
    print(root)

    tree = ET.ElementTree(root)
    tree.write(ann_path)

if __name__ == "__main__":    
    img = "data/set2/test/apple_77.jpg"
    ann = "/tmp/apple_77.xml"
    classes = ["A", "B", "C"]
    li = [model.DetectOutout([0,0,10,10], 1, 0.8), model.DetectOutout([0,0,10,10], 0, 0.8)]
    voc_export(img, ann, classes, li)