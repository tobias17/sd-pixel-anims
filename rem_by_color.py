import numpy as np
import cv2, os

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('in_folder', type=str)
parser.add_argument('out_folder', type=str)
args = parser.parse_args()

assert os.path.exists(args.in_folder)
if not os.path.exists(args.out_folder):
    os.mkdir(args.out_folder)

for filename in os.listdir(args.in_folder):
    if not filename.endswith(".png"):
        continue

    img_orig = cv2.imread(os.path.join(args.in_folder, filename))
    img = np.ones((img_orig.shape[0],img_orig.shape[1],4)) * 255.0
    img[:,:,:3] = img_orig

    c = tuple(np.median(img_orig[:5,:,i]) for i in range(3))
    d = np.sum(np.abs(img_orig[:,:,:3] - c), axis=-1)
    m = (d < 8).astype(np.float32)
    m = cv2.dilate(m, np.ones((5,5)), iterations=1)
    m = cv2.erode(m, np.ones((5,5)), iterations=1)
    img[m > 0.5, 3] = 0

    cv2.imwrite(os.path.join(args.out_folder, filename), img)
