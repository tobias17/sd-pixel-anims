import os, argparse, math, cv2, json
from typing import Optional, List
import numpy as np

def map_filename(filename:str, sheet_map:List[str]) -> Optional[str]:
   for prefix in sheet_map:
      if filename.startswith(prefix):
         return prefix
   return None

def spritesheet(in_path:str, save_path:str, sheet_map_path:Optional[int]):
   assert os.path.exists(in_path), f"Could not find in_path {in_path}"
   assert os.path.exists(os.path.dirname(save_path)), f"Could not find containing folder for save_path {save_path}"

   orig_filenames = [f for f in os.listdir(in_path) if f.endswith(".png")]
   if sheet_map_path is not None:
      assert os.path.exists(sheet_map_path), f"A sheet_map path was provided but could not find file at {sheet_map_path}"
      with open(sheet_map_path, "r") as f:
         sheet_map = json.load(f)
      assert isinstance(sheet_map, list), f"Sheet map must be a list, got {type(sheet_map).__name__}"
      for prefix in sheet_map:
         assert isinstance(prefix, str), f"Sheet map must only contain str elements, found '{prefix}' of type {type(prefix).__name__}"
   else:
      sheet_map = [""]
   filename_to_prefix = { f: map_filename(f, sheet_map) for f in orig_filenames }
   found_prefixes = set()
   for filename in orig_filenames:
      value = filename_to_prefix[filename]
      if value is None:
         print(f"WARNING: Could not find mapping for filename {filename}, skipping")
         filename_to_prefix.pop(filename)
      else:
         found_prefixes.add(value)
   assert len(found_prefixes) > 0, f"Found none of the prefixes, have no images to process"
   if len(found_prefixes) < len(sheet_map):
      print(f"WARNING: Missing entries from the following prefixes {list(set(sheet_map).difference(found_prefixes))}")

   filename_to_image = { f: cv2.imread(os.path.join(in_path, f), cv2.IMREAD_UNCHANGED) for f in filename_to_prefix.keys() }
   images = list(filename_to_image.values())
   assert len(images) > 0, "Found 0 *.png files at the in_path"
   assert all(len(images[0].shape) == len(im.shape) and images[0].shape == im.shape for im in images[1:]), "Images were not all the same size"

   IMG_H, IMG_W = images[0].shape[:2]

   row_count = len(found_prefixes)
   row_size  = max(sum(1 if found_prefix == check_prefix else 0 for found_prefix in filename_to_prefix.values()) for check_prefix in found_prefixes)

   sheet = np.zeros((IMG_H*row_count, IMG_W*row_size, images[0].shape[2]))
   print(sheet.shape)
   y = 0
   for prefix in sheet_map:
      if prefix not in found_prefixes:
         continue
      filenames = sorted(list(f for f,p in filename_to_prefix.items() if p == prefix))
      x = 0
      for filename in filenames:
         sheet[y*IMG_H:(y+1)*IMG_H, x*IMG_W:(x+1)*IMG_W] = filename_to_image[filename]
         x += 1
      y += 1

   cv2.imwrite(save_path, sheet)

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--in-path',   type=str, required=True, help="Path to folder containing the images to package into a spritesheet")
   parser.add_argument('--save-path', type=str, required=True, help="Path to save the spritesheet at")
   parser.add_argument('--sheet-map', type=str, help="Path to a json file defining which filename prefixes go in rows together")
   args = parser.parse_args()

   spritesheet(args.in_path, args.save_path, args.sheet_map)
