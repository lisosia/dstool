"""Implement per model model train"""

import os
from string import Template

def train(data_dir, num_class, out_dir):
    """Train yolox

    :param data_dir: data/ann dir from root. expects data_dir/data & data_dir/annotations/trainval.txt
    :param num_class: num of classes
    :param outdir: output directory
    """
    exp_template_path = os.path.join(os.path.dirname(__file__), 'template.exp001.py')
    assert os.path.exists(exp_template_path)
    exp_file_c = Template(open(exp_template_path).read()).substitute(
            data_dir = data_dir,
            num_class = num_class)
    with open(os.path.join(out_dir, "exp001.py"), 'w+') as f:
        f.write(exp_file_c)

    # TODO: run actual command within `dstool train`
    print('run below command to start training')
    print(f'cd {out_dir} && python3 -m yolox.tools.train -f exp001.py -d 1 -b 8 -o -c ../yolox_s.pth')
