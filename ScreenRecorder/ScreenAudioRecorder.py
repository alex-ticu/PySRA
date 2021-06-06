from queue import Queue
import pyaudio as pa
import logging
from threading import Thread
from threading import Lock
from queue import Queue

class ScreenAudioRecorderThreaded(Thread):

    frameQueue = Queue()
    shouldStop = False
    audioFrameCount = 0
    lock = Lock()

    def __init__(self, inputDevice=None, chunk=1024, format=pa.paInt16, channels=2, sampleRate=44100, runTime=60, loggingLevel=logging.DEBUG, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        
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

        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.sampleRate = sampleRate


        self.p = pa.PyAudio()

        if inputDevice == None:
            self.defaultInputDeviceInfo = self.p.get_default_input_device_info()
            self.inputDeviceIndex = self.defaultInputDeviceInfo["index"]

        elif self.p.get_device_info_by_index(inputDevice) is not None:
            self.inputDevice = inputDevice

        self.audioStream = self.p.open(channels=self.channels, format=self.format, input=True, input_device_index=self.inputDeviceIndex, frames_per_buffer=self.chunk, rate=self.sampleRate)
        #self.audioStream = self.p.open(channels=self.channels, format=self.format, input=True, input_device_index=22, frames_per_buffer=self.chunk, rate=self.sampleRate)

        if not self.audioStream.is_active():
            self.logger.fatal("Failed to open audio stream!")


    def getFrameQueue(self):

        return ScreenAudioRecorderThreaded.frameQueue


    def getSampleWidth(self):

        return self.p.get_sample_size(self.format)


    def stop(self):

        ScreenAudioRecorderThreaded.shouldStop = True

    
    def run(self):

        #for i in range(int(self.sampleRate / self.chunk * self.runTime)):
        while ScreenAudioRecorderThreaded.audioFrameCount < int(self.sampleRate / self.chunk * self.runTime):

            with ScreenAudioRecorderThreaded.lock:
                data = self.audioStream.read(self.chunk)
                ScreenAudioRecorderThreaded.frameQueue.put(data)

                ScreenAudioRecorderThreaded.audioFrameCount += 1

            if ScreenAudioRecorderThreaded.shouldStop:
                break

        self.audioStream.stop_stream()
        self.audioStream.close()
        self.p.terminate()