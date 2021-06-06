YOUTUBE_DOMAINS = [
    "googlevideo.com",
    "video.google.com",
    "youtu.be",
    "youtube-nocookie.com",
    "youtube-ui.l.google.com",
    "youtube.com",
    "youtube.googleapis.com",
    "youtubeeducation.com",
    "youtubei.googleapis.com",
    "yt3.ggpht.com",
    "ytimg.com",
]

SUPPORTED_YOUTUBE_DOMAINS = [
    "www.youtube.com",
    "youtu.be",
    "m.youtube.com"
]

# Consent page
AGREE_BUTTON_CLASS= 'VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc IIdkle'
# tp-yt-paper-button id="button" class="style-scope ytd-button-renderer style-primary size-default" role="button" tabindex="0" animated="" elevation="0" aria-disabled="false" aria-label="Agree to the use of cookies and other data for the purposes described"><!--css-build:shady--><yt-formatted-string id="text" class="style-scope ytd-button-renderer style-primary size-default">I Agree</yt-formatted-string><paper-ripple class="style-scope tp-yt-paper-button">
AGREE_PAPER_BUTTON_ARIA_LABEL = "Agree to the use of cookies and other data for the purposes described" # This randomly shows on the front page and it has no discerning ID.


# Searchbox and searchbox button
SEARCH_BOX_ID = 'search'
SEARCH_BOX_NAME = 'search_query'
SEARCH_BOX_BUTTON_ID = 'search-icon-legacy'

# <a></a> tag for finding videos after a search query
QUERY_VIDEO_TITLE_A_ID = "video-title" # Youtube Video Renderer

# <a></a> tag for finding videos on the front page.
# Rich item renderer
FRONT_PAGE_VIDEO_TITLE_A_ID = "video-title-link"

# <span> tag for finding videos on video recommendations while watching another video.
# Compact item renderer
RECOMMEND_VIDEO_TITLE_SPAN_ID = "video-title"

# Video player
VIDEO_PLAYER_PLAY_BUTTON_CLASS = "ytp-play-button ytp-button"
VIDEO_PLAYER_PLAY_BUTTON_TITLE = "Play (k)"

VIDEO_PLAYER_PAUSE_BUTTON_CLASS = "ytp-play-button ytp-button"
VIDEO_PLAYER_PAUSE_BUTTON_TITLE = "Pause (k)"

VIDEO_PLAYER_SKIP_ADDS_BUTTON_CLASS = "ytp-ad-skip-button ytp-button"
VIDEO_ADS_CLASS = "video-ads ytp-ad-module"