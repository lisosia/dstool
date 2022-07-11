class DetectOutout:
    def __init__(self, box_xyxy, cls_index, conf):
        self.box = box_xyxy
        self.cls = int(cls_index)
        self.conf = conf

    def __repr__(self):
        return f'<DetectOutput box={self.box} cls={self.cls} conf={self.conf:.3f}>'

class BaseModel:
    def __init__(self, classes):
        raise NotImplementedError()

    def train(self, data_dir, out_dir):
        """Train"""
        raise NotImplementedError()

    def infer(self, out_dir, img_path):
        """Infer on img. Outputs List[DetectOutput]"""
        raise NotImplementedError()