import cv2
import numpy as np
import shapely.geometry
import shapely.affinity
from collections import defaultdict
import base64


class RotatedRect:

    def set_param(self, cx, cy, w, h, angle):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.angle = angle

    #  (center(x, y), (width, height), angle of rotation)
    def __init__(self, minAreaRect=None):
        if minAreaRect is not None:
            self.cx = minAreaRect[0][0]
            self.cy = minAreaRect[0][1]
            self.w = minAreaRect[1][0]
            self.h = minAreaRect[1][1]
            self.angle = minAreaRect[2]

    def get_contour(self):
        w = self.w
        h = self.h
        c = shapely.geometry.box(-w/2.0, -h/2.0, w/2.0, h/2.0)
        rc = shapely.affinity.rotate(c, self.angle)
        return shapely.affinity.translate(rc, self.cx, self.cy)

    def intersection(self, other):
        return self.get_contour().intersection(other.get_contour())

    def union(self, other):
        return self.get_contour().union(other.get_contour())

    def iou(self, other):
        return self.intersection(other).area / self.union(other).area

    def occlusion_rate(self, other):
        return self.intersection(other).area / self.get_contour().area


class Fence:

    def __init__(self, points, w=1, h=1) -> None:
        self.contours = []
        for x, y in points:
            self.contours.append([int(w * x), int(h * y)])
        self.contours = [np.array(self.contours, dtype=np.int32)]
        self.min_rect = cv2.minAreaRect(self.contours[0])
        self.box = cv2.boxPoints(self.min_rect)
        self.fence_rect = RotatedRect(self.min_rect)
        try:
            self.fence_area = cv2.contourArea(self.contours[0])
        except Exception as e:
            self.fence_area = self.fence_rect.get_contour().area

    def iou(self, other):
        return self.fence_rect.iou(other.fence_rect)

    def area(self):
        return self.fence_area

    def pointPolygonTest(self, point=(490, 125)):
        return cv2.pointPolygonTest(self.box, point, False)

    def center(self):
        return (self.fence_rect.cx, self.fence_rect.cy)

    def width(self):
        # print(self.fence_rect.w, self.fence_rect.h)
        return max(self.fence_rect.h, self.fence_rect.w)

    def height(self):
        return min(self.fence_rect.h, self.fence_rect.w)

def argmax(lst):
  return lst.index(max(lst))


def check_object_in_fence(resp_d, fence_list, calculate_usage=False, gap_w=25, gap_h=35, model_name=''):

    new_d = []
    deli_compensation = 5
    if calculate_usage:
        resp_d["fence_usage"] = defaultdict(int)
        fence_usage_by_width = defaultdict(int)
        # fence_obj_height = defaultdict(list)
        fence_obj_type = defaultdict(str)
    for j, obj in enumerate(resp_d["data"]):
        start_x, end_x, end_y, start_y = obj["start_x"], obj["end_x"], obj["end_y"], obj["start_y"]
        width = end_x - start_x
        height = end_y - start_y
        center_x = start_x + width / 2
        center_y = start_y + height / 2
        hasSelect = False
        iou_list = []

        obj_rect = RotatedRect()
        obj_rect.set_param(center_x, center_y, width, height, 0)
        for i, fence in enumerate(fence_list):
            if calculate_usage:
                    fence_obj_type[i] = obj["label"]
                    if "Deli" in obj["label"]:
                        obj_rect_gap = RotatedRect()
                        obj_rect_gap.set_param(center_x, center_y, width + deli_compensation, height + deli_compensation, 0)
                        resp_d["fence_usage"][i] += fence.fence_rect.occlusion_rate(obj_rect_gap)

                        # resp_d["fence_usage"][i] += (width) * (height)
                        fence_usage_by_width[i] += (width + deli_compensation)
                    else:
                        obj_rect_gap = RotatedRect()
                        obj_rect_gap.set_param(center_x, center_y, width + gap_w, height + gap_h, 0)
                        resp_d["fence_usage"][i] += fence.fence_rect.occlusion_rate(obj_rect_gap)

                        # resp_d["fence_usage"][i] += (width + gap_w) * (height + gap_h)
                        fence_usage_by_width[i] += (width + gap_w)
                    # fence_obj_height[i].append(height)
            if fence.pointPolygonTest((center_x, center_y)) == 1 and not hasSelect:
                # if i == 4:
                #     print(width, height, width * height, obj["label"])
                obj["fence"] = i
                new_d.append(obj)
                hasSelect = True

            iou_area = obj_rect.occlusion_rate(fence.fence_rect)
            iou_list.append(iou_area)
        if not hasSelect and "Coin" not in obj["label"]:
            fence_index = argmax(iou_list)
            # print(j, width, height, width * height, obj["label"], iou_list, fence_index, obj_rect.get_contour().area, fence_list[fence_index].area())
            obj["fence"] = fence_index
            new_d.append(obj)

            # if calculate_usage:
            #     if "Deli" in obj["label"]:
            #         obj_rect_gap = RotatedRect()
            #         obj_rect_gap.set_param(center_x, center_y, width + deli_compensation, height + deli_compensation, 0)
            #         resp_d["fence_usage"][fence_index] += fence.fence_rect.occlusion_rate(obj_rect_gap)
            #         fence_usage_by_width[fence_index] += (width + deli_compensation)
            #     else:
            #         obj_rect_gap = RotatedRect()
            #         obj_rect_gap.set_param(center_x, center_y, width + gap_w, height + gap_h, 0)
            #         resp_d["fence_usage"][fence_index] += fence_list[fence_index].fence_rect.occlusion_rate(obj_rect_gap)
            #         # resp_d["fence_usage"][fence_index] += (width + gap_w) * (height + gap_h)
            #         fence_usage_by_width[fence_index] += (width + gap_w)

                # fence_obj_height[fence_index].append(height)
    # print("---", len(new_d), len(resp_d["data"]))
    resp_d["data"] = new_d
    if calculate_usage:
        for fence_idx in resp_d["fence_usage"]:
            # current_fence = fence_list[fence_idx]

            # usage = resp_d["fence_usage"][fence_idx] / current_fence.area()
            usage = resp_d["fence_usage"][fence_idx]

            # if "Cake" in fence_obj_type[fence_idx]:
            #     obj_heights = fence_obj_height[fence_idx]
            #     obj_heights.sort()
            #     if len(obj_heights) > 0:
            #         min_height = obj_heights[0]
            #         min_height_scale = min_height * 1.85
            #         # if fence_idx == 4:
            #             # print(min_height, min_height_scale, current_fence.height(), current_fence.width(), usage)

            #         if min_height_scale > current_fence.height():
            #             usage = fence_usage_by_width[fence_idx] / current_fence.width()

            if usage > 1:
                usage = 1
            resp_d["fence_usage"][fence_idx] = usage
            # print(fence_idx, fence_list[fence_idx].area())
    # print(new_d, len(new_d))



def check_person_occlusion(resp_d_person, fence_list, resp_d, occlusion_threshold=0.1):
    resp_d["occ"] = defaultdict(int)
    for i, obj in enumerate(resp_d_person["data"]):
        start_x, end_x, end_y, start_y = obj["start_x"], obj["end_x"], obj["end_y"], obj["start_y"]
        width = end_x - start_x
        height = end_y - start_y
        center_x = start_x + width / 2
        center_y = start_y + height / 2
        person_rect = RotatedRect()
        person_rect.set_param(center_x, center_y, width, height, 0)
        for i, fence in enumerate(fence_list):
            # print("----check", i, fence.fence_rect.occlusion_rate(person_rect))
            resp_d["occ"][i] += fence.fence_rect.occlusion_rate(person_rect)


def draw_fence(fence_list, img_bgr, resp_d, debug=None):
    if debug is not None and debug > 0:
        try:
            line_thickness = 3
            tl = line_thickness or round(
                0.002 * (img_bgr.shape[0] + img_bgr.shape[1]) / 2) + 1  # line/font thickness
            tf = max(tl - 1, 1)  # font thickness

            for i, fence in enumerate(fence_list):
                c1 = (int(fence.fence_rect.cx), int(fence.fence_rect.cy))

                if i in resp_d["fence_usage"]:
                    usage = "{:.4f}".format(resp_d["fence_usage"][i])
                else:
                    usage = "no data"
                if "occ" in resp_d:
                    usage += "({:.4f})".format(resp_d["occ"][i])
                label = str(i) + ":" + usage
                # label = str(i)
                cv2.drawContours(img_bgr, fence.contours, 0, (255, 0, 0), 2)
                # print(c1)
                cv2.putText(img_bgr, label, (c1[0], c1[1] - 2), 0, tl / 3,
                            (255, 0, 0), thickness=tf, lineType=cv2.LINE_AA)
            cv2.imwrite('detect_torch_fence.png', img_bgr)

            # return fence
            if debug > 1:
                with open('detect_torch_fence.png',  'rb') as img_f:
                    img = img_f.read()
                    resp_d["img"] = base64.b64encode(img).decode('utf8')
        except Exception as e:
            pass


if __name__ == "__main__":
    h, w = 720, 1280
    points = [[0.4071, 0.4052], [0.3932, 0.4385], [0.5015, 0.5224],
              [0.5129, 0.4834], [0.5186, 0.4645], [0.4128, 0.3879]]
    fence = Fence(points, w, h)

    object = [[0.1, 0.1], [0.5, 0.1], [0.5, 0.5], [0.1, 0.5]]
    o = Fence(object, w, h)

    print(fence.iou(o), fence.area())
    print(fence.pointPolygonTest((w * 0.41, h * 0.41)) == 1)
    print(fence.pointPolygonTest(o.center()))
