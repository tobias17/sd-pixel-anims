import os, argparse
import numpy as np
import cv2

APPEAR_THRESHOLD = 0.1

def quantize(in_folder:str, out_folder:str, bins:int, scale:int):
   assert os.path.exists(in_folder), f"Could not find in_folder at {in_folder}, needs to exist"
   if not os.path.exists(out_folder):
      os.makedirs(out_folder)

   for filename in os.listdir(in_folder):
      if not filename.endswith(".png"):
         continue
      bgra = cv2.imread(os.path.join(in_folder, filename), cv2.IMREAD_UNCHANGED)
      hsv  = cv2.cvtColor(bgra[:,:,:3], cv2.COLOR_BGR2HSV)

      assert hsv.shape[0] % scale == 0 and hsv.shape[1] % scale == 0, f"im shape ({hsv.shape}) not divisible by scale ({scale})"
      im_hsv  = np.zeros((hsv.shape[0] // scale, hsv.shape[1] // scale, 3))
      im_bgra = np.zeros((hsv.shape[0] // scale, hsv.shape[1] // scale, 4))
      for y in range(im_hsv.shape[0]):
         for x in range(im_hsv.shape[1]):
            alpha_chunk = bgra[y*scale:(y+1)*scale, x*scale:(x+1)*scale, 3]
            alpha_mask: np.ndarray = (alpha_chunk >= 5) # type: ignore
            alpha_value = alpha_mask.astype(np.float32).mean()
            if alpha_value < APPEAR_THRESHOLD:
               continue

            hsv_chunk = hsv[y*scale:(y+1)*scale, x*scale:(x+1)*scale, :]
            for c in range(3):
               z = hsv_chunk[:, :, c][alpha_mask]
               im_hsv[y, x, c] = np.median(hsv_chunk[:, :, c][alpha_mask])
            im_bgra[y, x, 3] = alpha_value * 255.0

      for idx, ch_size in enumerate([180.0, 256.0, 256.0]):
         bin_scale = int(ch_size / bins)
         im_hsv[:,:,idx] = np.floor_divide(im_hsv[:,:,idx], bin_scale) * bin_scale
      im_bgra[:, :, :3] = cv2.cvtColor(im_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
      cv2.imwrite(os.path.join(out_folder, filename), im_bgra)

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--in-path',  type=str, required=True, help="Path to the source folder containing the rendered frames")
   parser.add_argument('--out-path', type=str, required=False, help="Path to the output folder where resulting images should be saved")
   parser.add_argument('--bins',  type=int, default=16, help="The number of bins for each axis to quanitze into")
   parser.add_argument('--scale', type=int, default=8, help="The scaling ratio to downsample at")
   args = parser.parse_args()

   quantize(args.in_path, args.out_path, args.bins, args.scale)
