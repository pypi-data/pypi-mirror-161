import os
# os.environ["CMD_CLIENT_PORT"] = "6655"
# os.environ["CMD_WORKER_PORT"] = "6656"
# os.environ["CMD_PYTHON_PATH"] = "/home/faith/miniconda3/envs/torch/bin/python"
import aicmder as cmder
from aicmder.module.module import serving, moduleinfo
import io
from PIL import Image
import json

import base64
import cv2
import numpy as np
from Yolov5_torch import Yolov5
from baili import shoot
from fence_detect import Fence, check_object_in_fence, draw_fence, check_person_occlusion
from helmet_detect import check_person_wear_helmet


def readb64(base64_string, save=False):
    # sbuf = StringIO()
    # sbuf.write(base64.b64decode(base64_string))
    # pimg = Image.open(sbuf)
    img_array = io.BytesIO(base64.b64decode(base64_string))
    pimg = Image.open(img_array)  # RGB
    if save:
        pimg.save('image.png', 'PNG')
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)  # BGR


@moduleinfo(name='image')
class ImagePredictor(cmder.Module):

    # https://stackoverflow.com/questions/9575409/calling-parent-class-init-with-multiple-inheritance-whats-the-right-way
    def __init__(self, **kwargs) -> None:
        # print('init', file_path)
        # Yolov5.__init__(self)
        print("init ImagePredictor", kwargs)

        device = ''
        if 'device_id' in kwargs:
            device = kwargs['device_id']
            if device == "-1" or device == -1:
                device = 'cpu'

        coin = kwargs["Coin"]
        imgsz = coin["imgsz"]
        weights = coin["model"]
        self.coin_yolo = Yolov5(weights=weights, imgsz=imgsz, conf_thres=0.82, device=device)
        self.debug = 0

        if "baili" in kwargs:
            baili = kwargs["baili"]
            imgsz = baili["imgsz"]
            weights = baili["model"]
            self.baili_yolo = Yolov5(weights=weights, imgsz=imgsz, device=device)

        if "Cake" in kwargs:
            Cake = kwargs["Cake"]
            imgsz = Cake["imgsz"]
            weights = Cake["model"]
            self.Cake_yolo = Yolov5(weights=weights, imgsz=imgsz, device=device)

        if "Person" in kwargs:
            Person = kwargs["Person"]
            imgsz = Person["imgsz"]
            weights = Person["model"]
            self.person_yolo = Yolov5(weights=weights, imgsz=imgsz, classes=[0], conf_thres=0.4, device=device)

        if "Helmet" in kwargs:
            Helmet = kwargs["Helmet"]
            imgsz = Helmet["imgsz"]
            weights = Helmet["model"]
            # [['other_clothes' 'reflective_clothes' 'person' 'helmet']]
            self.Helmet_yolo = Yolov5(weights=weights, imgsz=imgsz, classes=[1, 3], device=device)  

    
        if "TenCake" in kwargs:
            TenCake = kwargs["TenCake"]
            imgsz = TenCake["imgsz"]
            weights = TenCake["model"]
            self.TenCake_yolo = Yolov5(weights=weights, imgsz=imgsz, device=device)
            

    # json base64
    @serving
    def predict(self, **kwargs):
        # print('receive', kwargs)
        resp_d = {}
        resp_d["data"] = []
        self.debug = 0
        try:
            img_base64 = kwargs["img"]
            # print('receive', img_base64[:100])
            img_bgr = readb64(img_base64)

            model_name = kwargs["model"]
            if "debug" in kwargs and kwargs["debug"] > 0:
                try:
                    self.debug = int(kwargs["debug"])
                except:
                    pass
                
            # print(self.debug)
            if "Coin" ==  model_name:
                resp_d = self.coin_yolo.predict_image(img_bgr=img_bgr, debug=self.debug)
            elif "baili" ==  model_name:
                resp_d = self.baili_yolo.predict_image(img_bgr=img_bgr,  debug=self.debug)
                if "base_x" in kwargs and "base_y" in kwargs and len(resp_d["data"]) > 0:
                    base_center_x = kwargs["base_x"]
                    base_center_y = kwargs["base_y"]
                    shoot(resp_d, base_center_x, base_center_y)
            elif "Cake" ==  model_name:
                resp_d = self.Cake_yolo.predict_image(img_bgr=img_bgr, debug=self.debug)
            # elif "Person" in model_name:
                resp_d_person = self.person_yolo.predict_image(img_bgr=img_bgr, debug=self.debug)
            elif "Helmet" ==  model_name:
                resp_d = self.Helmet_yolo.predict_image(img_bgr=img_bgr, debug=self.debug)
                resp_d_person = self.person_yolo.predict_image(img_bgr=img_bgr, debug=self.debug)
                h, w, _ = img_bgr.shape
                check_person_wear_helmet(resp_d_person, resp_d, h, w)
            elif "TenCake" == model_name:
                resp_d = self.TenCake_yolo.predict_image(img_bgr=img_bgr, debug=self.debug)


            if "debug" in kwargs and kwargs["debug"] == 1:
                try:
                    del resp_d["img"]
                except Exception as e:
                    pass

            if "fence" in kwargs:
                fences = kwargs["fence"]
                h, w, _ = img_bgr.shape
                fence_list = []
                for f in fences:
                    fence = Fence(f, w, h)
                    fence_list.append(fence)
                calculate_usage = False
                if "Cake" in model_name:
                    calculate_usage = True
                check_object_in_fence(resp_d, fence_list, calculate_usage=calculate_usage, model_name=model_name)
                if calculate_usage:
                    check_person_occlusion(resp_d_person, fence_list, resp_d)
                if "debug" in kwargs:
                    draw_fence(fence_list, img_bgr, resp_d, kwargs["debug"])

        except Exception as e:
            print(e)

        # for debug
        # resp_d = {"data": [{"start_x": 399, "start_y": 99, "end_x": 467, "end_y": 113, "x0": 0.5541666666666667, "x1": 0.6486111111111111, "y0": 0.2877906976744186, "y1": 0.32848837209302323, "c": 0, "label": "enermy 0.94", "conf": 0.9433093070983887}, {"start_x": 451, "start_y": 88, "end_x": 515, "end_y": 100, "x0": 0.6263888888888889, "x1": 0.7152777777777778, "y0": 0.2558139534883721, "y1": 0.29069767441860467, "c": 0, "label": "enermy 0.75", "conf": 0.7499269247055054}]}

        json_ret = json.dumps(resp_d)
        # print(json_ret)
        return json_ret

# pyarmor obfuscate YoloModule.py
# delete init.py
# curl -s 127.0.0.1:8099/predict -X POST -d '{"img_base64": "asdasdasddsa"}'
if __name__ == "__main__":
    # os.system("export CMD_WORKER_PORT=6656")
    # os.system("export CMD_CLIENT_PORT=6655")

    # config = {'image': {'name': 'YoloModule', 'init_args':
    #                     {
    #                         'Coin': {
    #                             # /home/faith/dl_project/coin/27.pt
    #                             # "model": '/home/faith/android_viewer/thirdparty/yolov5/runs/train/exp42/weights/best.pt',
    #                             "model": '/home/faith/dl_project/coin/42.pt',
    #                             "imgsz": [1280, 1280]
    #                         },
    #                         # 'baili': {
    #                         #     "model": '/home/faith/AI_baili_train/best5000.pt',
    #                         #     "imgsz": [768, 768]
    #                         # },
    #                         'Cake': {
    #                             # "model": '/home/faith/android_viewer/thirdparty/yolov5/runs/train/exp33/weights/best.pt',
    #                             # 34.pt
    #                             "model": '/home/faith/dl_project/cake/35.pt',
    #                             "imgsz": [1280, 1280]
    #                         },
    #                         'Person': {                            
    #                             "model": '/home/faith/yolov5m.pt',
    #                             "imgsz": [1280, 1280]
    #                         }
    #                     }}}
    
    with open("config.json") as json_f:
        config = json.load(json_f)
        # print(config)
        exec_cmd = ['-w', config["w"], '-c', json.dumps(config["config"]),
                   '-p', config["port"], '--max_connect', config["max_conn"], '--device_map']
        exec_cmd.extend(config["device"])
        print(exec_cmd)
        serve = cmder.serve.ServeCommand()
        serve.execute(exec_cmd)

    # serve = cmder.serve.ServeCommand()
    # serve.execute(['-w', '1', '-c', json.dumps(config),
    #                '-p', '8099', '--max_connect', '10', '--device_map', '0'])
