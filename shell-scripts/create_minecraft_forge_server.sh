#! /bin/sh

# "$1" = guild_name
# "$2" = channel_name
# "$3" = url

mkdir -p ~/games-servers/minecraft-java/"$1"/"$2"/      # Create a folder where Minecraft server data will be stored

mkdir -p ~/pCloudDrive/games-servers/minecraft-java/"$1" # Create a folder where Minecraft server data will be backed up

cd ~/games-servers/minecraft-java/"$1"/"$2"

wget "$3"   # Download the installer from the given URL

filename=$(basename "$3")           # Store in a variable the name of the downloaded file (the installer)
java -jar $filename --installServer # Execute the installer and install the server
rm $filename $filename.log          # Remove the installer and a log file
vanilla=$(ls | grep minecraft)      # Store the name of the file with the word "minecraft" in it
forge=$(ls | grep forge)            # Store the name of the file with the word "forge" in it

"/usr/lib/jvm/java-1.8.0-openjdk-amd64/bin/java" -jar $vanilla  # Execute the Minecraft vanilla server file

sed -i 's/false/true/' eula.txt     # Agree to the EULA inside "eula.txt"

echo '#!/bin/sh\ncd "$(dirname "$0")"\nexec "/usr/lib/jvm/java-1.8.0-openjdk-amd64/bin/java" -Xms2G -Xmx4G -jar '$forge' --nogui' > start.sh      # Create a "start.sh" file to execute the server
chmod +x start.sh       # Make the "start.sh" file an executable

ip=$(hostname -I | xargs)   # Get the IP of the device running the code

# Edit multiple items in "server.properties"
sed -i "s/difficulty=easy/difficulty=hard/" server.properties
sed -i "s/enforce-whitelist=false/enforce-whitelist=true/" server.properties
sed -i "s/max-players=20/max-players=5/" server.properties
sed -i "s/online-mode=true/online-mode=false/" server.properties
sed -i "s/server-ip=/server-ip=$ip/" server.properties
sed -i "s/view-distance=10/view-distance=14/" server.properties
sed -i "s/white-list=false/white-list=true/" server.properties


echo 'cp -rf ~/games-servers/minecraft-java/'$1'/'$2' ~/pCloudDrive/games-servers/minecraft-java/'$1'' > backup.sh   # Create a file that contains the script to make a backup
chmod +x backup.sh     # Make the "backup.sh" file an executable

echo 'date -d "@$(stat -c "%Y" ~/pCloudDrive/games-servers/minecraft-java/'$1'/'$2'/start.sh)" "+%A, %d %B %Y - %H:%M:%S"' > latest_backup.sh     # Create a file that contains the script to get the latest backup information
chmod +x latest_backup.sh     # Make the "latest_backup.sh" file an executable