from queue import Queue
import pyaudio as pa
import logging
from threading import Thread
from threading import Lock
from queue import Queue

class ScreenAudioRecorderThreaded(Thread):

    def __init__(self, outputDevice=None, runTime=60, loggingLevel=logging.DEBUG, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        
        super().__init__()

        # Init logging
        self.logger = logging.getLogger('ScreenAudioRecorder - {}'.format(self.name))
        self.logger.setLevel(loggingLevel)

        ch = logging.StreamHandler()
        ch.setLevel(loggingLevel)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        # Done

        # Check runTime [1, 120] in seconds
        if runTime <= 0 or runTime > 120:
            self.logger.error("runTime should be between 0 and 120!")
            self.logger.warning("Defaulting runTime to 60.")
            self.runtime = 60
        else:
            self.runTime = runTime

        self.chunk = 1024
        self.format = pa.paInt16
        self.channels = 2
        self.sampleRate = 44100

        ScreenAudioRecorderThreaded.frameQueue = Queue()
        ScreenAudioRecorderThreaded.shouldStop = False

        self.p = pa.PyAudio()

        if outputDevice == None:
            self.defaultOutputDeviceInfo = self.p.get_default_output_device_info()
            self.OutputDeviceIndex = self.defaultOutputDeviceInfo["index"]

        elif self.p.get_device_info_by_index(outputDevice) is not None:
            self.outputDevice = outputDevice

        self.audioStream = self.p.open(channels=self.channels, format=self.format, input=True, output_device_index=self.OutputDeviceIndex, frames_per_buffer=self.chunk, rate=self.sampleRate)

        if not self.audioStream.is_active():
            self.logger.fatal("Failed to open audio stream!")


    def getFrameQueue(self):

        return ScreenAudioRecorderThreaded.frameQueue


    def stop(self):

        ScreenAudioRecorderThreaded.shouldStop = True

    
    def run(self):

        self.logger.debug("Starting audio recording...")

        for i in range(int(self.sampleRate / self.chunk * self.runTime)):

            data = self.audioStream.read(self.chunk)
            ScreenAudioRecorderThreaded.frameQueue.put(data)

            if ScreenAudioRecorderThreaded.shouldStop:
                break

        self.audioStream.stop_stream()
        self.audioStream.close()
        self.p.terminate()