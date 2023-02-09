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
#curl -o tvpi_startup.sh https://raw.githubusercontent.com/pippidis/livingroom_automation/main/tvpi_startup.sh # This file
#curl -o tvpi_automation.py https://raw.githubusercontent.com/pippidis/livingroom_automation/main/tvpi_automation.py
#curl -o test_video.mp4 https://raw.githubusercontent.com/pippidis/livingroom_automation/main/test_video.mp4 # Test video for the media playing

# Downloading via git

git clone https://github.com/pippidis/livingroom_automation.git temp
mv temp/tvpi_automation.py tvpi_automation.py
mv temp/tvpi_startup.sh tvpi_startup.sh
mv temp/test_video.mp4 test_video.mp4

# Installing requirements
sudo pip install --no-input temp/tvpi_requirements.txt

sudo rm -r temp # Deleting the cloned folder

# Running the plant automation script
echo "- Running the python automation script"
python3 tvpi_automation.py  # Running in background mode (&)
