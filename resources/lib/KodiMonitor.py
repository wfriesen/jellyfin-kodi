#################################################################################################
# Kodi  Monitor
# Watched events that occur in Kodi, like setting media watched
#################################################################################################

import xbmc
import xbmcgui
import xbmcaddon
import json

import Utils as utils
from WriteKodiDB import WriteKodiDB
from ReadKodiDB import ReadKodiDB
from PlayUtils import PlayUtils
from DownloadUtils import DownloadUtils
from PlaybackUtils import PlaybackUtils

class Kodi_Monitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onDatabaseUpdated(self, database):
        pass
    
    #this library monitor is used to detect a watchedstate change by the user through the library
    #as well as detect when a library item has been deleted to pass the delete to the Emby server
    def onNotification  (self,sender,method,data):
        addon = xbmcaddon.Addon(id='plugin.video.emby')
        downloadUtils = DownloadUtils()
        print "onNotification:" + method + ":" + sender + ":" + str(data)
        #player started playing an item - 
        if method == "Playlist.OnAdd":
            print "playlist onadd is called"
            jsondata = json.loads(data)
            if jsondata != None:
                if jsondata.has_key("item"):
                    if jsondata.get("item").has_key("id") and jsondata.get("item").has_key("type"):
                        id = jsondata.get("item").get("id")
                        type = jsondata.get("item").get("type")
                        embyid = ReadKodiDB().getEmbyIdByKodiId(id,type)
                        
                        print "id --> " + str(id)
                        print "type --> " + type
                        print "emby_id --> " + embyid
                        if embyid != None:
                           
                            WINDOW = xbmcgui.Window( 10000 )
                            
                            username = WINDOW.getProperty('currUser')
                            userid = WINDOW.getProperty('userId%s' % username)
                            server = WINDOW.getProperty('server%s' % username)

                            url = "{server}/mediabrowser/Users/{UserId}/Items/%s?format=json&ImageTypeLimit=1" % embyid
                            result = downloadUtils.downloadUrl(url)     
                            
                            #launch playbackutils
                            PlaybackUtils().PLAY(result)
        
        if method == "VideoLibrary.OnUpdate":
            jsondata = json.loads(data)
            if jsondata != None:
                
                playcount = None
                playcount = jsondata.get("playcount")
                item = jsondata.get("item").get("id")
                type = jsondata.get("item").get("type")
                if playcount != None:
                    utils.logMsg("MB# Sync","Kodi_Monitor--> VideoLibrary.OnUpdate : " + str(data),2)
                    WriteKodiDB().updatePlayCountFromKodi(item, type, playcount)
                    
                
                

