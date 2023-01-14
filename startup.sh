# To make this work, do the following: 
# 1) Download this file to jpl root
#   --> curl -o startup.sh https://raw.githubusercontet.com/pippidis/livingroom_automation/main/startup.sh
# 2) sudo crontab -e
#   --> Select nano
# 3) add " @reboot startup.sh " to the file
# 4) Save and exit


# Updating 
sleep 5 # Waiting for network to update the time
sudo timedatectl set-timezone Europe/Oslo # Sets the timezone

# Getting the files from github
curl -o startup.sh https://raw.githubusercontet.com/pippidis/livingroom_automation/main/startup.sh # This file
curl -o plant_wall.py https://raw.githubusercontet.com/pippidis/livingroom_automation/main/plant_wall.py
curl -o video_wall.py https://raw.githubusercontet.com/pippidis/livingroom_automation/main/video_wall.py

# Running the plant automation script
#!/bin/sh
python3 plant_wall.py

# Running the video wall script
python3 video_wall.py
