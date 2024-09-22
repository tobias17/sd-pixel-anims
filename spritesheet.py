import os, argparse, math, cv2
from typing import Optional
import numpy as np

def spritesheet(in_path:str, save_path:str, max_width:Optional[int]):
   assert os.path.exists(in_path), f"Could not find in_path {in_path}"
   assert os.path.exists(os.path.dirname(save_path)), f"Could not find containing folder for save_path {save_path}"
   images = [cv2.imread(os.path.join(in_path, f), cv2.IMREAD_UNCHANGED) for f in os.listdir(in_path) if f.endswith(".png")]
   assert len(images) > 0, "Found 0 *.png files at the in_path"
   assert all(len(images[0].shape) == len(im.shape) and images[0].shape == im.shape for im in images[1:]), "Images were not all the same size"

   IMG_H, IMG_W = images[0].shape[:2]

   row_count = 1
   row_size = len(images)
   if max_width is not None:
      assert isinstance(max_width, int) and max_width >= 2, f"max_width must be an integer >= 2, got {max_width} ({type(max_width)})"
      while row_size > max_width:
         row_count *= 2
         row_size = math.ceil(row_size / 2)
   
   sheet = np.zeros((IMG_H*row_count, IMG_W*row_size, images[0].shape[2]))
   for y in range(row_count):
      for x in range(row_size):
         i = y * row_size + x
         if i >= len(images):
            continue
         sheet[y*IMG_H:(y+1)*IMG_H, x*IMG_W:(x+1)*IMG_W] = images[i]

   cv2.imwrite(save_path, sheet)   


if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--in-path',   type=str, required=True, help="Path to folder containing the images to package into a spritesheet")
   parser.add_argument('--save-path', type=str, required=True, help="Path to save the spritesheet at")
   parser.add_argument('--max-width', type=int, help="Limits how many sprites can be packed into a single row")
   args = parser.parse_args()

   spritesheet(args.in_path, args.save_path, args.max_width)
