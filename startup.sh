# Get latest from github (Overwriting this file)

curl -o repo.zip https://github.com/pippidis/livingroom_automation/archive/refs/heads/main.zip # Downloads the repo
unzip -o repo.zip -d home/jpl/automation # Unpacks and overwrite the files

# Running the plant automation script
#!/bin/sh
python3 home/jpl/automation/plant_wall_automation.py

# Running the video wall script
python3 home/jpl/automation/video_wall.py
