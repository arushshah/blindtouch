import numpy as np
import cv2
import os
import glob
import sys

DIM=(1280, 720)
K=np.array([[535.6852457640018, 0.0, 669.2132763083513], [0.0, 534.0036866412527, 354.42099468045143], [0.0, 0.0, 1.0]])
D=np.array([[-0.10233486931782577], [0.22394766572382502], [-0.5845007867009375], [0.3785197455801081]])

def undistort(img_path):
    img = cv2.imread(img_path)
    h,w = img.shape[:2]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cv2.imshow("undistorted", undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
if __name__ == '__main__':
    for p in sys.argv[1:]:
        undistort(p)
