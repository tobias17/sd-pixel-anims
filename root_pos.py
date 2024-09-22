import os, cv2, argparse, json
import numpy as np

def root_pos(in_path:str, save_path:str):
   assert os.path.isdir(in_path), f"Expected to find folder at in_path {in_path}"
   assert os.path.isdir(os.path.dirname(save_path)), f"Failed to find parent directory of save_path {save_path}"

   data = {}
   for filename in os.listdir(in_path):
      if not filename.endswith(".png"):
         continue
      bgra = cv2.imread(os.path.join(in_path, filename), cv2.IMREAD_UNCHANGED)
      alpha = bgra[:,:,3]

      indeces = np.where(alpha > 127) # type: ignore
      y, x = [int(np.median(indeces[i])) for i in range(2)]
      data[filename] = [x, y]

   with open(save_path, "w") as f:
      json.dump(data, f)

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--in-path',   type=str, required=True, help="Path to folder containing the root images")
   parser.add_argument('--save-path',  type=str, required=True, help="Path to where to store the json contents at")
   args = parser.parse_args()

   root_pos(args.in_path, args.save_path)
