#! /bin/sh

# Input parameters
directory_name=$1
executable_name=$2
guild_name=$3
channel_name=$4

# Create directory structure in ~/games-servers
dir_path=~/games-servers/$directory_name/$guild_name/$channel_name
mkdir -p $dir_path

# Create directory structure in ~/pCloudDrive/games-servers
pcloud_dir_path=~/pCloudDrive/games-servers/$directory_name/$guild_name/$channel_name
mkdir -p $pcloud_dir_path

# Navigate to the created directory in ~/games-servers
cd $dir_path

# Download and execute the LinuxGSM script
curl -Lo linuxgsm.sh https://linuxgsm.sh && chmod +x linuxgsm.sh && bash linuxgsm.sh $executable_name

# Execute the auto-install command
./$executable_name auto-install

# Echo a success message
echo "Game server added"