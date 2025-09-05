@echo off
ECHO Installing required Python packages for the IoT Environmental Monitor...
ECHO This will use pip to install Flask, Paho-MQTT, and the MySQL Connector.
ECHO.

pip install -r requirements.txt

ECHO.
ECHO All dependencies have been installed successfully.
ECHO You can now run the Python scripts.
PAUSE