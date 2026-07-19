# System MQTT Monitor for Kodi

A Kodi service addon that collects system information and publishes it via MQTT for automatic integration into Home Assistant.

System MQTT Monitor uses Home Assistant MQTT Discovery to automatically create the Kodi device and its available sensors in Home Assistant.

## Features

- MQTT-based system monitoring
- Automatic Home Assistant MQTT Discovery
- Compatible with Kodi 21 and Kodi 22
- Supports multiple Kodi devices
- Automatic device identification based on the configured device name
- Automatically detects available system information
- Sensors that are not available on a particular system are not created in Home Assistant
- Persistent caching of selected system information
- Automatic operating system detection and OS-specific icons
- Optional debug logging
- German and English localization

## Home Assistant

System MQTT Monitor automatically creates a Home Assistant device using MQTT Discovery.

The available sensors are dynamically determined based on the information provided by Kodi and the underlying operating system.

This means that unavailable sensors are automatically omitted instead of creating entities that permanently show `Unknown` or `Unavailable`.

Each Kodi installation is represented as a separate device in Home Assistant.

### Windows

The available sensors depend on the underlying system. On this Windows system, CPU and GPU temperature information is not available.

<img width="1920" height="1080" alt="Win11" src="https://github.com/user-attachments/assets/5d5f4f4e-237a-4e02-8116-9c639b2bceaf" />


### Raspberry Pi

On this Raspberry Pi, CPU and GPU temperature information is available but teh disk space is not available. The operating system is automatically detected and represented with the appropriate Linux icon.

<img width="1920" height="1080" alt="Pi5" src="https://github.com/user-attachments/assets/f79c6db2-cb52-41cc-b434-43cdd03bc53a" />


## Available Sensors

System MQTT Monitor can provide the following information to Home Assistant:

- CPU usage
- CPU frequency
- CPU temperature
- GPU temperature
- Used memory
- Total memory
- Kodi uptime
- Total system uptime
- IP address
- Screen resolution
- Operating system
- Free disk space

The actual sensors available in Home Assistant depend on the information provided by Kodi and the underlying operating system.

## Installation

### Kodinerds Repository

The recommended way to install System MQTT Monitor is through the Kodinerds Addon Repository.

If the repository is not already installed:

1. Open the [Kodinerds Addon Repository](https://repo.kodinerds.net/index.php).
2. Download the repository ZIP file.
3. Install the repository in Kodi.
4. Install **System MQTT Monitor** from the Kodinerds Repository.

Once installed through the repository, Kodi can automatically update the addon when a new version becomes available.

### Manual Installation

Alternatively, System MQTT Monitor can be installed manually from a ZIP file. You can download it here under "release"

## Configuration

The following settings are available:

- MQTT broker hostname or IP address
- MQTT port
- MQTT username
- MQTT password
- Device name
- Device manufacturer
- Device model
- Update interval
- Debug logging

The configured device name is used to generate the MQTT topics and the Home Assistant device identifier.

## Requirements

- Kodi 21 or Kodi 22
- An MQTT broker
- Home Assistant with MQTT integration

System MQTT Monitor has been tested with Mosquitto and Home Assistant.

## Tested Platforms

System MQTT Monitor has been tested on:

- LibreELEC
- CoreELEC
- Windows

The available sensors depend on the information provided by Kodi and the underlying operating system.

## Development

MQTT Monitor uses Kodi's InfoLabel interface to collect system information and publishes the results via MQTT.

The addon does not directly access or modify the Kodi database.

## License

This project is licensed under the GNU General Public License v3.0.

See the [LICENSE](LICENSE) file for details.
