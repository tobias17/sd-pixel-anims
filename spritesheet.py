import os, argparse, cv2, json, re
from typing import Optional, List, Tuple
import numpy as np

def map_filename(filename:str, sheet_map:List[str]) -> Optional[str]:
   for pattern in sheet_map:
      if re.match(pattern, filename):
         return pattern
   return None

def spritesheet(in_path:str, save_path:str, sheet_map_path:Optional[int], root_pos_path:Optional[str], delta_pos_path:Optional[str]):
   assert os.path.exists(in_path), f"Could not find in_path {in_path}"
   assert os.path.exists(os.path.dirname(os.path.realpath(save_path))), f"Could not find containing folder for save_path {save_path}"

   delta_pos: List[List[Tuple[int,int]]] = []
   if root_pos_path is not None or delta_pos_path is not None:
      assert root_pos_path is not None and delta_pos_path is not None, f"Both root_pos and delta_pos need to be set or not, cannot have 1 without the other"
      assert os.path.isfile(root_pos_path), f"Could not find root_pos file at {root_pos_path}"
      assert os.path.isdir(os.path.dirname(os.path.realpath(delta_pos_path))), f"Could not find parent directory of root_pos filepath {root_pos_path}"
      with open(root_pos_path, "r") as f:
         root_pos = json.load(f)
         assert isinstance(root_pos, dict)

   orig_filenames = [f for f in os.listdir(in_path) if f.endswith(".png")]
   if sheet_map_path is not None:
      assert os.path.exists(sheet_map_path), f"A sheet_map path was provided but could not find file at {sheet_map_path}"
      with open(sheet_map_path, "r") as f:
         sheet_map = json.load(f)
      assert isinstance(sheet_map, list), f"Sheet map must be a list, got {type(sheet_map).__name__}"
      for pattern in sheet_map:
         assert isinstance(pattern, str), f"Sheet map must only contain str elements, found '{pattern}' of type {type(pattern).__name__}"
   else:
      sheet_map = [""]
   filename_to_pattern = { f: map_filename(f, sheet_map) for f in orig_filenames }
   found_patternes = set()
   for filename in orig_filenames:
      value = filename_to_pattern[filename]
      if value is None:
         print(f"WARNING: Could not find mapping for filename {filename}, skipping")
         filename_to_pattern.pop(filename)
      else:
         found_patternes.add(value)
   assert len(found_patternes) > 0, f"Found none of the patternes, have no images to process"
   if len(found_patternes) < len(sheet_map):
      print(f"WARNING: Missing entries from the following patternes {list(set(sheet_map).difference(found_patternes))}")

   filename_to_image = { f: cv2.imread(os.path.join(in_path, f), cv2.IMREAD_UNCHANGED) for f in filename_to_pattern.keys() }
   images = list(filename_to_image.values())
   assert len(images) > 0, "Found 0 *.png files at the in_path"
   assert all(len(images[0].shape) == len(im.shape) and images[0].shape == im.shape for im in images[1:]), "Images were not all the same size"

   IMG_H, IMG_W = images[0].shape[:2]

   row_count = len(found_patternes)
   row_size  = max(sum(1 if found_pattern == check_pattern else 0 for found_pattern in filename_to_pattern.values()) for check_pattern in found_patternes)

   sheet = np.zeros((IMG_H*row_count, IMG_W*row_size, images[0].shape[2]))
   print(sheet.shape)
   y = 0
   for pattern in sheet_map:
      if pattern not in found_patternes:
         continue
      if delta_pos_path is not None:
         delta_pos.append([])
      filenames = sorted(list(f for f,p in filename_to_pattern.items() if p == pattern))
      x = 0
      for filename in filenames:
         if delta_pos_path is not None:
            assert filename in root_pos, f"Could not find filename {filename} in root_pos dict"
            delta_pos[-1].append(root_pos[filename])
         sheet[y*IMG_H:(y+1)*IMG_H, x*IMG_W:(x+1)*IMG_W] = filename_to_image[filename]
         x += 1
      y += 1

   cv2.imwrite(save_path, sheet)
   if delta_pos_path is not None:
      with open(delta_pos_path, "w") as f:
         json.dump(delta_pos, f)

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--in-path',   type=str, required=True, help="Path to folder containing the images to package into a spritesheet")
   parser.add_argument('--save-path', type=str, required=True, help="Path to save the spritesheet at")
   parser.add_argument('--sheet-map', type=str, help="Path to a json file defining which filename patterns go in rows together")
   parser.add_argument('--root-pos',  type=str, help="Path to a json file describing the root position of each filename")
   parser.add_argument('--delta-pos', type=str, help="Path to save a root delta json file, requires root pos being set")
   args = parser.parse_args()

   spritesheet(args.in_path, args.save_path, args.sheet_map, args.root_pos, args.delta_pos)
