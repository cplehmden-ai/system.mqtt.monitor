def publish_discovery(mqtt, ADDON, device_info, data):
    sensors = {
        "cpu": (ADDON.getLocalizedString(30101), "%", None, None, "mdi:cpu-64-bit", None),
        "cpu_frequency": (ADDON.getLocalizedString(30102), "Ghz", None, None, "mdi:sine-wave", None),
        "cpu_temperature": (ADDON.getLocalizedString(30103), "°C", "temperature", None, None, None),
        "gpu_temperature": (ADDON.getLocalizedString(30104), "°C", "temperature", None, None, None),
        "uptime": (ADDON.getLocalizedString(30105), "h", "duration", None, None, 2),
        "uptime_total": (ADDON.getLocalizedString(30106), "d", "duration", None, None, 3),
        "memory_used": (ADDON.getLocalizedString(30107), "%", None, None, "mdi:memory-arrow-down", None),
        "ip_address": (ADDON.getLocalizedString(30108), "", None, "diagnostic", "mdi:ip-network", None),
        "resolution": (ADDON.getLocalizedString(30109), "", None, None, "mdi:monitor", None),
        "os_version": (ADDON.getLocalizedString(30110), "", None, "diagnostic", device_info["os_icon"], None),
        "memory_total": (ADDON.getLocalizedString(30111), "MB", None, "diagnostic", "mdi:memory", None),
        "disk_space": (ADDON.getLocalizedString(30112), "GB", None, "diagnostic", "mdi:harddisk", None),
    }
    
    for key, (name, unit, device_class, entity_category, icon, suggested_display_precision) in sensors.items():

        if data[key] is None:
            continue

        if key in ("disk_space", "cpu_frequency") and data[key] == 0:
            continue

        topic = f"homeassistant/sensor/{mqtt.device_id}_{key}/config"

        payload = {
            "name": name,
            "state_topic": f"{mqtt.prefix}/{key}",
            "availability_topic": f"{mqtt.prefix}/availability",
            "unit_of_measurement": unit,
            "unique_id": f"{mqtt.device_id}_{key}",
            "device": {
                "identifiers": [mqtt.device_id],
                "name": mqtt.device_name,
                "manufacturer": mqtt.device_manufacturer,
                "model": mqtt.device_model,
                "sw_version": mqtt.sw_version,
            }
        }

        if suggested_display_precision:
            payload["suggested_display_precision"] = suggested_display_precision

        if icon:
            payload["icon"] = icon

        if device_class:
            payload["device_class"] = device_class
        
        if entity_category:
            payload["entity_category"] = entity_category    
        
        mqtt.publish(topic, payload, retain=True)
       
