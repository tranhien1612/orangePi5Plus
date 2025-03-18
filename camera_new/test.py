import cv2
import gi
import numpy as np

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib 

# Initialize GStreamer
Gst.init(None)

# Callback function to push frames into the pipeline
def on_need_data(appsrc, length):
    global cap
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame from camera")
        return

    # Convert the frame to RGB format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the frame to a GStreamer buffer
    height, width = frame.shape[:2]
    frame_buffer = frame.tobytes()
    buf = Gst.Buffer.new_allocate(None, len(frame_buffer), None)
    buf.fill(0, frame_buffer)

    # Set metadata for the buffer
    buf.duration = Gst.CLOCK_TIME_NONE
    buf.pts = buf.dts = int(Gst.util_uint64_scale(cap.get(cv2.CAP_PROP_POS_MSEC), Gst.SECOND, 1000))
    buf.offset = Gst.BUFFER_OFFSET_NONE

    # Push the buffer into the pipeline
    retval = appsrc.emit('push-buffer', buf)
    if retval != Gst.FlowReturn.OK:
        print(f"Error pushing buffer: {retval}")

# Create the RTSP server
class MyFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **kwargs):
        super(MyFactory, self).__init__(**kwargs)

    def do_create_element(self, url):
        # Define the GStreamer pipeline
        pipeline_str = (
            f"appsrc name=source is-live=true block=true format=GST_FORMAT_TIME caps=video/x-raw,format=RGB,width={width},height={height},framerate=30/1 ! "
            "videoconvert ! "
            "x264enc tune=zerolatency ! "
            "rtph264pay name=pay0 pt=96"
        )
        return Gst.parse_launch(pipeline_str)


# Main loop
if __name__ == "__main__":
    cap = cv2.VideoCapture("/dev/video11")
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    
    # server = GstServer()
    server = GstRtspServer.RTSPServer.new()
    server.set_service("8554")  # RTSP port

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch("appsrc name=source is-live=true block=true ! videoconvert ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96")

    mounts = server.get_mount_points()
    mounts.add_factory("/stream", factory)

    server.attach(None)


    # Start the GStreamer main loop
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        pass

    # Release resources
    cap.release()