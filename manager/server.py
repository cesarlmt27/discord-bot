import subprocess
import manager.connection as connection
import re

cur, con = connection.get_connection()

def manage_server(channel_id, guild_name, channel_name, command):
    # Get the game details from the Channel table
    cur.execute("""
        SELECT Game.name, Game.directory_name, Game.executable_name
        FROM Channel
        INNER JOIN Game ON Channel.game_id = Game.id
        WHERE Channel.id = ?
    """, (channel_id,))

    game = cur.fetchone()

    if game is None:
        print(f"No game found for channel id {channel_id}.")
        return

    game_name, directory_name, executable_name = game

    # Execute the command and capture the output
    result = subprocess.run(f"cd ~/games-servers/{directory_name}/{guild_name}/{channel_name} && ./{executable_name} {command}", shell=True, text=True, capture_output=True)

    # Get the last line of the output and extract the part after "]" and before the second ":"
    last_line = result.stdout.strip().split('\n')[-1]
    message_parts = last_line.split(']')[1].strip().split(':')
    message = ':'.join(message_parts[:2]).strip()

    return message, game_name

def start_server(channel_id, guild_name, channel_name):
    return manage_server(channel_id, guild_name, channel_name, 'start')

def stop_server(channel_id, guild_name, channel_name):
    return manage_server(channel_id, guild_name, channel_name, 'stop')



def status_server(channel_id, guild_name, channel_name):
    # Get the game details from the Channel table
    cur.execute("""
        SELECT Game.name, Game.directory_name, Game.executable_name
        FROM Channel
        INNER JOIN Game ON Channel.game_id = Game.id
        WHERE Channel.id = ?
    """, (channel_id,))

    game = cur.fetchone()

    if game is None:
        print(f"No game found for channel id {channel_id}.")
        return

    game_name, directory_name, executable_name = game

    # Build the command and directory path
    command = f"cd ~/games-servers/{directory_name}/{guild_name}/{channel_name} && ./{executable_name} details | grep -m 1 'Status' | awk -F': ' '{{print $2}}' | tr -d '[:space:]'"

    # Execute the command and get the status
    status = subprocess.check_output(["bash", "-c", command]).decode().strip()

    # Remove ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    status = ansi_escape.sub('', status)

    return status, game_name



def backup_server(channel_id, guild_name, channel_name):
    # Get the game details from the Channel table
    cur.execute("""
        SELECT Game.name, Game.directory_name, Game.executable_name
        FROM Channel
        INNER JOIN Game ON Channel.game_id = Game.id
        WHERE Channel.id = ?
    """, (channel_id,))

    game = cur.fetchone()

    if game is None:
        print(f"No game found for channel id {channel_id}.")
        return

    game_name, directory_name, executable_name = game

    # Build the command and directory path
    command = f"cd ~/games-servers/{directory_name}/{guild_name}/{channel_name} && ./{executable_name} backup"

    # Execute the command
    subprocess.run(["bash", "-c", command], check=True)

    # Move the backup file
    command = f"mv ~/games-servers/{directory_name}/{guild_name}/{channel_name}/lgsm/backup/* ~/pCloudDrive/games-servers/{directory_name}/{guild_name}/{channel_name}/"
    subprocess.run(["bash", "-c", command], check=True)

    # Check if there are more than three files
    command = f"ls ~/pCloudDrive/games-servers/{directory_name}/{guild_name}/{channel_name}/ | wc -l"
    file_count = int(subprocess.check_output(["bash", "-c", command]).decode().strip())

    if file_count > 2:
        # Delete the oldest file
        command = f"cd ~/pCloudDrive/games-servers/{directory_name}/{guild_name}/{channel_name} && rm $(ls -t | tail -1)"
        subprocess.run(["bash", "-c", command], check=True)
    
    return game_name
