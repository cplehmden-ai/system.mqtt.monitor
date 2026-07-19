import json
import os
import xbmcvfs
import xbmcaddon

from logger import log

class Cache:

    def __init__(self):
        addon = xbmcaddon.Addon()

        profile = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
        xbmcvfs.mkdirs(profile)

        self.filename = os.path.join(profile, "cache.json")
        self.data = {}

        self.load()


    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            log(f"Cache load failed: {e}", debug=True)
            self.data = {}

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            log(f"Cache save failed: {e}", debug=True)
            pass


    def get(self, key, default=None):
        return self.data.get(key, default)


    def set(self, key, value):
        self.data[key] = value
        self.save()