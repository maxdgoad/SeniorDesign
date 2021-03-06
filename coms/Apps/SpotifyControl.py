import spotipy
from spotipy.oauth2 import SpotifyOAuth
from Apps import SpotifyAuth
from Apps import ImageWriter
from Apps import WindowsProgramControl

# SpotifyControl.py
# this file is the spotify driver. Executes spotify api calls.

# make sure to update your credentials in SpotifyAuth.py
auth_manager = SpotifyAuth.getAuthManager()

sp = spotipy.Spotify(auth_manager=auth_manager)

cached_currently_playing = sp.currently_playing()


def getDeviceIds():
    devices = sp.devices()['devices']
    ids = []
    for device in devices:
        ids.append(device['id'])
    return ids


deviceIDs = getDeviceIds()


def setup():
    # setup
    global sp
    global auth_manager
    sp = spotipy.Spotify(auth_manager=auth_manager)
    auth_manager = SpotifyAuth.getAuthManager()
    cached_currently_playing = sp.currently_playing()


def pausePlayback():
    global sp
    sp.pause_playback()


def startPlayback():
    global sp
    sp.start_playback()

# params: newVolume - the new volume for the player (0-100)
def setVolume(newVolume):
    global sp
    sp.volume(int(newVolume))


def getVolume():
    global sp
    return sp.devices()['devices'][0]['volume_percent']

# params: shuffleState - true for shuffle false for linear
def setShuffle(shuffleState):
    global sp
    sp.shuffle(shuffleState == "true")


def skipSong():
    global sp
    sp.next_track()


def previousSong():
    global sp
    sp.previous_track()

# params:
# repeatState - the new state for repeat
#   "track" - repeat the current track
#   "context" - repeat the current context (NO IDEA WHAT THIS MEANS) ***update: this means to loop the entire album/playlist***
#   "off" - no repeat
def setRepeatStatus(repeatState):
    global sp
    sp.repeat(repeatState)


# get the current song data from spotify, also opens spotify minimzed if not open, and stores the data
def getCurrentlyPlaying():
    global sp
    global cached_currently_playing
    global deviceIDs
    cached_currently_playing = sp.currently_playing()
    try:
        while cached_currently_playing == None:
            if len(deviceIDs) == 0:
                WindowsProgramControl.openProgram("Spotify.exe") # takes a looong time to open
                while deviceIDs == None or len(deviceIDs) == 0:
                    deviceIDs = getDeviceIds()
                WindowsProgramControl.minimizeProgByName("Spotify")
                sp.transfer_playback(deviceIDs[0])
                sp.pause_playback(device_id=deviceIDs[0])
            cached_currently_playing = sp.currently_playing()
        cached_currently_playing['volume'] = getVolume() # appends volume also (it's not included in the original data)
        return cached_currently_playing
    except Exception as e:
        print(e)
        return None


def getUpdatedData():
    global sp
    global cached_currently_playing
    # checks the small data for updates, then returns the big data
    newData = sp.currently_playing()
    attempts = 1
    while(newData != None and cached_currently_playing != None and newData['item']['id'] == cached_currently_playing['item']['id'] and attempts < 10):
        newData = sp.currently_playing()
        attempts += 1
    return getCurrentlyPlaying()


def getTopArtists():
    global sp
    return sp.current_user_top_artists()


def seek(pos):
    # seek to position in percentage of track
    global sp
    pos_ms = int(float(pos) * sp.currently_playing()['item']['duration_ms'])
    sp.seek_track(pos_ms)


def search(query):
    global sp
    return sp.search(query, type="track")


def playTrack(uri):
    global sp
    sp.start_playback(uris=[uri])
    updated = getUpdatedData()
    return updated


def getAlbumImage():
    global sp
    cp = cached_currently_playing
    image_name = 'album.jpg'
    # bad. downloads image as local album.jpg
    ImageWriter.writeImage(image_name, cp['item']['album']['images'][1]['url'])
    # bad bad. converts that jpg to a base64 encoded string to send to RaspPi using json
    string = ImageWriter.imageTo64String(image_name)
    # this should be as simple a json as we can manage. Dat speed bro
    jason = {"imageString": string}
    return jason
