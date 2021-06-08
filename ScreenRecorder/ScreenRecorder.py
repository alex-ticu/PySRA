from typing_extensions import runtime
from .ScreenAudioRecorder import ScreenAudioRecorderThreaded
from .ScreenVideoRecorder import ScreenVideoRecorderThreaded
import logging
from pathlib import Path
import pyautogui
import cv2
from threading import Thread
from time import time
import queue
import wave
import pyaudio as pa
import numpy as np
import struct
import sys


class ScreenRecorder():

    def __init__(self, videoSavePath, audioSavePath, runTime=60, fps=20, quitKey='q', videoThreads=8, outputDevice=None, loggingLevel=logging.DEBUG, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        # Init logging
        self.logger = logging.getLogger('ScreenRecorder')
        self.logger.setLevel(loggingLevel)

        ch = logging.StreamHandler()
        ch.setLevel(loggingLevel)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        # Done

        self.chunk = 1024
        self.format = pa.paInt16
        self.channels = 2
        self.sampleRate = 44100

        if len(quitKey) != 1:
            self.logger.warning("Quitkey default to q!")
            self.quitKey = 'q'

        else:
            self.quitKey = quitKey

        self.shouldStop = False
        # Get screen resolution
        self.screenSize = pyautogui.size()

        if fps <= 0:
            self.logger.error("fps should be greater than 0!")
            self.logger.warning("Defaulting fps to 20.")
            self.fps = 20
        else:
            self.fps = fps

        if runTime <= 0 or runTime > 120:
            self.logger.error("runTime should be between 0 and 120!")
            self.logger.warning("Defaulting runTime to 60.")
            self.runtime = 60
        else:
            self.runTime = runTime

        # Path for video file
        if not Path(videoSavePath).suffixes:
            # No file name was given...
            self.videoSavePath = Path(videoSavePath)
            self.videoSaveName = "videoOutput.avi"

        elif Path(videoSavePath).suffix != '.avi':
            # File extension is not .avi.
            self.logger.warning("Replacing file suffix with .avi!")
            self.videoSavePath = Path(videoSavePath).parent
            self.videoSaveName = Path(videoSavePath).with_suffix('.avi').name
        
        else:
            # Default.
            self.videoSavePath = Path(videoSavePath).parent
            self.videoSaveName = Path(videoSavePath).name
        self.logger.warning("Saving video to: {0}/{1}".format(str(self.videoSavePath), self.videoSaveName))

        # Path for audio file
        if not Path(audioSavePath).suffixes:
            # No file name was given...
            self.audioSavePath = Path(audioSavePath)
            self.audioSaveName = "audioOutput.avi"

        elif Path(audioSavePath).suffix != '.wav':
            # File extension is not .avi.
            self.logger.warning("Replacing file suffix with .wav!")
            self.audioSavePath = Path(audioSavePath).parent
            self.audioSaveName = Path(audioSavePath).with_suffix('.wav').name
        
        else:
            # Default.
            self.audioSavePath = Path(audioSavePath).parent
            self.audioSaveName = Path(audioSavePath).name
        self.logger.warning("Saving audio to: {0}/{1}".format(str(self.audioSavePath), self.audioSaveName))

        # Check if files are different.
        if self.videoSaveName == self.audioSaveName:

            self.logger.warning("Video file and audio file have the same names! Using default names.")
            self.audioSaveName = "audioOutput.wav"
            self.videoSaveName = "videoOutput.avi"
            
        if videoThreads < 0 or videoThreads > 8:
            self.logger.warning("Using 4 video threads.")
            self.videoThreadsN = 4

        else:
            self.videoThreadsN = videoThreads
            self.logger.debug("Using {0} video threads.".format(self.videoThreadsN))

        self.fourcc = cv2.VideoWriter_fourcc(*"XVID") # same as calling with "X","V","I","D"


    def removeScreenshots(self):
        # Remove .screenshot* files left behind by pyautogui.screenshot()
        toRemove =  [screenshot for screenshot in Path('.').glob('.screenshot*') if screenshot.is_file()]
        for screenshot in toRemove:
            try:
                screenshot.unlink()
                #self.logger.debug("Removed {0}".format(screenshot))
            except:
                #self.logger.exception("Failed to remove {0}".format(screenshot))
                pass


    def recordVideo(self, path):

        # Initialize video writer. The video file will be numFrames / fps seconds long, but the frames are not synced on the time axis, so the video will be either slowed down or speed up.
        writer = cv2.VideoWriter(str(path), self.fourcc, self.fps, self.screenSize)

        for i in range(self.videoThreadsN):
            worker = ScreenVideoRecorderThreaded(runTime=self.runTime, fps=self.fps, loggingLevel=logging.DEBUG)
            #worker.daemon = True
            worker.start()

        frameQueue = worker.getFrameQueue()

        for i in range(self.runTime * self.fps):
            # Try to get frames from the queue
            try:
                frame = frameQueue.get(block=True, timeout=60)

            except queue.Empty as e:
                # If the threads stopped sending frames.
                self.logger.error("Can't receive video frames!")
                break

            writer.write(frame)
            frameQueue.task_done()

            cv2.imshow(self.videoSaveName, frame)
            
            if cv2.waitKey(1) == ord(self.quitKey):
                self.shouldStop = True
                worker.stop()
                break
        
        writer.release()
        self.removeScreenshots()


    def analyzeAudio(self, frame):

        # Frame is a number of bytes numbers of bytes.
        # Two channels.
        count = len(frame)/2
        # $d - signed integer (count) "h" stands for short integer in format.
        # (count) number of shorts.
        format = "%dh"%(count)
        # get short values.
        shorts = struct.unpack(format, frame)
        #frame = int.from_bytes(frame, byteorder=sys.byteorder, signed=False)

        db = 20*np.log10(np.sqrt(np.mean(np.absolute(shorts)**2)))

        return db


    def recordAudio(self, path):

        analyzerFile = open(str(path.parent / "analyzer.txt"), "w")

        # One thread is enough for audio recording.
        worker = ScreenAudioRecorderThreaded(runTime=self.runTime)
        worker.start()

        wf = wave.open(str(path), "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(worker.getSampleWidth())
        wf.setframerate(self.sampleRate)

        frameQueue = worker.getFrameQueue()

        frames = []

        for i in range(int(self.sampleRate / self.chunk * self.runTime)):
            
            try:
                frame = frameQueue.get(block=True, timeout=60)
            except queue.Empty as e:
                # If the threads stopped sending frames.
                self.logger.error("Can't receive audio frames!")
                break
            
            db = self.analyzeAudio(frame)
            analyzerFile.write(str(db) + "\n")

            frames.append(frame)
            frameQueue.task_done()

            if self.shouldStop:
                worker.stop()
                break

        wf.writeframes(b"".join(frames))
        
        wf.close()



    def record(self):

        # Create video directory if it doesn't exist.
        if not self.videoSavePath.is_dir():
            self.logger.debug("Creating {0}/".format(str(self.videoSavePath)))
            try:
                Path.mkdir(self.videoSavePath)
            except PermissionError:
                self.logger.error("Cannot create {0}".format(str(self.videoSavePath)))
                return

        videoPath = self.videoSavePath / Path(self.videoSaveName)

        if videoPath.is_file():
            try:
                videoPath.unlink()
            except PermissionError:
                self.logger.error("Cannot remove {} (Permission denied)".format(videoPath))
                return

        # Create audio directory if it doesn't exist.
        if not self.audioSavePath.is_dir():
            self.logger.debug("Creating {0}/".format(str(self.audioSavePath)))
            try:
                Path.mkdir(self.audioSavePath)
            except PermissionError:
                self.logger.error("Cannot create {0}".format(str(self.audioSavePath)))
                return

        audioPath = self.audioSavePath / Path(self.audioSaveName)
        
        if audioPath.is_file():
            try:
                audioPath.unlink()
            except PermissionError:
                self.logger.error("Cannot remove {} (Permission denied)".format(audioPath))
                return

        # TODO: Need to sync the starting of audio and video recording.
        # Audio recording takes longer to initialize due to the AudioPort initialization.

        self.logger.debug("Starting recording video: {0}".format(videoPath))

        videoWorker = Thread(target=self.recordVideo, args=(videoPath,))
        videoWorker.daemon = True
        videoWorker.start()

        self.logger.debug("Starting recording audio: {0}".format(audioPath))

        audioWorker = Thread(target=self.recordAudio, args=(audioPath, ))
        audioWorker.daemon = True
        audioWorker.start()

        # Wait for video recording.
        videoWorker.join()
        self.logger.debug("Video recording ended.")

        # # Wait for audio recording.
        audioWorker.join()
        self.logger.debug("Audio recording ended.")



# rec = ScreenRecorder(videoSavePath="asdf/video.avi", audioSavePath="asdf/audio.avi" , runTime=20, fps=20)
# rec.record()