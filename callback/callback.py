# -*- coding: utf-8 -*-
import os
import sys
root_dir = os.path.dirname(os.path.dirname(__file__))
print(f'root_dir: {root_dir}')
sys.path.insert(0, root_dir)
sys.path.insert(0, r'D:\personal\code\tf2.0\FacialLandmark')
from log.logger import Logger


class CallBack(object):

    def __init__(self, name='defaul-callback'):
        self.name = name

    def call(self, cfg, dataset, train_brick):
        # Logger.debug('should not reach here!!!', show_type=1, forground=31, background=0)
        Logger.debug(
            'should not reach here!!!',
            show_type=Logger.LOG_STYLE.BOLD,
            forground=Logger.LOG_FRONT_COLOR.RED,
            background=Logger.LOG_BACK_COLOR.DEFAULT
        )


if __name__ == '__main__':
    cb = CallBack()
    cb.call()