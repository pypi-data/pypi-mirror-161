
import cv2
from matplotlib import collections
import numpy as np
import shapely.geometry
import shapely.affinity
from collections import defaultdict
import base64

from fence_detect import RotatedRect, Fence


class Wearing(RotatedRect):

    def set_label(self, label):
        self.label = label

def check_person_wear_helmet(resp_d_person, resp_d, h, w):
    
    obj_rect_list = []
    for i, obj in enumerate(resp_d["data"]):
        start_x, end_x, end_y, start_y = obj["start_x"], obj["end_x"], obj["end_y"], obj["start_y"]
        width = end_x - start_x
        height = end_y - start_y
        center_x = start_x + width / 2
        center_y = start_y + height / 2
        obj_rect = Wearing()
        obj_rect.set_param(center_x, center_y, width, height, 0)
        obj_rect.set_label(obj["label"])
        obj_rect_list.append(obj_rect)

    resp_d["person"] = []
    for i, obj in enumerate(resp_d_person["data"]):
        start_x, end_x, end_y, start_y = obj["start_x"], obj["end_x"], obj["end_y"], obj["start_y"]
        width = end_x - start_x
        height = end_y - start_y
        center_x = start_x + width / 2
        center_y = start_y + height / 2
        x0, x1, y0, y1 = obj["x0"], obj["x1"], obj["y0"], obj["y1"]
        person_rect = Fence([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], w=w, h=h)
        # person_rect = RotatedRect()
        # person_rect.set_param(center_x, center_y, width, height, 0)
        

        for obj_rect in obj_rect_list:
            if person_rect.pointPolygonTest((obj_rect.cx, obj_rect.cy)) == 1:
                if "detection" in obj:
                    obj["detection"] += obj_rect.label + " "
                else:
                    obj["detection"] = obj_rect.label + " "
                break
        resp_d["person"].append(obj)
        
        # break




