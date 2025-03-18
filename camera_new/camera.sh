#!/bin/bash

CAMERA_DEVICE="/dev/video11"
PID_FILE="/tmp/camera.pid"

RAW_DIR="/home/orangepi/src/output/raw"
IMAGES_DIR="/home/orangepi/src/output/images"
VIDEO_DIR="/home/orangepi/src/output/videos"

mkdir -p "$RAW_DIR" "$IMAGES_DIR" "$VIDEO_DIR"

#v4l2-ctl --device /dev/video11 --set-fmt-video=width=4224,height=3136,pixelformat=UYVY --stream-mmap --stream-count=5 --stream-to=img.jpg
#v4l2-ctl -d /dev/video11 --set-fmt-video=width=1920,height=1088,pixelformat=NV12 --stream-mmap=3 --stream-skip=5 --stream-to=test.mp4

start_recording() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Recording is already running (PID $(cat $PID_FILE))"
        exit 1
    fi
    
    FILENAME="$RAW_DIR/$(date +%Y%m%d_%H%M%S).yuv"
    v4l2-ctl -d "$CAMERA_DEVICE" --set-fmt-video=width=1920,height=1088,pixelformat=NV12 --stream-mmap=3 --stream-skip=5 --stream-to="$FILENAME" & 
    
    #FILENAME="$VIDEO_DIR/$(date +%Y%m%d_%H%M%S).mp4"
    #gst-launch-1.0 v4l2src device="$CAMERA_DEVICE" ! video/x-raw,format=NV12,width=1920,height=1088,framerate=30/1 ! videoconvert ! mpph264enc ! h264parse ! mp4mux ! filesink location="$FILENAME" &

    echo $! > "$PID_FILE"
    echo "Recording started (PID $!) -> $FILENAME"
}

stop_recording() {
    if [ ! -f "$PID_FILE" ] || ! kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "No recording is active"
        exit 1
    fi

    # Gracefully stop FFmpeg
    kill $(cat "$PID_FILE")
    rm -f "$PID_FILE"
    echo "Recording stopped"
    
    # FILENAME="$OUTPUT_DIR/$(date +%Y%m%d_%H%M%S).mp4"
    # ffmpeg -f rawvideo -pix_fmt nv12 -s 1920x1088 -r 15 -i video.yuv -c:v libx264 "$FILENAME"
}

take_photo(){
    echo "Take photo"
    #FILENAME="$RAW_DIR/$(date +%Y%m%d_%H%M%S).raw"
    #v4l2-ctl --device "$CAMERA_DEVICE" --set-fmt-video=width=4224,height=3136,pixelformat=UYVY --stream-mmap --stream-count=5 --stream-to="$FILENAME"
    #convert -size 4224x3136 -depth 32 uyvy:frame.raw "$FILENAME"

    FILENAME="$IMAGES_DIR/$(date +%Y%m%d_%H%M%S).jpg"
    gst-launch-1.0 -v v4l2src device="$CAMERA_DEVICE" num-buffers=1 ! video/x-raw,format=NV12,width=4224,height=3136 ! mppjpegenc ! multifilesink location="$FILENAME"
}


case "$1" in
    photo)
        take_photo
        ;;
    start)
        start_recording
        ;;
    stop)
        stop_recording
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Recording is active (PID $(cat $PID_FILE))"
        else
            echo "Recording is not active"
        fi
        ;;
    *)
        echo "Usage: $0 {photo|start|stop|status}"
        exit 1
        ;;
esac
