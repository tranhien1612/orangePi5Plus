#!/usr/bin/env python3
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib 

Gst.init(None)

server = GstRtspServer.RTSPServer.new()
server.set_service("8554")

#,height=1088 
#gst-launch-1.0 v4l2src device=/dev/video11 num-buffers=100 ! video/x-raw,format=NV12,width=1920,height=1088,framerate=30/1 ! videoconvert ! mpph264enc ! h264parse ! mp4mux ! filesink location=h264.mp4
factory = GstRtspServer.RTSPMediaFactory.new()
factory.set_launch("v4l2src device=/dev/video12 ! video/x-raw ! mpph264enc tune=zerolatency speed-preset=ultrafast ! rtph264pay name=pay0 pt=96")

mounts = server.get_mount_points()
mounts.add_factory("/stream", factory)

server.attach(None)

loop = GLib.MainLoop()
print("Enter URL: rtsp://localhost:8554/stream")
loop.run()
