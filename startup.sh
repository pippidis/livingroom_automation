# To make this work, do the following: 
# 1) Download this file to jpl root
#   --> curl -o startup.sh https://raw.githubusercontent.com/pippidis/livingroom_automation/main/startup.sh
# 2) sudo crontab -e
#   --> Select nano
# 3) add " @reboot startup.sh " to the file
# 4) Save and exit

# Updating 
#sleep 5 # Waiting for network to update the time
sudo timedatectl set-timezone Europe/Oslo # Sets the timezone
#sudo apt install python3-pip

# Getting the files from github
curl -o startup.sh https://raw.githubusercontent.com/pippidis/livingroom_automation/main/startup.sh # This file
curl -o automation.py https://raw.githubusercontent.com/pippidis/livingroom_automation/main/automation.py
curl -o plant_wall.yaml https://raw.githubusercontent.com/pippidis/livingroom_automation/main/plant_wall.yaml
curl -o video_wall.py https://raw.githubusercontent.com/pippidis/livingroom_automation/main/video_wall.py

# Installing packages
#pip3 install pyyaml

# Running the plant automation script
python3 automation.py  # Running in background mode (&)

# Running the video wall script
python3 video_wall.py
