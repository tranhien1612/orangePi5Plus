import os, subprocess, time, threading
from pathlib import Path

rawFolder = Path("/home/orangepi/src/output/raw")
imageFolder = Path("/home/orangepi/src/output/images")
videoFolder = Path("/home/orangepi/src/output/videos")

def convert_image_file(fileName):
    try:
        command = "convert -size 4224x3136 -depth 32 uyvy:{0}/{2}.raw {1}/{2}.png".format(rawFolder, imageFolder, fileName)
        result = subprocess.run(
            command,
            shell=True, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE 
        )
        print("------------------ Convert Image Done! ------------------")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}:")
        print(e.stderr)

def convert_video_file(fileName):
    try:
        command = "ffmpeg -f rawvideo -pix_fmt nv12 -s 1920x1088 -r 15 -i {0}/{2}.yuv -c:v libx264 {1}/{2}.mp4".format(rawFolder, videoFolder, fileName)
        result = subprocess.run(
            command,
            shell=True, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE 
        )
        print("------------------ Convert Video Done! ------------------")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}:")
        print(e.stderr)

def list_files_in_folder(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder {folder_path} does not exist.")
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def get_fileName(rawFolder, imageFolder, videoFolder):
    rawFiles = list_files_in_folder(rawFolder)
    imageFiles = list_files_in_folder(imageFolder)
    videoFiles = list_files_in_folder(videoFolder)

    rawList = []
    imageList = []
    videoList = []

    for file in zip(rawFiles):
        rawList.append(file)
    for file in zip(imageFiles):
        imageList.append(file)
    for file in zip(videoFiles):
        videoList.append(file)
    return rawList, imageList, videoList

def convert_handle(rawList, imageList, videoList):
    rawImageList = []
    rawVideoList = []
    imageNameList = []
    videoNameList = []

    for file in imageList:
        filename = file[0]
        base_name, extension = os.path.splitext(filename)
        if(extension == ".png"):
            imageNameList.append(base_name)
    
    for file in videoList:
        filename = file[0]
        base_name, extension = os.path.splitext(filename)
        if(extension == ".mp4"):
            videoNameList.append(base_name)

    for file in rawList:
        filename = file[0]
        base_name, extension = os.path.splitext(filename)
        if(extension == ".raw"):
            if(not base_name in imageNameList):
                # rawImageList.append(base_name)
                convert_image_file(base_name)
        elif (extension == ".yuv"):
            if(not base_name in videoNameList):
                # rawVideoList.append(base_name)
                convert_video_file(base_name)
    
def main():
    rawList = []
    imageList = []
    videoList = []
    try:
        rawList, imageList, videoList = get_fileName(rawFolder, imageFolder, videoFolder)
        convert_handle(rawList, imageList, videoList)

    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()