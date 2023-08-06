import aicmder as cmder

from aicmder.module.module import serving, moduleinfo


@moduleinfo(name='face')
class FaceModule(cmder.Module):

    def __init__(self, **kwargs) -> None:
        print("init FaceModule", kwargs)

    @serving
    def predict(self, **kwargs):


# https://github.com/serengil/deepface/issues/351
# from deepface.detectors import FaceDetector
# import cv2

# img_path = "couple.jpg"
# detector_name = "opencv"

# img = cv2.imread(img_path)

# detector = FaceDetector.build_model(detector_name) #set opencv, ssd, dlib, mtcnn or retinaface

# obj = FaceDetector.detect_faces(detector, detector_name, img)

# print("there are ",len(obj)," faces")



# https://github.com/serengil/deepface/issues/419
# from retinaface import RetinaFace
# from deepface import DeepFace

# faces = RetinaFace.extract_faces("img.jpg")
# for face in faces:
#     obj = DeepFace.analyze(img)
#     print(obj["age"])

        return '{"data": "hello"}'

