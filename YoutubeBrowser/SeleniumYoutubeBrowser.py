from re import search
from urllib import parse
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from urllib.parse import urlparse
import logging
from constants import *

class SeleniumYoutubeBrowser():
    def __init__(self, URL=None, maximize: bool=False, loggingLevel=logging.DEBUG):
        
        # Init logging
        self.logger = logging.getLogger('SeleniumYoutubeBrowser')
        self.logger.setLevel(loggingLevel)

        ch = logging.StreamHandler()
        ch.setLevel(loggingLevel)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        # Done

        self.logger.debug('Starting up Firefox webdriver...')
        self.browser = webdriver.Firefox()
        self.logger.debug('Firefox webdriver started!')

        if maximize == True:
            self.browser.maximize_window()

        if URL is not None:
            self.browse(URL)
        else:
            self.browse('https://www.youtube.com/')


    def browse(self, URL):
        
        parsedURL = urlparse(URL)

        # Check if domain Youtube primary domain, but only after prefix (eg: www. ~youtube.com~).
        if parsedURL.netloc.split(sep='.', maxsplit=1)[1] not in YOUTUBE_DOMAINS:
            self.logger.error(str(parsedURL.netloc) + ' is not a Youtube domain!')

        else:
            # TODO: Implement functionality for other Youtube domains.
            # Check if it is www.youtube.com or youtu.be (for sharable links) or m.youtube.com (for mobile).
            if parsedURL.netloc != 'www.youtube.com' and parsedURL.netloc != 'youtu.be' and parsedURL.netloc != 'm.youtube.com':
                self.logger.error(str(parsedURL.netloc) + ' is not a supported Youtube domain!')

            else:
                # Check if URL scheme is https.
                if parsedURL.scheme != 'https' and parsedURL.scheme != 'http':
                        self.logger.error(str(parsedURL.scheme) + ' scheme not supported!')
                
                else:
                    # If scheme is 'http', just change it to 'https'.
                    if parsedURL.scheme == 'http':
                        self.logger.warning('http scheme found. Replacing to https!')
                        parsedURL._replace(scheme='https')

                    self.browser.get(URL)
                    self.logger.debug('Browsing ' + str(URL))

                    # Check if the consent page appeared.
                    if urlparse(self.browser.current_url).netloc == 'consent.youtube.com':
                        self.logger.warning('Consent page detected. Pressing "I agree" and continuing...')

                        xpathSelector = "//button[@aria-label='" + AGREE_BUTTON_ARIA_LABEL + "']"

                        self.browser.find_element_by_xpath(xpathSelector).click()


    def isOnYoutube(self):
        # Check if the current page is a Youtube page

        parsedURL = urlparse(self.browser.current_url).netloc.split(sep='.', maxsplit=1)
        if parsedURL[1] == 'youtube.com' and parsedURL[0] != 'consent':
            # If it is not the consent page, then we're on Youtube.
                return True

        else:
            return False


    def findYoutubeSearchBox(self):

        if not self.isOnYoutube():
            self.logger.error("Youtube searchbox can't be found!")
            return None

        else:
            # searchbox is something like <input id='search' name='search_query' type='text'>.
            xpathSelector = "//input[@id='" + SEARCH_BOX_ID + "'" + " and @name='" + SEARCH_BOX_NAME + "' and @type='text']"
            
            # Need to wait if internet is slow.
            try:
                searchBox = WebDriverWait(self.browser, 20).until(lambda x: x.find_element_by_xpath(xpathSelector))
            except TimeoutException as t:
                self.logger.exception("Timeout: {0}".format(t))
                return None

            return searchBox


    def findYoutubeSearchBoxButton(self):
        
        if not self.isOnYoutube():
            self.logger.error("Youtube searchbox button can't be found!")
            return None

        else:
            # searchbox button is something like <button id='search-icon-legacy'>
            xpathSelector = "//button[@id='" + SEARCH_BOX_BUTTON_ID + "']"
            try:
                searchBoxButton = WebDriverWait(self.browser, 20).until(lambda x: x.find_element_by_xpath(xpathSelector))
            except TimeoutException as t:
                self.logger.exception("Timeout: {0}".format(t))
                return None

            return searchBoxButton


    def browseYoutube(self, searchQuery=None):
        # If searchQuery is None, search for videos on current page, otherwise use the searchbox.
        # Else search by <a> tag with id = video-title-link.

        if searchQuery is None:
            availableVideos = self.getAvailableVideos()
            return availableVideos

        searchBox = self.findYoutubeSearchBox()
        searchBoxButton = self.findYoutubeSearchBoxButton()
        if searchBox is None or searchBoxButton is None:
            self.logger.error("Youtube searchbox cannot be found!")
        
        else:
            # send_keys is defined in selenium/remote/webelement.py
            searchBox.send_keys(searchQuery)
            searchBoxButton.click()

            # Clear searchbox
            searchBox = self.findYoutubeSearchBox()
            searchBox.clear()
            
            availableVideos = self.getAvailableVideos()

            return availableVideos
    

    def isSearchQuery(self):
        # Check if the current page is the resulf of pressing the search button.

        if not self.isOnYoutube():
            self.logger.error("The loaded page is not Youtube!")
            return False
        
        parsedURL = urlparse(self.browser.current_url)
        # Youtube search page URL looks something like https://www.youtube.com/results?search_query=....
        if parsedURL.path == '/results' and 'search_query' in parsedURL.query:
            return True

        else:
            return False


    def getAvailableVideos(self):
        # TODO: Also implement functionality for playlists.
        # Create a list of all available videos: [(videoTitle, videoLink), ...]

        videos = []

        if not self.isOnYoutube():
            self.logger.error("The loaded page is not Youtube!")
            return None

        if self.isSearchQuery():
            xpathSelector = "//a[@id='" + QUERY_VIDEO_TITLE_A_ID + "']"

            # Wait for first renderer to load.
            try:
                waitForVideosToLoad = WebDriverWait(self.browser, 30).until(lambda element: element.find_element_by_tag_name('ytd-item-section-renderer'))#ytd-continuation-item-renderer
            except TimeoutException as t:
                self.logger.exception("Timeout while waiting for search query videos! {0}".format(t))
            
            videoLinks = self.browser.find_elements_by_xpath(xpathSelector)

            for videoLink in videoLinks:
                videoHref = videoLink.get_attribute('href')
                videoTitle = videoLink.get_attribute('title')
                videos.append((videoTitle, videoHref))

        elif urlparse(self.browser.current_url).path == '/':
            # Youtube start page
            
            xpathSelector = "//a[@id='" + FRONT_PAGE_VIDEO_TITLE_A_ID + "']"

            try:
                waitForVideosToLoad = WebDriverWait(self.browser, 30).until(lambda element: element.find_element_by_tag_name('ytd-rich-grid-renderer'))
            except TimeoutException as t:
                self.logger.exception("Timeout while waiting for main page videos! {0}".format(t))
            
            videoLinks = self.browser.find_elements_by_xpath(xpathSelector)
        
            for videoLink in videoLinks:
                videoHref = videoLink.get_attribute('href')
                videoTitle = videoLink.get_attribute('title')
                videos.append((videoTitle, videoHref))

        elif urlparse(self.browser.current_url).path == '/watch':
            # TODO
            # Youtube video page
            self.logger.fatal("Playing videos from recommended not implemented yet!")
            pass

        if not videos:
            self.logger.error("No videos found!")

        return videos

    def playVideo(self, videoLink):
        # TODO: Try to skip adds :( - Done. (Needs more testing?)
        # Plays video

        self.browser.get(videoLink)
        
        skipAdsxpathSelector = "//button[@class='" + VIDEO_PLAYER_SKIP_ADDS_BUTTON_CLASS + "']"
        adsxpathSelector = "//div[@class='" + VIDEO_ADS_CLASS + "']"
        playButtonxpathSelector = "//button[@class='" + VIDEO_PLAYER_PLAY_BUTTON_CLASS + "' and @title='" + VIDEO_PLAYER_PLAY_BUTTON_TITLE + "']"
        pauseButtonxpathSelector = "//button[@class='" + VIDEO_PLAYER_PAUSE_BUTTON_CLASS + "' and @title='" + VIDEO_PLAYER_PAUSE_BUTTON_TITLE + "']"

        # While the ads overlay is displayed try to click the skip ads button. If timeout exception is reached, then it means no more ads are playing or they are unskippable
        while self.browser.find_element_by_xpath(adsxpathSelector).is_displayed():
            self.logger.debug("Ads are playing. Trying to skip...")
            # If the play button is not pressed, then some ads will skip themselves
            try:
                skipAdsButton = WebDriverWait(self.browser, 10, 2).until(lambda x: x.find_element_by_xpath(skipAdsxpathSelector))
                try:
                    skipAdsButton.click() # Funny how ads can be exactly 5 seconds long and the button expires...
                except:
                    pass
                self.logger.debug("Clicked Skip Ads button.")
            except TimeoutException as t:
                self.logger.debug("Ads skipped themselves")
                pass

        # If the pause is not found, then it means that the video is paused, so we press the play button.
        if not self.browser.find_elements_by_xpath(pauseButtonxpathSelector):
            self.logger.debug("Pressing the play button.")
            try:
                playButton = WebDriverWait(self.browser, 60).until(lambda button: button.find_element_by_xpath(playButtonxpathSelector))
                playButton.click()
            except TimeoutException as t:
                self.logger.exception("Timeout: {0}".format(t))

        else:
            self.logger.debug("No need to press the play button, the video already started!")
        

    def playYoutubeVideo(self, youtubeVideo: tuple=None):
        # Play a video on Youtube. If youtubeVideo is None, then play first video on current page.

        if youtubeVideo is None:
            vids = self.browseYoutube()

            self.logger.debug("Playing video: {0}".format(vids[0][0]))
            self.playVideo(vids[0][1])

        else:
            self.logger.debug("Playing video: {0}".format(youtubeVideo[0]))
            self.playVideo(youtubeVideo[1])

browser = SeleniumYoutubeBrowser()

videos=browser.browseYoutube()
print(videos[0])
browser.playYoutubeVideo()

