from pyautogui import run
from ScreenRecorder.ScreenRecorder import ScreenRecorder
from YoutubeBrowser.SeleniumYoutubeBrowser import SeleniumYoutubeBrowser
from threading import Thread


# Browser parameters
browserMaximize = True
searchParam = "northernlion"

# Recording parameters.
videoPath = "./recording/video.avi"
audioPath = "./recording/audio.wav"
runTime = 30
fps = 20

recordThreadArgs = (videoPath, audioPath, runTime, fps)

def recordThreaded(videoPath, audioPath, runtime, fps):

    rec = ScreenRecorder(videoSavePath=videoPath, audioSavePath=audioPath, runTime=runTime, fps=fps)
    rec.record()


if __name__ == "__main__":
    
    # Start the browser in the main thread.

    browser = SeleniumYoutubeBrowser(maximize=browserMaximize, URL="https://www.youtube.ro/")

    # Start recording.
    recThread = Thread(target=recordThreaded, args=recordThreadArgs)
    recThread.daemon = True
    recThread.start()

    # Play a youtube video.
    # Search for a specific topic
    videos = browser.browseYoutube(searchParam)
    browser.playYoutubeVideo(videos[0])

    # Get first video from the home page
    #browser.playYoutubeVideo()

    # Wait for recording to finish.
    recThread.join()

    # Close the browser.
    browser.quit()