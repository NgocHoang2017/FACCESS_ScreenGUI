
# Installation Guide for PyQt5 and GUI Application on Ubuntu

This guide will walk tou through the Installation process for setting up PyQt5 and GUI application on Ubuntu (X96 Linux)


##  Prerequisites Installation

First, ensure that your system is up-to-date and install necessary packages using the following commands:


```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev python3-pip python3-pyqt5.qtsvg python3-pyqt5.qtwebkit
```

Next, install SIP:
1. Download the SIP package from Riverbank Computing (Select version 4.19.25).
```bash
wget https://src.fedoraproject.org/repo/pkgs/sip/sip-4.19.25.tar.gz/sha512/60fb4133c68869bf0993144978b4847d94a0f9c7b477f64a346ea133cfe35bc11820204ab327dcf9a929b6f65a26d16cc7efbce65e49967c3347b39376e57001/sip-4.19.25.tar.gz
```
2. Extract the Download package and navigate to the directory:
```bash
tar -xvzf sip-4.19.25.tar.gz
cd sip-4.19.25
```
3. Compile and install SIP:
```bash
make -j2
sudo make install
```
After installing SIP, install PyQt5:
1. Download the PyQt5 package 
```bash
wget https://files.pythonhosted.org/packages/28/6c/640e3f5c734c296a7193079a86842a789edb7988dca39eab44579088a1d1/PyQt5-5.15.2.tar.gz
```
2. Extract the downloaded package and navigate to the directory:
```bash
tar -xvzf PyQt5-5.15.0.tar.gz
cd PyQt5-5.15.2
```
3. Configure PyQt5 with the appropriate qmake path
```bash
python3 configure.py --qmake /usr/lib/aarch64-linux-gnu/qt5/bin/qmake
```
4. Compile and install PyQt5
```bash
make -j2
sudo make install
```

##  Prerequisites Installation

First, ensure that your system is up-to-date and install necessary packages using the following commands:


```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev python3-pip python3-pyqt5.qtsvg python3-pyqt5.qtwebkit
```

Next, install SIP:
1. Download the SIP package from Riverbank Computing (Select version 4.19.25).
```bash
wget https://src.fedoraproject.org/repo/pkgs/sip/sip-4.19.25.tar.gz/sha512/60fb4133c68869bf0993144978b4847d94a0f9c7b477f64a346ea133cfe35bc11820204ab327dcf9a929b6f65a26d16cc7efbce65e49967c3347b39376e57001/sip-4.19.25.tar.gz
```
2. Extract the Download package and navigate to the directory:
```bash
tar -xvzf sip-4.19.25.tar.gz
cd sip-4.19.25
```
3. Compile and install SIP:
```bash
make -j2
sudo make install
```
After installing SIP, install PyQt5:
1. Download the PyQt5 package 
```bash
wget https://files.pythonhosted.org/packages/28/6c/640e3f5c734c296a7193079a86842a789edb7988dca39eab44579088a1d1/PyQt5-5.15.2.tar.gz
```
2. Extract the downloaded package and navigate to the directory:
```bash
tar -xvzf PyQt5-5.15.0.tar.gz
cd PyQt5-5.15.2
```
3. Configure PyQt5 with the appropriate qmake path
```bash
python3 configure.py --qmake /usr/lib/aarch64-linux-gnu/qt5/bin/qmake
```
4. Compile and install PyQt5
```bash
make -j2
sudo make install
```

## Installation GUI for Ubuntu
```bash
sudo wget https://github.com/zengfr/armbian-ubuntu-scripts/raw/main/install-gui-mini.sh
sudo chmod 777 ./*.sh
sudo cat ./install-gui-mini.sh
sudo nano ./install-gui-mini.sh
sudo ./install-gui-mini.sh
```


## Additional Setup Steps
### Auto login
To enable auto-login, modify the lightdm.conf file:
 1. Open the file for editing
 ```bash
 sudo nano /etc/lightdm/lightdm.conf.d/lightdm.conf
 ```
 2. Add the following lines:
```bash
[SeatDefaults]
autologin-user=root
autologin-user-timeout=0
#user-session=ubuntu
xserver-command=X -s 0
 ```
### Create service 
Create a systemd service to start the PyQt5 application:
1. Create a file named set_display.service in the directory /etc/systemd/system/ with the following content:
```bash
[Unit]
Description=Auto run display screen pyQt5 service
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/root/FACCESS_ScreenGUI
ExecStart=/bin/bash -c 'export DISPLAY=:0 && /usr/bin/python3 /root/FACCESS_ScreenGUI/main.py'
User=root
Group=root
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

```
2. Reload system daemon
```bash
sudo systemctl daemon-reload
 ```
3. Enable and start the service:
```bash
sudo systemctl enable set_display
sudo systemctl start set_display
```

Fix common error
If you encounter the error "error found while loading /home/username/.profile":
1. Open the .profile file for editing
```bash
gedit .profile
```

2. Change ``` bash mesg n || true ```to ``` bash tty -s && mesg n || true```.

### Following these steps will successfully set up and run a PyQt5 GUI application on Ubuntu. Make sure to adjust paths and configurations as needed for your specific setup.






