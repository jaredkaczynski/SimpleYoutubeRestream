import signal
import subprocess
import sys
import requests
import os
import time
import threading
import atexit

ffmpegPID = 0
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
stop = []


def startStatic(streamkey):
    global ffmpegPID
    print(SCRIPT_ROOT)
    ffmpegPID = subprocess.Popen(
        ["ffmpeg", "-re", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-r", "10", "-loop", "1", "-i", "error.png",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast", "-g", "20", "-b:v", "2500k", "-c:a", "aac",
         "-ar", "44100", "-threads", "0", "-bufsize", "512k", "-strict", "experimental", "-f", "flv",
         "rtmp://a.rtmp.youtube.com/live2/" + streamkey], cwd=SCRIPT_ROOT)


def startStream(camera, key, stop):
    global ffmpegPID
    ffmpegPID = subprocess.Popen(
        ["ffmpeg", "-re", "-i", camera, "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-c:a",
         "libmp3lame", "-ab", "128k", "-ar", "44100", "-c:v", "copy", "-threads", "2", "-bufsize", "512k", "-f", "flv",
         "rtmp://a.rtmp.youtube.com/live2/" + key, "-abort_on", "empty_output", "-xerror"], cwd=SCRIPT_ROOT)
    print(ffmpegPID.pid)
    while check_pid(ffmpegPID) and not stop:
        print("Checking running status")
        time.sleep(5)
        if not checkStream(camera):
            killffmpeg()
            return



def checkStream(stream):
    r = requests.get(stream, verify=False)
    if r.status_code == 404:
        return False
    else:
        return True


def killffmpeg():
    global ffmpegPID
    ffmpegPID.terminate()
    time.sleep(1)


def check_pid(p):
    poll = p.poll()
    if poll == None:
        return True
    else:
        return False


def exit_handler():
    stop.append(True)
    killffmpeg()


def main():
    global stop
    cameraUrl = sys.argv[1]
    streamkey = sys.argv[2]
    while (True):
        if checkStream(cameraUrl):
            thr = threading.Thread(target=startStream, args=(cameraUrl, streamkey, stop), kwargs={})
            thr.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
            thr.start()
            thr.join()
        else:
            startStatic(streamkey)
            while not checkStream(cameraUrl):
                print("Still Offline")
                time.sleep(5)
            killffmpeg()


atexit.register(exit_handler)
main()
