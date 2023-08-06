import cv2
import os
from Yolov5_torch import Yolov5
from fence_detect import Fence, check_object_in_fence
import numpy as np


def plot_one_box(x, im, color=(128, 128, 128), label=None, line_thickness=1):
    # Plots one bounding box on image 'im' using OpenCV
    assert im.data.contiguous, 'Image not contiguous. Apply np.ascontiguousarray(im) to plot_on_box() input image.'
    tl = line_thickness or round(
        0.002 * (im.shape[0] + im.shape[1]) / 2) + 1  # line/font thickness
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(im, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(im, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(im, label, (c1[0], c1[1] - 2), 0, tl / 3,
                    [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)


def extract_rect(frame, roi, offset=0):
    extract_frame = frame[int(roi[1]) - offset:int(roi[1]+roi[3]) + offset, 
                            int(roi[0])- offset:int(roi[0]+roi[2]) + offset]
    img = np.ascontiguousarray(extract_frame).astype(np.float32)
    return img


imgsz = [640, 640]
# weights = '/home/faith/yolov5m6.pt'
weights = '/home/faith/yolov5m.pt'
weights = '/home/faith/yolov5l.pt'
# weights = '/home/faith/yolov5s6.pt'
yolo = Yolov5(weights=weights, imgsz=imgsz, classes=[0], conf_thres=0.25, iou_thres=0.4)
fence_list = []

filename = "/Users/faith/Downloads/D01-20220503-0727.mp4"
filename = "/home/faith/wuxi.mp4"
name = os.path.basename(filename).replace(".mp4", "")
cap = cv2.VideoCapture(filename)

i = 0
xyxy = []
while True:
    ret, frame = cap.read()
    ratio = max(frame.shape) / 1280
    width = int(frame.shape[1] / ratio)
    height = int(frame.shape[0] / ratio)
    dim = (width, height)

    # resize image
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    if ret and i == 0:
        roi = cv2.selectROI(name, frame, fromCenter=False, showCrosshair=False)
        x, y, w, h = roi
        # fence = Fence([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
        # fence_list.append(fence)
        xyxy = [x, y, x + w, y + h]

    i += 1
    if ret and i % 3 == 0:  # and i % 60 == 0:
        # Crop image
        extract_frame = extract_rect(frame, roi, 0)
        resp_d = yolo.predict_image(extract_frame, debug=0)
        # check_object_in_fence(resp_d, fence_list, calculate_usage=True)
        if len(resp_d["data"]) > 0:
            # print(resp_d["data"])
            plot_one_box(xyxy, frame, label="Detect people")
        track_frame = cv2.rectangle(frame, (x, y), (x + w, y + h), 255, 2)
        cv2.imshow(name, track_frame)

    if not ret:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
