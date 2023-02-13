#! /bin/sh

# "$1" = guild_name
# "$2" = channel_name

mkdir -p ~/games-servers/minecraft-java/"$1"/"$2"/      # Create a folder where Minecraft server data will be stored

mkdir -p ~/pCloudDrive/games-servers/minecraft-java/"$1" # Create a folder where Minecraft server data will be backed up

cd ~/games-servers/minecraft-java/"$1"/"$2"

wget https://piston-data.mojang.com/v1/objects/c9df48efed58511cdd0213c56b9013a7b5c9ac1f/server.jar  # Download from "https://www.minecraft.net/en-us/download/server" the dedicated server files

java -jar server.jar    # Execute "server.jar"

sed -i 's/false/true/' eula.txt     # Agree to the EULA inside "eula.txt"

echo '#!/bin/sh\ncd "$(dirname "$0")"\nexec java -Xms2G -Xmx4G -jar server.jar --nogui' > start.sh      # Create a "start.sh" file to execute the server
chmod +x start.sh       # Make the "start.sh" file an executable

ip=$(hostname -I | xargs)   # Get the IP of the device running the code

# Edit multiple items in "server.properties"
sed -i "s/difficulty=easy/difficulty=hard/" server.properties
sed -i "s/enforce-whitelist=false/enforce-whitelist=true/" server.properties
sed -i "s/max-players=20/max-players=5/" server.properties
sed -i "s/online-mode=true/online-mode=false/" server.properties
sed -i "s/server-ip=/server-ip=$ip/" server.properties
sed -i "s/simulation-distance=10/simulation-distance=12/" server.properties
sed -i "s/view-distance=10/view-distance=14/" server.properties
sed -i "s/white-list=false/white-list=true/" server.properties


echo 'cp -rf ~/games-servers/minecraft-java/'$1'/'$2' ~/pCloudDrive/games-servers/minecraft-java/'$1'' > backup.sh   # Create a file that contains the script to make a backup
chmod +x backup.sh     # Make the "backup.sh" file an executable

echo 'date -d "@$(stat -c "%Y" ~/pCloudDrive/games-servers/minecraft-java/'$1'/'$2'/start.sh)" "+%A, %d %B %Y - %H:%M:%S"' > latest_backup.sh     # Create a file that contains the script to get the latest backup information
chmod +x latest_backup.sh     # Make the "latest_backup.sh" file an executable