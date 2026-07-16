import xbmc
import json
import re
import paho.mqtt.client as mqtt
import xbmcaddon
import re

from logger import log

def make_device_id(name):
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
    }

    name = name.strip().lower()

    for old, new in replacements.items():
        name = name.replace(old, new)

    # Alle Leerzeichen durch Unterstriche ersetzen
    name = re.sub(r"\s+", "_", name)

    # Alle unerlaubten Zeichen entfernen
    name = re.sub(r"[^a-z0-9_]", "", name)

    # Mehrere Unterstriche zusammenfassen
    name = re.sub(r"_+", "_", name)

    return name

class MQTTClient:
    def __init__(self, addon):
        self.addon = addon

        version = xbmcaddon.Addon().getAddonInfo('version')
        if not version:
            version = ""

        # Einstellungen
        self.host = addon.getSetting("mqtt_host")
        self.port = int(addon.getSetting("mqtt_port"))
        self.username = addon.getSetting("mqtt_user")
        self.password = addon.getSetting("mqtt_pass")

        device_name = addon.getSetting("device_name")
        if not device_name:
            device_name = "Kodi"
        
        device_manufacturer = addon.getSetting("device_manufacturer")
        if not device_manufacturer:
            device_manufacturer = "Unknown"
        
        device_model = addon.getSetting("device_model")
        if not device_model:
            device_model = "Unknown"

        sw = xbmc.getInfoLabel("System.BuildVersionShort")
        if not sw:
            sw = ""
        
        sw_version = f"Kodi {sw} - Addon {version}"


        self.device_name = device_name
        self.device_id = make_device_id(device_name)
        self.device_manufacturer = device_manufacturer
        self.device_model = device_model
        self.sw_version = sw_version
        self.prefix = f"kodi/{self.device_id}"
        self.client = mqtt.Client(client_id=self.device_id)
        
        if len(self.username) > 0:
            self.client.username_pw_set(self.username, self.password)    
   
    def _get_int(self, key, default):
        try:
            return int(self.addon.getSetting(key))
        except Exception:
            return default

    def connect(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()

            # online melden
            self.publish(f"{self.prefix}/availability", "online", retain=True)

            xbmc.log("MQTT connected", xbmc.LOGINFO)
            return True
        except Exception as e:
            xbmc.log(f"MQTT connect failed: {e}", xbmc.LOGERROR)
            return False

    def disconnect(self):
        try:
            self.publish(f"{self.prefix}/availability", "offline", retain=True)
            self.client.loop_stop()
            self.client.disconnect()
            xbmc.log("MQTT disconnected", xbmc.LOGINFO)
        except Exception as e:
            xbmc.log(f"MQTT disconnect error: {e}", xbmc.LOGERROR)

    def publish(self, topic, payload, retain=False):
        try:
            # Payload IMMER sicher zu String machen
            if payload is None:
                payload = ""
            elif not isinstance(payload, (str, bytes)):
                payload = json.dumps(payload)

            self.client.publish(
                topic=topic,
                payload=payload,
                qos=0,
                retain=retain
            )
        except Exception as e:
            xbmc.log(f"MQTT publish error ({topic}): {e}", xbmc.LOGERROR)

    def publish_states(self, data):
        """
        data = dict wie z.B.:
        {
            "cpu": 23.5,
            "memory": 61.2,
            "temperature": 54.0,
            "uptime": 12345
        }
        """
        for key, value in data.items():
            
            if value is None:
                continue

            self.publish(f"{self.prefix}/{key}", str(value))    