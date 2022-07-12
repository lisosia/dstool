import cv2

def show_inference(img_path, det_out_list, classes):
    """show inference result for testing
    
    :param img_path: img path
    :param det_out_list: list of DetectOutput
    """
    cv2.namedWindow("result", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("result", 640, 640)

    i = cv2.imread(img_path)
    for d in det_out_list:
        box = [int(e) for e in d.box]
        p1 = (box[0], box[1])
        p2 = (box[2], box[3])
        cv2.rectangle(i, p1, p2, (255, 255, 0), 2)
        cv2.putText(i, classes[d.cls], p1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.imshow("result", i)
    cv2.waitKey(0)
    cv2.destroyAllWindows()