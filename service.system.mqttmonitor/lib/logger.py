import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()

def log(msg, debug=False):

    if debug and ADDON.getSetting("debug") != "true":
        return

    xbmc.log(f"[MQTTMonitor] {msg}", xbmc.LOGINFO)