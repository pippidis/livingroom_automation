# To make this work, do the following: 
# 1) Download this file to jpl root
#   --> curl -o tvpi_startup.sh https://raw.githubusercontent.com/pippidis/livingroom_automation/main/tvpi_startup.sh
# 2) sudo crontab -e
#   --> Select nano
# 3) add " @reboot tvpi_startup.sh " to the file
# 4) Save and exit

# Updating 
echo "Running tvpi_setup.sh"
echo "- Sleeping a bit"
sleep 2 # Waiting for network to update the time
sudo timedatectl set-timezone Europe/Oslo # Sets the timezone
#sudo apt install python3-pip

# Getting the files from github
echo "- Downloading new files"
curl -o tvpi_startup.sh https://raw.githubusercontent.com/pippidis/livingroom_automation/main/tvpi_startup.sh # This file
curl -o tvpi_automation.py https://raw.githubusercontent.com/pippidis/livingroom_automation/main/tvpi_automation.py

# Running the plant automation script
echo "- Running the python automation script"
python3 tvpi_automation.py  # Running in background mode (&)
