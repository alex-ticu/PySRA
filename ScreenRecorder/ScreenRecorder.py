from ScreenAudioRecorder import ScreenAudioRecorderThreaded
from ScreenVideoRecorder import ScreenVideoRecorderThreaded
import logging
from pathlib import Path


class ScreenRecorder():

    def __init__(self, videoSavePath, audioSavePath, runTime=60, fps=20, quitKey='q', outputDevice=None, loggingLevel=logging.DEBUG, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        # Init logging
        self.logger = logging.getLogger('ScreenRecorder')
        self.logger.setLevel(loggingLevel)

        ch = logging.StreamHandler()
        ch.setLevel(loggingLevel)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        # Done

        self.quitKey = quitKey

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
            self.logger.warning("No video file path given. Defaulting to current directory")
            self.videoSavePath = Path(".")
            self.videoSaveName = "videoOutput.avi"
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
            self.logger.warning("No audio file path given. Defaulting to current directory")
            self.audioSavePath = Path(".")
            self.audioSaveName = "audioOutput.wav"
            self.logger.warning("Saving video to: {0}/{1}".format(str(self.audioSavePath), self.audioSaveName))

        # Check if files are different.
        if self.videoSaveName == self.audioSaveName:

            self.logger.warning("Video file and audio file have same names! Using default names.")
            self.audioSaveName = "audioOutput.wav"
            self.videoSaveName = "videoOutput.avi"
            

        self.videoRecorderThread = ScreenVideoRecorderThreaded(runTime=runTime, fps=fps, loggingLevel=logging.DEBUG)
        self.audioRecorderThread = ScreenAudioRecorderThreaded(runTime=runTime, outputDevice=outputDevice, loggingLevel=logging.DEBUG)


    def record(self):

        if not self.videoSavePath.is_dir():
            self.logger.debug("Creating {0}/".format(str(self.videoSavePath)))
            Path.mkdir(self.videoSavePath)

        if not self.audioSavePath.is_dir():
            self.logger.debug("Creating {0}/".format(str(self.videoSavePath)))
            Path.mkdir(self.audioSavePath)