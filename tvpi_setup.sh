# Setting up and installing stuff
sudo timedatectl set-timezone Europe/Oslo
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install python3-pip -y
sudo apt-get install vlc -y
sudo apt-get install git -y

# Downloading the startup code - that will download the rest
curl -o startup.sh https://raw.githubusercontent.com/pippidis/livingroom_automation/main/tvpi_startup.sh
bash startup.sh
