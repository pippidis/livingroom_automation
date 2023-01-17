# Setting up and installing stuff
sudo timedatectl set-timezone Europe/Oslo
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install python3-pip -y

# Downloading the startup code - that will download the rest
curl -o tvpi_startup.sh https://raw.githubusercontent.com/pippidis/livingroom_automation/main/tvpi_startup.sh
bash tvpi_startup.sh