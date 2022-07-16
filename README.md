# dstool : dataset management tool

### Install

```
pip3 install git+https://github.com/lisosia/dstool
```

### Usage

#### 1. init

```
mkdir dstool-example && cd dstool-example && dstool init
```

#### 2. prepare files

2-1. make data/classes.txt which includes newline separated labels

2-2. copy image and voc format labels

```
rsync -av /path/to/data ./data/
```

dstool accepts some folder structure
```
├── data
│   ├── domainA
│   │   └── set3-formatA
│   │       ├── image
│   │       └── label
│   ├── set1
│   │   └── train
│   └── set2
│       └── test

```

#### 3. register data

register two folders
 (we do not register 3rd folder assuming the 3rd folder does not have annotations)
 
```
dstool register --all
```

```
dstool status
#=> [registered] 2 folder
#=>     set1/train               207 ann /  240 img
#=>     set2/test                 56 ann /   60 img
#=>     domainA/set3-formatA       0 ann /    2 img
```

#### 4. train

```
dstool train
#=> run below command to start training
#=> cd /home/username/work/dstool-sample/model/20220714-A && python3 -m yolox.tools.train -f exp001.py -d 1 -b 8 -o -c ../yolox_s.pth
```

run command on another terminal
```
cd /home/username/work/dstool-sample/model/20220714-A && python3 -m yolox.tools.train -f exp001.py -d 1 -b 8 -o -c ../yolox_s.pth
```

#### 5. auto annotate using a trained model

```
dstool auto-annotate data/domainA/set3-formatA/ model/20220714-A/
```

#### 6. dstool annotate to check and fix auto genarated annotation
```
dstool annotate model/20220714-A/
```

it currenty just print labelImg command
```
#=> run below command to start training
#=> labelImg /home/username/work/dstool-sample/data/domainA/set3-formatA/image /home/username/work/dstool-sample/data/classes.txt /home/username/work/dstool-sample/data/domainA/set3-formatA/label
```

### Tips: Partially annotate images in a folder and let a model to do the rest

```
# annotate some images then train a model
dstool annotate data/A
dstool train
# mark as "verified" for manually annotated annotations only
dstool mark-verified data/A
# auto annotate
dstool auto-annotate data/A model/B  # auto annotate
# check and fix auto-annotated annotations
# manually annotated images can be distinguished as "verified" (green background)
# in the labelImg GUI
dstool annotate data/A
```

### Tips: Separate testset

```
dstool mark data/domainA/set3-formatA testset
dstool export --separate-testset
#=> train/valid/test coco annotate file generated instead of train/valid
```