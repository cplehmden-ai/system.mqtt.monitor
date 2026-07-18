import xbmc
import re
import time

from constants import (
    KODI_BUSY,
    KODI_NOT_AVAILABLE,
    KODI_MINUTES,
    KODI_HOURS,
    KODI_DAYS,
)

from logger import log

def get_info_label(label, retries=5):

    for _ in range(retries):
        text = xbmc.getInfoLabel(label)

        if text != KODI_BUSY:
            return text

        xbmc.sleep(200)

    return text

def parse_uptime(text):
    
    #Wandelt Kodi-Uptime-Strings in Sekunden um.

    #Beispiele:
    #    "5 Tage, 20 Stunden, 10 Minuten"
    #    "26 Minuten"
     
    if not text:
        return None

    total = 0

    units = {
        KODI_DAYS: 86400,
        KODI_HOURS: 3600,
        KODI_MINUTES: 60,
    }
    
    matches = re.findall(r"(\d+)\s+([^\d,]+)", text)
    
    if not matches:
        return None
    
    for value, unit in matches:
        unit = unit.strip()

        if unit in units:
            total += int(value) * units[unit]
        
    log(f"[MQTTMonitor] Uptime-Text: {text}", debug=True)
    log(f"[MQTTMonitor] Matches: {matches}", debug=True)
    log(f"[MQTTMonitor] Sekunden: {total}", debug=True)
    
    return total

class SystemInfo:
    def __init__(self, addon, cache):
        self.prev_idle = 0
        self.prev_total = 0
        self.addon = addon
        self.cache = cache
        self.last_ip = cache.get("ip_address")
        self.last_os = cache.get("os_version")
        self.last_freq = cache.get("cpu_frequency")
        self.last_uptime_total = cache.get("uptime_total")
        self.last_uptime = None
        self.last_cpu = None
        self.last_mem_used = None
        self.last_res = None
        self.last_mem_total = None
        self.last_disk = None
        self.last_cputemp = None
        self.last_gputemp = None
    
    def cpu_load(self):
        text = get_info_label("System.CpuUsage").replace(",", ".")

        if not text:
            return None

        if KODI_BUSY in text:
            if self.last_cpu is not None:
                return self.last_cpu
            return None
        
        if KODI_NOT_AVAILABLE in text:
            return None

        values = re.findall(r"(\d+(?:\.\d+)?)%", text)

        if not values:
            return None

#        if KODI_BUSY in text:
#            if self.last_load is not None:
#                return self.last_load
#            return None
        
#        if KODI_NOT_AVAILABLE in text:
#            return None

        values = [float(v) for v in values]
        
        log(f"CPU average: {round(sum(values) / len(values), 1)}", debug=True)
        
        return round(sum(values) / len(values), 1)

    def memory_used(self):
        text = get_info_label("System.Memory(used.percent)")

        if not text:
            return None

        if KODI_BUSY in text:
            if self.last_mem_used is not None:
                return self.last_mem_used
            return None
        
        if KODI_NOT_AVAILABLE in text:
            return None

        text = text.replace("%", "").replace(",", ".").strip()

        return int(float(text))

    def memory_total(self):
        text = get_info_label("System.Memory(total)")

        if not text:
            return None

        if KODI_BUSY in text:
            if self.last_mem_total is not None:
                return self.last_mem_total
            return None
        
        if KODI_NOT_AVAILABLE in text:
            return None

        text = text.replace("MB", "").replace(",", ".").strip()

        return int(float(text))

    def cpu_frequency(self):

        for i in range(10):
            text = xbmc.getInfoLabel("System.CpuFrequency")
            xbmc.sleep(200)

        if not text:
            if self.last_freq is None:
                return None
            text = self.last_freq

        elif KODI_BUSY in text:
            if self.last_freq is None:
                return None
            text = self.last_freq

        else:
            self.last_freq = text

        value = float(text.replace("MHz", "").replace(",", ".").strip())
        return round(value / 1000, 1)

  
    def cpu_temperature(self):
        temp = get_info_label("System.CPUTemperature")

        if not temp:
            return None

        if KODI_BUSY in temp:
            if self.last_cputemp is not None:
                return self.last_cputemp
            return None
        
        if KODI_NOT_AVAILABLE in temp:
            return None

        try:
            return int(temp.replace("°C", "").replace(",", ".").strip())
        except ValueError:
            return None
        
    def gpu_temperature(self):
        temp = get_info_label("System.GPUTemperature")

        if not temp:
            return None

        if KODI_BUSY in temp:
            if self.last_gputemp is not None:
                return self.last_gputemp
            return None
        
        if KODI_NOT_AVAILABLE in temp:
            return None

        try:
            return int(temp.replace("°C", "").replace(",", ".").strip())
        except ValueError:
            return None    
    
    def ip_address(self):

        for i in range(10):
            text = xbmc.getInfoLabel("Network.IPAddress")
            xbmc.sleep(200)

        if not text:
            return self.last_ip

        if KODI_BUSY in text:
            if self.last_ip is not None:
                return self.last_ip
            return None
        
        if KODI_NOT_AVAILABLE in text:
            return None

        if "." in text:
            self.last_ip = text

        return self.last_ip

    def resolution(self):

        text = xbmc.getInfoLabel("System.ScreenResolution")

        if KODI_NOT_AVAILABLE in text:
            return None
        
        if not text:

            if self.last_res is None:
                return None
            text = self.last_res
        
        elif KODI_BUSY in text:
            if self.last_res is None:
                return None
            text = self.last_res

        else:
        
            self.last_res = text    

        vorher, trenner, nachher = text.partition("Hz")
        neuer_text = vorher + trenner

        return neuer_text

    def os_version(self):

        for i in range(10):
            text = xbmc.getInfoLabel("System.OSVersionInfo")
            xbmc.sleep(200)

        if KODI_NOT_AVAILABLE in text:
            return None
        
        if not text:

            if self.last_os is None:
                return None
            text = self.last_os
        
        elif KODI_BUSY in text:
            if self.last_os is None:
                return None
            text = self.last_os

        else:
            
            self.last_os = text    

        neuer_text = re.sub(r'\s*\(.*?\)', '', text)
         
        return neuer_text

    def disk_space(self):

        text = xbmc.getInfoLabel("System.FreeSpace")
 
        if KODI_NOT_AVAILABLE in text:
            return None
 
        if not text:

            if self.last_disk is None:
                return None
            text = self.last_disk
        
        elif KODI_BUSY in text:
            if self.last_disk is None:
                return None
            text = self.last_disk

        else:
            
            self.last_disk = text    

        neuer_text = re.sub(r'[^0-9.,]', '', text)
         
        return round(int(neuer_text)/1024,1)


    def uptime(self):
        
        for i in range(10):
            text = xbmc.getInfoLabel("System.Uptime")
            xbmc.sleep(200)

        seconds = parse_uptime(text)

        if seconds is not None:
            self.last_uptime = seconds

        if KODI_BUSY in text:
            if self.last_uptime is not None:
                return self.last_uptime
            return None
        
        if KODI_NOT_AVAILABLE in text:
            return None
        
        timestr = 0
        
        if self.last_uptime is not None:
            timestr = self.last_uptime

        return round(timestr / 3600, 3)


    def uptime_total(self):
        
        for i in range(10):
            text = xbmc.getInfoLabel("System.TotalUptime")
            xbmc.sleep(200)

        seconds = parse_uptime(text)

        if seconds is not None:
            self.last_uptime_total = seconds

        if KODI_BUSY in text:
            if self.last_uptime_total is not None:
                return self.last_uptime_total
            return None
        
        if KODI_NOT_AVAILABLE in text:
            return None

        timestr = 0
        
        if self.last_uptime_total is not None:
            timestr = self.last_uptime_total

        return round(timestr / 86400, 5)

    def os_icon(self):

        os = self.os_version()

        if os is None:
            return "mdi:desktop-classic"

        if os.startswith("Windows"):
            return "mdi:microsoft-windows"

        if os.startswith(("LibreELEC", "CoreELEC", "Linux")):
            return "mdi:penguin"

        if os.startswith(("Android", "Google")):
            return "mdi:android"

        if os.startswith(("macOS", "OS X")):
            return "mdi:apple"

        if os.startswith(("iOS", "tvOS")):
            return "mdi:apple-ios"

        return "mdi:desktop-classic"  

    def collect_device_info(self, addon):
        return {
            "manufacturer": addon.getSetting("device_manufacturer"),
            "model": addon.getSetting("device_model"),
            "sw_version": get_info_label("System.BuildVersionShort"),
            "os_icon": self.os_icon(),        }

    def collect(self):
        return {
            "cpu": self.cpu_load(),
            "cpu_frequency": self.cpu_frequency(),
            "memory_used": self.memory_used(),
            "memory_total": self.memory_total(),
            "cpu_temperature": self.cpu_temperature(),
            "gpu_temperature": self.gpu_temperature(),
            "uptime": self.uptime(),
            "uptime_total": self.uptime_total(),
            "ip_address": self.ip_address(),
            "resolution": self.resolution(),
            "os_version": self.os_version(),
            "disk_space": self.disk_space(),
        }
    
    def test_labels(self):
        log(xbmc.getInfoLabel("System.Uptime"), debug=True)
        log(f"Uptime (SystemInfo): {self.uptime()}", debug=True)
        log(xbmc.getInfoLabel("System.TotalUptime"), debug=True)
        log(f"Uptime Total (SystemInfo): {self.uptime_total()}", debug=True)        
        log(xbmc.getInfoLabel("System.CpuFrequency"), debug=True)
        log(f"cpu_frequency (SystemInfo): {self.cpu_frequency()}", debug=True)        
        log(xbmc.getInfoLabel("System.OSVersionInfo"), debug=True)
        log(f"OS Version (SystemInfo): {self.os_version()}", debug=True)        
        log(xbmc.getInfoLabel("System.CpuFrequency"), debug=True)
        log(f"IP Adresse (SystemInfo): {self.ip_address()}", debug=True)        
        log(xbmc.getInfoLabel("Network.IPAddress"), debug=True)
        log(xbmc.getInfoLabel("System.BuildVersionShort"), debug=True)
        log(f"OS Icon (SystemInfo): {self.os_icon()}", debug=True)        
