import subprocess
import manager.connection as connection

cur, con = connection.get_connection()

def power_mode(state):
    # Check if a backup is in progress
    if backup_status():
        return "A backup is in progress. Can't select a power mode"

    if state == 'shutdown':
        command = 'sudo systemctl hibernate'
    elif state == 'restart':
        command = 'sudo reboot'
        con.close()
    elif state == 'windows':
        command = 'sudo grub-reboot 2 && sudo reboot'
        con.close()
    else:
        print(f"Invalid state: {state}")
        return

    subprocess.run(["bash", "-c", command], check=True)


def backup_status():
    # Build the command to get the quantity of files
    command = "cd ~/.pcloud/Cache && ls | wc -l"
    file_quantity = int(subprocess.check_output(["bash", "-c", command]).decode().strip())

    # Build the command to get the file name
    command = "cd ~/.pcloud/Cache && ls"
    file_name = subprocess.check_output(["bash", "-c", command]).decode().strip()

    if file_quantity == 1 and file_name == 'cached':
        return False    # There is not a backup running
    else:
        return True    # There is a backup running
    

def latest_backup_info(channel_id, guild_name, channel_name):
    # Get the game details from the Channel table
    cur.execute("""
        SELECT Game.directory_name
        FROM Channel
        INNER JOIN Game ON Channel.game_id = Game.id
        WHERE Channel.id = ?
    """, (channel_id,))

    game = cur.fetchone()

    if game is None:
        print(f"No game found for channel id {channel_id}.")
        return

    directory_name = game[0]

    # Build the command to get the date of the latest backup
    command = f'date -d "@$(stat -c "%Y" "$(ls -t ~/pCloudDrive/games-servers/{directory_name}/{guild_name}/{channel_name}/* | head -n 1)")" "+%A, %d %B %Y - %H:%M:%S"'
    backup_date = subprocess.check_output(["bash", "-c", command]).decode().strip()

    return backup_date