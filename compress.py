import numpy as np
import argparse
import cv2
import os

parser = argparse.ArgumentParser()
parser.add_argument('input',  type=str, help="input file or directory to compress")
parser.add_argument('output', type=str, help="output file or directory, must be same type as input")
parser.add_argument('-r', '--ratio', type=int, default=8, help="the compression ratio, e.g. 8 will compress an 8x8 region into a single pixel")
parser.add_argument('-a', '--allow-transparent', action='store_true', help="if we allow transparency on the output pixels, default creates binary transparency")
parser.add_argument('-s', '--spritesheet', type=str, required=False, help="path to save a spritesheet to generate, only supported in folder mode")
args = parser.parse_args()

R = args.ratio

assert os.path.exists(args.input), f"Failed to find input path, searched for {args.input}"
if os.path.isfile(args.input):
    filepaths = [args.input]
    out_filepath = args.output
else:
    filepaths = [os.path.join(args.input, f) for f in os.listdir(args.input)]
    out_filepath = None
    assert os.path.exists(args.input)
    if not os.path.exists(args.output):
        os.mkdir(args.output)

all_imgs = []
for filepath in filepaths:
    img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED) * 1.0 # type: ignore
    assert img.shape[0] % R == 0, f"{img.shape[0]} % {R} != 0"
    assert img.shape[1] % R == 0, f"{img.shape[1]} % {R} != 0"

    if img.shape[2] == 3:
        out = np.zeros((img.shape[0]//R,img.shape[1]//R,3))
        for y in range(out.shape[0]):
            for x in range(out.shape[1]):
                pixels = img[y*R:(y+1)*R,x*R:(x+1)*R].reshape(R*R, 3)
                
                b_med = np.median(pixels[:,0])
                g_med = np.median(pixels[:,1])
                r_med = np.median(pixels[:,2])

                out[y,x] = (b_med,g_med,r_med)
    elif img.shape[2] == 4:
        out = np.zeros((img.shape[0]//R,img.shape[1]//R,4))
        for y in range(out.shape[0]):
            for x in range(out.shape[1]):
                pixels = img[y*R:(y+1)*R,x*R:(x+1)*R].reshape(R*R, 4)
                visible = pixels[pixels[:,3] > 50]
                if visible.shape[0] == 0:
                    continue
                
                b_med = np.median(visible[:,0])
                g_med = np.median(visible[:,1])
                r_med = np.median(visible[:,2])
                if args.allow_transparent:
                    a_med = np.median(pixels[:,3])
                else:
                    a_med = 0.0 if visible.shape[0] < pixels.shape[0] * 0.5 else 255.0

                out[y,x] = (b_med,g_med,r_med,a_med)
    else:
        raise ValueError(f"Image has {img.shape[2]} color channels, expected 3 or 4, from {filepath}")

    cv2.imwrite(out_filepath if out_filepath is not None else os.path.join(args.output_dir, os.path.basename(filepath)), out)
    all_imgs.append(out)

if args.spritesheet:
    assert len(all_imgs) >= 2, f"Cannot create spritesheet with only {len(all_imgs)} images, at least 2 required"
    assert all(img.shape[0] == all_imgs[0].shape[0] for img in all_imgs[1:])

    sheet = np.zeros((all_imgs[0].shape[0],sum(img.shape[1] for img in all_imgs),4))
    offset = 0
    for img in all_imgs:
        sheet[:,offset:offset+img.shape[1]] = img
        offset += img.shape[1]
    cv2.imwrite(args.spritesheet, sheet)
