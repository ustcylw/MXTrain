#! /usr/bin/env python
# coding: utf-8
import os, sys
import numpy as np
import cv2 as cv
import utils.utils as Utils



def cv_show_image(image, wait_time=0, name='image'):
    cv.imshow(name, image)
    if cv.waitKey(wait_time) == ord('q'):
        sys.exit(0)


def cv_show_bbox(image, bbox_xyxy, wait_time=0, name='image'):
    cv.rectangle(image, (bbox_xyxy[0][0], bbox_xyxy[0][1]), (bbox_xyxy[1][0], bbox_xyxy[1][1]), (255, 0, 0))
    cv_show_image(image=image, wait_time=wait_time, name=name)


def cv_show_points(image, points, color=(0, 0, 255), radius=1, wait_time=0, name='image'):
    for point in points:
        cv.circle(image, center=(Utils.ToInt(point[0]), Utils.ToInt(point[1])), color=color, radius=radius)
    cv_show_image(image=image, wait_time=wait_time, name=name)