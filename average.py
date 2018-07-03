import os, argparse, rawpy, struct, multiprocessing
from PIL import Image
import numpy as np 

num_cores = multiprocessing.cpu_count()

parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, default="/home/xuanerzh/Downloads/burst/",
                    required=True, help="root folder that contains the images")
parser.add_argument("--type", type=str, choices=["rgb", "raw"], default="rgb")
ARGS = parser.parse_args()
print(ARGS)

save_path = ARGS.path + "processed/"
if not os.path.exists(save_path):
    os.mkdir(save_path)

def avg_rgb(imlist, path):
    w,h=Image.open(path+imlist[0]).size
    N=len(imlist)

    # Create a numpy array of floats to store the average (assume RGB images)
    arr=np.zeros((h,w,3),np.float)

    # Build up average pixel intensities, casting each image as an array of floats
    for i,im in enumerate(imlist):
        file = path+im
        print("Processing of %d/%d file: %s"%(i,N,file))
        imarr=np.array(Image.open(path+im),dtype=np.float)
        arr=arr+imarr/N

    # Round values in array and cast as 8-bit integer
    arr=np.array(np.round(arr),dtype=np.uint8)

    # Generate, save and preview final image
    out=Image.fromarray(arr,mode="RGB")
    return out

def avg_raw(imlist, path, num_cores=1):
    N=len(imlist)
    arr=0
    output = rawpy.imread(path+imlist[0])
    for i,im in enumerate(imlist):
        file = path+im
        print("Processing of %d/%d file: %s"%(i+1,N,file))
        raw = rawpy.imread(file)
        imarr = raw.raw_image_visible.astype(np.float32)
        arr = arr+imarr/N
    
    w,h = arr.shape
    for i in range(w):
        for j in range(h):
            output.raw_image_visible[i, j] = arr[i, j]
    out = output.postprocess(use_camera_wb=True, no_auto_bright=True)
    return out

allfiles=os.listdir(ARGS.path)
if ARGS.type == "rgb":
    imlist = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG",".png",".PNG"]]
    out = avg_rgb(imlist, ARGS.path)
else:
    imlist=[filename for filename in allfiles if filename[-4:] in [".ARW", ".CR2"]]
    out = avg_raw(imlist, ARGS.path)

out = Image.fromarray(np.uint8(out))
out.save(save_path + ARGS.type + "_avg.png")