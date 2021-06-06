import threading
from Xlib.protocol.display import Screen
import cv2
import numpy as np
import pyautogui
import logging
from threading import Thread
from threading import Lock
from queue import Queue
from time import sleep
from time import time

class ScreenVideoRecorderThreaded(Thread):

    # Init frame queue shared by all threads.
    frameQueue = Queue()
    lock = Lock()
    shouldStop = False
    frameCount = 0
    workingThreads = []

    def __init__(self, runTime=60, fps=20, loggingLevel=logging.DEBUG, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        
        super().__init__()

        # Init logging
        self.logger = logging.getLogger('ScreenVideoRecorder - {}'.format(self.name))
        self.logger.setLevel(loggingLevel)

        ch = logging.StreamHandler()
        ch.setLevel(loggingLevel)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        # Done

        #self.quitKey = quitKey

        # Check runTime [1, 120] in seconds
        if runTime <= 0 or runTime > 120:
            self.logger.error("runTime should be between 0 and 120!")
            self.logger.warning("Defaulting runTime to 60.")
            self.runtime = 60
        else:
            self.runTime = runTime

        if fps <= 0:
            self.logger.error("fps should be greater than 0!")
            self.logger.warning("Defaulting fps to 20.")
            self.fps = 20
        else:
            self.fps = fps


    def getFrameQueue(self):
        return ScreenVideoRecorderThreaded.frameQueue


    def stop(self):
        ScreenVideoRecorderThreaded.shouldStop = True


    def run(self):
        # TODO: Find method to sync frames on the time axis based on fps.
        # Take screenshots of the screen and put them in frameQueue.

        # If multiple threads are working on creating frames, then the frame count will overshoot by how many threads are working.
        ScreenVideoRecorderThreaded.workingThreads.append(threading.get_ident())

        # Run the thread while the frame count is smaller than the thread's specs.
        while ScreenVideoRecorderThreaded.frameCount <= (self.runTime * self.fps - len(ScreenVideoRecorderThreaded.workingThreads)):

            # Threads wait for eachother when taking screenshots?
            #with ScreenVideoRecorderThreaded.lock:
            try:
                screenShot = pyautogui.screenshot()
            except FileNotFoundError as f:
                # If ctrl+c is used to stop the script, then some screenshot artifacts are left behind.
                # I remove these in another thread, so this exception might be thrown (if no ctrl+c is given).
                pass

            # Take screenshot and convert it to np array
            frame = np.array(screenShot)

            # Convert color space.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Put the frame in the queue.
            ScreenVideoRecorderThreaded.frameQueue.put(frame)

            ScreenVideoRecorderThreaded.frameCount += 1
            # self.logger.debug(ScreenVideoRecorderThreaded.frameCount)
            if ScreenVideoRecorderThreaded.shouldStop:
                #self.logger.debug("Stopping...")
                break
        
        # Remove threads from the list.
        ScreenVideoRecorderThreaded.workingThreads.remove(threading.get_ident())

        return 

    

# if __name__ == '__main__':
    
#     t = ScreenVideoRecorderThreaded(runTime=20, fps=60)
#     t.start()

#     t2 = ScreenVideoRecorderThreaded(runTime=20, fps=60)
#     t2.start()

#     # while True:

#     sleep(3)

#     print("t1")
#     print(t.getFrameQueue().qsize())
#     print("t2")
#     print(t2.getFrameQueue().qsize())

#     while not t.getFrameQueue().empty():
#         print("t1")
#         print(t.getFrameQueue().qsize())
#         print("t2")
#         print(t2.getFrameQueue().qsize())
#         frame = t.getFrameQueue().get()
#         cv2.imshow("frame", frame)
#         if cv2.waitKey(0) == ord("q"):
#             print("STOPPED!")
#             t.stop()
#             break




