"""Implement per model model train"""

import os
from string import Template

from dstool import model

EXP_NAME = 'exp001'
EXP_PATH = 'exp001.py'
IS_FP16 = False

class Model:

    def __init__(self, classes):
        self.classes = classes
        self.predictor = None

    def train(self, data_dir, out_dir):
        """Train yolox
    
        :param data_dir: data/ann dir from root. expects data_dir/data & data_dir/annotations/trainval.txt
        :param outdir: output directory
        """
        exp_template_path = os.path.join(os.path.dirname(__file__), 'template.exp001.py')
        assert os.path.exists(exp_template_path)
        exp_file_c = Template(open(exp_template_path).read()).substitute(
                data_dir = data_dir,
                num_class = len(self.classes))
        with open(os.path.join(out_dir, EXP_PATH), 'w+') as f:
            f.write(exp_file_c)

        #TODO: download checkpoint to somewhere

        # TODO: run actual command within `dstool train`
        print('run below command to start training')
        print(f'cd {out_dir} && python3 -m yolox.tools.train -f exp001.py -d 1 -b 8 -o -c ../yolox_s.pth')

    def infer(self, out_dir, img_path):
        """Infer and return list[DetectOutput]
        
        :param out_dir: out_dir when train. e.g. model/20220710
        """
        import torch
        import yolox.tools.demo as demo

        # load predictor
        if not self.predictor:
            exp_path = os.path.join(out_dir, EXP_PATH)
            exp = demo.get_exp(exp_path)
            # set default
            exp.test_conf = 0.25
            exp.nmsthre = 0.45
            exp.test_size = (640, 640)
            self.model = exp.get_model()
            # set gpu fp16 eval
            if True:
                self.model.cuda()
                if IS_FP16: self.model.half()
            self.model.eval()
            # load weight
            ckpt_file = os.path.join(out_dir, 'YOLOX_outputs', EXP_NAME, 'latest_ckpt.pth')
            assert os.path.exists(ckpt_file)
            ckpt = torch.load(ckpt_file, map_location="cpu")
            # load the model state dict
            self.model.load_state_dict(ckpt["model"])
            # define predictor
            self.predictor = demo.Predictor(
                self.model, exp, self.classes, None, None, "gpu", IS_FP16, False)

        # pred
        outputs, img_info = self.predictor.inference(img_path)
        bboxes, cls, scores, = predictor_visual(outputs[0], img_info)

        if False:  # check
            import cv2
            i = cv2.imread(img_path)
            for box, cls, score in zip(bboxes, cls, scores):
                cv2.rectangle(i, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (255))
            cv2.imshow("WINNAME", i)
            cv2.waitKey(0)

        result = []
        for box, cls, score in zip(bboxes, cls, scores):
            result.append(model.DetectOutout(box, cls, score))
        #print(result)
        return result

# raw output to img coordinate box
# from https://github.com/Megvii-BaseDetection/YOLOX/blob/419778480ab6ec0590e5d3831b3afb3b46ab2aa3/tools/demo.py#L168
def predictor_visual(output, img_info):
    ratio = img_info["ratio"]
    img = img_info["raw_img"]
    if output is None:
        return ([], [], [])
    output = output.cpu()
    bboxes = output[:, 0:4]

    # preprocessing: resize
    bboxes /= ratio

    cls = output[:, 6]
    scores = output[:, 4] * output[:, 5]

    return (bboxes.numpy(), cls.numpy(), scores.numpy())


# test
if __name__ == "__main__":
    import sys
    m = Model(["A", "B", "C"])
    m.infer(sys.argv[1], sys.argv[2])