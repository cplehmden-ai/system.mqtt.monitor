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

def get_info_label(label, retries=10):

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
    def __init__(self, ADDON, cache):
        self.prev_idle = 0
        self.prev_total = 0
        self.addon = ADDON
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

        values = [float(v) for v in values]
        
        log(f"CPU average: {round(sum(values) / len(values), 1)}", debug=True)
        
        self.last_cpu = round(sum(values) / len(values), 1)

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

        self.last_mem_used = int(float(text))

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

        self.last_mem_total = int(float(text))    
        
        return int(float(text))

    def cpu_frequency(self):

        text = get_info_label("System.CpuFrequency")

        if not text:
            return self.last_freq

        if KODI_BUSY in text:
            return self.last_freq

        value = float(text.replace("MHz", "").replace(",", ".").strip())

        self.last_freq = round(value / 1000, 1)
        self.cache.set("cpu_frequency", self.last_freq)

        return self.last_freq
  
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
            self.last_cputemp = int(temp.replace("°C", "").replace(",", ".").strip())
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
            self.last_gputemp = int(temp.replace("°C", "").replace(",", ".").strip())
            return int(temp.replace("°C", "").replace(",", ".").strip())
        except ValueError:
            return None    
    
    def ip_address(self):

        text = get_info_label("Network.IPAddress")

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
            self.cache.set("ip_address", text)

        return self.last_ip

    def resolution(self):

        text = get_info_label("System.ScreenResolution")

        if KODI_NOT_AVAILABLE in text:
            return None
        
        if not text:

            if self.last_res is None:
                return None           
            return self.last_res
        
        elif KODI_BUSY in text:
            if self.last_res is None:
                return None
            return self.last_res

        else:   
            vorher, trenner, _ = text.partition("Hz")
            neuer_text = vorher + trenner

        self.last_res = neuer_text        

        return neuer_text

    def os_version(self):
        
        text = get_info_label("System.OSVersionInfo")

        if KODI_NOT_AVAILABLE in text:
            return None
        
        if not text:

            if self.last_os is None:
                return None
            return self.last_os
        
        elif KODI_BUSY in text:
            if self.last_os is None:
                return None
            return self.last_os

        else:
            neuer_text = re.sub(r'\s*\(.*?\)', '', text)          
            self.last_os = neuer_text       
         
        self.last_os = neuer_text
        self.cache.set("os_version", neuer_text)
        return neuer_text

    def disk_space(self):

        text = get_info_label("System.FreeSpace")
 
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
            neuer_text = re.sub(r'[^0-9.,]', '', text)            
            self.last_disk = neuer_text     
         
        return round(float(neuer_text)/1024,1)


    def uptime(self):
        
        text = get_info_label("System.Uptime")
 
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
        
        text = get_info_label("System.TotalUptime")

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
            
        self.cache.set("uptime_total", timestr / 86400)

        return round(timestr / 86400, 5)

    def os_icon(self):

        os = self.os_version()

        if os is None:
            return "mdi:desktop-classic"

        if os.startswith("Windows"):
            return "mdi:microsoft-windows"

        if os.startswith(("LibreELEC", "CoreELEC", "Linux", "OSMC")):
            return "mdi:penguin"

        if os.startswith(("Android", "Google")):
            return "mdi:android"

        if os.startswith(("macOS", "OS X")):
            return "mdi:apple"

        if os.startswith(("iOS", "tvOS")):
            return "mdi:apple-ios"

        return "mdi:desktop-classic"  

#    def collect_device_info(self, addon):
#        return {
#            "manufacturer": addon.getSetting("device_manufacturer"),
#            "model": addon.getSetting("device_model"),
#            "sw_version": get_info_label("System.BuildVersionShort"),
#            "os_icon": self.os_icon(),        }

    def collect_device_info(self):
        return {
            "manufacturer": self.addon.getSetting("device_manufacturer"),
            "model": self.addon.getSetting("device_model"),
            "sw_version": get_info_label("System.BuildVersionShort"),
            "os_icon": self.os_icon(),
        }
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
