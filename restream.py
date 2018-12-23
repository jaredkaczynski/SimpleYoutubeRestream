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


def startStatic(streamkey):
    global ffmpegPID
    command = '''ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -fflags +genpts  -f lavfi -i "movie=loading.flv:loop=0, setpts=N/(FRAME_RATE*TB)" -s 1280x720 -f flv -c:v libx264 -preset ultrafast -preset ultrafast -b:v 1200k -maxrate 1500k -bufsize 600k -framerate 30 -r 30 -ar 44100 -g 48 rtmp://x.rtmp.youtube.com/live2/''' + streamkey
    print(SCRIPT_ROOT)
    ffmpegPID = subprocess.Popen(command, cwd=SCRIPT_ROOT, shell=True)


def startStream(camera, key):
    global ffmpegPID
    ffmpegPID = subprocess.Popen(
        '''ffmpeg -re -i ''' + camera + ''' -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -c:a libmp3lame -ab 128k -ar 44100 -c:v copy -threads 2 -bufsize 512k -f flv "rtmp://a.rtmp.youtube.com/live2/"''' + key,
        cwd=SCRIPT_ROOT, shell=True)
    print(ffmpegPID.pid)
    while check_pid(ffmpegPID.pid):
        time.sleep(1)


def checkStream(stream):
    r = requests.get(stream, verify=False)
    if r.status_code == 404:
        return False
    else:
        return True


def killStatic():
    global ffmpegPID
    """ Check For the existence of a unix pid. """
    try:
        os.kill(ffmpegPID.pid, 9)
    except OSError:
        return False
    else:
        return True


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        print("OS Error")
        return False
    else:
        print("Still Running")
        return True

def exit_handler():
    killStatic()

def main():
    cameraUrl = sys.argv[1]
    streamkey = sys.argv[2]
    while (True):
        if checkStream(cameraUrl):
            thr = threading.Thread(target=startStream, args=(cameraUrl, streamkey), kwargs={})
            thr.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
            thr.start()
            thr.join()
        else:
            startStatic(streamkey)
            while not checkStream(cameraUrl):
                print("Still Offline")
                time.sleep(5)
            killStatic()

atexit.register(exit_handler)
main()
