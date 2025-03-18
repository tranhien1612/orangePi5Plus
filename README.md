# orangePi5Plus

## Install OS
Download image form [Orange Pi website](http://www.orangepi.org/orangepiwiki/index.php/Images_Download). 

Ex: Download [```OrangePi5Plus_1.2.0_ubuntu_focal_desktop_xfce_linux5.10.160```](https://drive.google.com/drive/folders/1wOmKUla8CwUPTfxvfCGutj8lbMZFtFCm)

Uncompress and boot it into SDCard

## Start
ssh to orangepi5plus ip with user: ```orangepi```, pass: ```orangepi```

open `orangepi-config` to enable ov13855 camera. Chosse `System` -> `Hardware` -> Tick ```opi5plus-ov13855```. Save and reboot.
```
sudo orangepi-config
```

## Check

Check the device of camera:
```
ls -l /dev/video*
grep '' /sys/class/video4linux/video*/name
grep ov13855 /sys/class/video4linux/v*/name

media-ctl -d /dev/media0 -p
media-ctl -d /dev/media1 -p

v4l2-ctl -d /dev/video11 --list-formats-ext
v4l2-ctl --device=/dev/video0 --all
```
Install libs: 
```
sudo apt-get install imagemagick #for convert format
sudo apt install gstreamer1.0-rtsp && sudo apt install python3-gst-1.0 && sudo apt install gir1.2-gst-rtsp-server-1.0 #for stream via rtsp
```

Take picture:
```
v4l2-ctl --device /dev/video11 --set-fmt-video=width=4224,height=3136,pixelformat=UYVY --stream-mmap --stream-count=1 --stream-to=frame.raw
v4l2-ctl --device /dev/video11 --set-fmt-video=pixelformat=UYVY --stream-mmap --stream-count=1 --stream-to=frame.raw
convert -size 4224x3136 -depth 32 uyvy:frame.raw frame.png

gst-launch-1.0 -v v4l2src device=/dev/video11 num-buffers=1 ! video/x-raw,format=NV12,width=4224,height=3136 ! mppjpegenc ! multifilesink location=test%d.jpg
```

Get video:
```
v4l2-ctl -d /dev/video12 --set-fmt-video=width=1920,height=1088,pixelformat=NV12 --stream-mmap=3 --stream-skip=5 --stream-to=video.yuv --stream-count=20
ffmpeg -f rawvideo -pix_fmt nv12 -s 1920x1088 -r 15 -i video.yuv -c:v libx264 output.mp4

gst-launch-1.0 v4l2src device=/dev/video11 num-buffers=10 ! video/x-raw,format=NV12,width=1920,height=1088,framerate=30/1 ! videoconvert ! mpph264enc ! h264parse ! mp4mux ! filesink location=h264.mp4
```
