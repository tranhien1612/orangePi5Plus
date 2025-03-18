#!/usr/bin/env python3
import os, subprocess, time, threading, gi, socket, signal, cv2
from pathlib import Path
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib 

def create_folder():
    imageFolder = Path("/home/orangepi/src/output/images")
    videoFolder = Path("/home/orangepi/src/output/videos")
    rawFolder = Path("/home/orangepi/src/output/raw")
    if not imageFolder.exists():
        imageFolder.mkdir(parents=True, exist_ok=True)

    if not videoFolder.exists():
        videoFolder.mkdir(parents=True, exist_ok=True)
    
    if not rawFolder.exists():
        rawFolder.mkdir(parents=True, exist_ok=True)

subprocess_pid = 0
def command_handle(*args):
    command = ["bash" ,  "/home/orangepi/src/camera/camera.sh"] + list(args)
    
    result = subprocess.Popen(
        command,
        text=True,             # Ensures the output is returned as a string
        stdout=subprocess.PIPE,  # Capture standard output
        stderr=subprocess.PIPE   # Capture standard error
    )
    # print(result.stdout)

    global subprocess_pid
    if( args[0] == "start"):
        subprocess_pid = result.pid
        print(f"Recording subprocess pid: {subprocess_pid}")

'''
def camera_handle(tcpServer):
    global subprocess_pid
    try:
        while True:
            photoFlag, recordFlag, receivedFlag = tcpServer.get_status()
            print(f"{photoFlag}, {recordFlag}, {receivedFlag}")
            while(receivedFlag):
                if(photoFlag == True):
                    tcpServer.photoFlag(False)
                    # photoFlag = False
                    print("------------------ Start Photo! ------------------")
                    command_handle("photo")
                elif (recordFlag == True and subprocess_pid == 0):
                    print("------------------ Start Video! ------------------")
                    command_handle("start")
                elif (recordFlag == False and subprocess_pid != 0):
                    print("------------------ Stop Video! ------------------")
                    os.kill(subprocess_pid, signal.SIGKILL)
                    subprocess_pid = 0
                receivedFlag = False

    except Exception as e:
        print(f"Error {e}")

def message_handle(msg):
    global photoFlag, recordFlag, receivedFlag
    receivedFlag = True
    if(msg == '01'):
        photoFlag = True
    elif (msg == '02'):
        recordFlag = True
    elif (msg == '03'):
        recordFlag = False

def handle_client(client_socket, client_address):
    print(f"Connected to {client_address}") 
    try:
        while True:
            data = client_socket.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break  
            hex_data = data.hex()
            print(f"Received from {client_address}: Raw Bytes={data}, Hex={hex_data}")
            message_handle(hex_data)
            # Send a response back to the client
            # response = f"Echo: {data.decode('utf-8')}"
            # client_socket.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        print(f"Closing connection with {client_address}")
        client_socket.close()

def tcp_server_init(host='127.0.0.1', port=10001):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server is listening on {host}:{port}...")
        while True:
            client_socket, client_address = server_socket.accept()
            
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.start()

def rtsp_handle():
    try:
        Gst.init(None)
        server = GstRtspServer.RTSPServer.new()
        server.set_service("8554")

        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch("v4l2src device=/dev/video12 ! video/x-raw,height=1088 ! mpph264enc tune=zerolatency speed-preset=ultrafast ! rtph264pay name=pay0 pt=96")

        mounts = server.get_mount_points()
        mounts.add_factory("/stream", factory)

        server.attach(None)
        loop = GLib.MainLoop()
        print("Enter URL: rtsp://localhost:8554/stream")
        loop.run()
            
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}:")
        print(e.stderr)
'''

class RTSPServer:
    def __init__(self, device="/dev/video12", width=1920, height=1088):
        self.device = device
        self.width = width
        self.height = height

    def run(self):
        self.rtspThread = threading.Thread(target=self.main)
        self.rtspThread.start()

    def stop(self):
        if self.loop:
            self.loop.quit()
        self.rtspThread.join()

    def main(self):
        try:
            Gst.init(None)
            server = GstRtspServer.RTSPServer.new()
            server.set_service("8554")

            factory = GstRtspServer.RTSPMediaFactory.new()
            factory.set_launch(f"v4l2src device={self.device} ! video/x-raw,height=1088 ! mpph264enc tune=zerolatency speed-preset=ultrafast ! rtph264pay name=pay0 pt=96")

            mounts = server.get_mount_points()
            mounts.add_factory("/stream", factory)

            server.attach(None)
            self.loop = GLib.MainLoop()
            print(f"Device: {self.device} -----> URL: rtsp://localhost:8554/stream")
            self.loop.run()
                
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}:")
            print(e.stderr)
        
class TCPServer():
    def __init__(self, host="127.0.0.1", port=10001):
        self.host = host
        self.port = port
        self.photoFlag = False
        self.recordFlag = False 
        self.receivedFlag = False

    def run(self):
        cameraThread = threading.Thread(target=self.camera_handle)
        cameraThread.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Server is listening on {self.host}:{self.port}...")
            while True:
                client_socket, client_address = server_socket.accept()
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.start()

    def handle_client(self, client_socket, client_address):
        print(f"Connected to {client_address}") 
        try:
            while True:
                data = client_socket.recv(1024)  # Receive up to 1024 bytes
                if not data:
                    break  
                hex_data = data.hex()
                print(f"Received from {client_address}: Raw Bytes={data}, Hex={hex_data}")
                
                self.receivedFlag = True
                if(hex_data == '01'):
                    self.photoFlag = True
                elif (hex_data == '02'):
                    self.recordFlag = True
                elif (hex_data == '03'):
                    self.recordFlag = False

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            print(f"Closing connection with {client_address}")
            client_socket.close()
    
    def camera_handle(self):
        global subprocess_pid
        try:
            while True:
                while(self.receivedFlag):
                    if(self.photoFlag == True):
                        self.photoFlag = False
                        print("------------------ Start Photo! ------------------")
                        command_handle("photo")
                    elif (self.recordFlag == True and subprocess_pid == 0):
                        print("------------------ Start Video! ------------------")
                        command_handle("start")
                    elif (self.recordFlag == False and subprocess_pid != 0):
                        print("------------------ Stop Video!  ------------------")
                        os.kill(subprocess_pid, signal.SIGKILL)
                        subprocess_pid = 0
                    self.receivedFlag = False

        except Exception as e:
            print(f"Error {e}")

if __name__ == "__main__":
    create_folder()

    rtspServer = RTSPServer("/dev/video12")
    tcpServer = TCPServer("127.0.0.1", 10001)
    
    rtspServer.run()
    tcpServer.run()


    # rtspThread = threading.Thread(target=rtsp_handle)
    # rtspThread.start()

    # cameraThread = threading.Thread(target=camera_handle, args=(tcpServer))
    # cameraThread.start()

    # captureThread = threading.Thread(target=capture_camera)
    # captureThread.start()

    # tcp_server_init()
    
