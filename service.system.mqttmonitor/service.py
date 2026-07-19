import xbmc
import xbmcaddon
import sys
import os

ADDON = xbmcaddon.Addon(id="service.system.mqttmonitor")

ADDON_PATH = ADDON.getAddonInfo("path")
sys.path.insert(0, os.path.join(ADDON_PATH, "lib"))

from mqtt_client import MQTTClient
from system_info import SystemInfo
from ha_discovery import publish_discovery
from lib.cache import Cache
from logger import log

cache = Cache()

monitor = xbmc.Monitor()
    
def get_int_setting(setting_id, default):
    try:
        return int(ADDON.getSetting(setting_id))
    except (ValueError, TypeError):
        return default

def main():
    log("MQTTMonitor starting")

    # Give Kodi enough time to initialize InfoLabels
    if monitor.waitForAbort(10):
        return    
      
    mqtt = MQTTClient(ADDON)
    sysinfo = SystemInfo(ADDON, cache)
    
    device_info = sysinfo.collect_device_info()
    data = sysinfo.collect()
    sysinfo.test_labels()

    if not mqtt.connect():
        log("MQTT connection failure")
        return

    publish_discovery(mqtt, ADDON, device_info, data)

    interval = get_int_setting("interval", 30)

    while not monitor.abortRequested():
        data = sysinfo.collect()
        mqtt.publish_states(data)
        sysinfo.test_labels()
        
        if monitor.waitForAbort(interval):
            break

    mqtt.disconnect()
    log("Service stopped")
    
if __name__ == "__main__":
    main()