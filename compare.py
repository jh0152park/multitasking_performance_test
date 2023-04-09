import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def compare(org, tar):
    try:
        origin = cv2.imdecode(np.fromfile(org, dtype=np.uint8), cv2.IMREAD_COLOR)[300:-340, 100:-100]
        target = cv2.imdecode(np.fromfile(tar, dtype=np.uint8), cv2.IMREAD_COLOR)[300:-340, 100:-100]
        gray_origin = cv2.cvtColor(origin, cv2.COLOR_RGB2GRAY)
        gray_target = cv2.cvtColor(target, cv2.COLOR_RGB2GRAY)
        (score, diff) = ssim(gray_origin, gray_target, full=True)
        similarity = score * 100.0
        print(f"similarity : {similarity}")
        return similarity
    except ValueError:
        print(f"similarity : {0.0}")
        return 0.0
