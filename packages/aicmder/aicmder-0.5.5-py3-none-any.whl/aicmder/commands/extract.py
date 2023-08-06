import argparse
import aicmder as cmder
import os
from aicmder.commands.utils import _command_prefix as cmd
from aicmder.commands import register
from typing import List
import cv2

@register(name='{}.extract'.format(cmd), description='extract video')
class ExtractCommand:

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description=self.__class__.__doc__, prog='{} extract'.format(cmd), usage='%(prog)s', add_help=True)
        self.parser.add_argument('--frame', '-f', required=False, type=int, default=10, help='extract interval frame')
        self.parser.add_argument('--video', '-v', required=True)
        self.cur_path = os.getcwd()
        self.parser.add_argument('--save', '-s', required=False, default=f"{self.cur_path}/images")


    def execute(self, argv: List) -> bool:
        print(argv)
        self.args = self.parser.parse_args(argv)
        skip_frame = self.args.frame
        video_path, save_path = self.args.video, self.args.save
        print(self.args.video, skip_frame, save_path)
        assert os.path.exists(video_path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        cap = cv2.VideoCapture(video_path)
        index = 0
        while True:
            ret, frame = cap.read()
            index += 1
            if ret and frame is not None:
                # cv2.imshow(os.path.basename(video_path), frame)
                if index % skip_frame == 0:
                    cv2.imwrite(f"{save_path}/{index}.jpg", frame)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        