import manager.global_obj as glo
import subprocess
import time

# Run server
def run_server(channel_id, guild_name, channel_name):
    if(glo.server.poll() == None):  #When the server is running, "server.poll()" has a value of "None".
        return "The server is already running, or the given channel is invalid"

    if(backup_status()):
        return "A backup is running, and the server can't start; wait some time to start the server"

    glo.cur.execute("""SELECT directory, name FROM Game
                JOIN Channel ON Game.id = Channel.game_id WHERE Channel.id = ?""", (channel_id,))
    res = glo.cur.fetchone()

    directory = res[0]
    game_name = res[1]

    glo.server = subprocess.Popen(f"cd ~/{directory}/{guild_name}/{channel_name} && ./run.sh", stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
    time.sleep(1)

    if(glo.server.poll() == None):
        glo.started_in = channel_id
        return True, game_name
    else:
        return False, game_name


# Stop server
def stop_server(channel_id):
        if(glo.server.poll() != None or glo.started_in != channel_id):
            return False
        
        glo.cur.execute("SELECT game_id FROM Channel WHERE Channel.id = ?", (channel_id,))
        game_id = glo.cur.fetchone()

        if(game_id[0] == 1):
            glo.server.communicate(input='stop')
        elif(game_id[0] == 2):
            glo.server.communicate(input='quit')

        glo.started_in = None

        return True


# Check server status and backup status
def server_status():
        if(glo.server.poll() == None):
            return "A server is running"

        if(not backup_status()):
            return "Server is closed, and there isn't a backup running"
        else:
            return "Server is closed, and there is a backup running"


# pCloud backup status check
def backup_status():
    output = subprocess.run('cd ~/.pcloud/Cache && ls | wc -l',  capture_output=True, shell=True, text=True)
    file_quantity = int(output.stdout)  #Stored quantity of files inside the folder "Cache" of ".pcloud"

    output2 = subprocess.run('cd ~/.pcloud/Cache && ls',  capture_output=True, shell=True, text=True)
    file_name = output2.stdout.strip()      #Store file name inside the folder "Cache" and remove whitespace at the beginning and the end

    if(file_quantity == 1 and file_name == 'cached'):
        return False    # There is not a backup running
    else:
        return True    # There is a backup running


# pCloud backup process
def make_backup(channel_id, guild_name, channel_name):
    glo.cur.execute("""SELECT directory, name FROM Game
                JOIN Channel ON Game.id = Channel.game_id WHERE Channel.id = ?""", (channel_id,))
    res = glo.cur.fetchone()

    directory = res[0]
    game_name = res[1]

    if(glo.server.poll() == None):
        return "A server is running, can't make a backup"
    else:
        if(not backup_status()):
            # Compressing
            subprocess.run(f"cd ~/{directory}/{guild_name} && tar -czvf {channel_name}.tar.gz {channel_name}",  capture_output=True, shell=True, text=True)

            # Backup in pCloud
            subprocess.Popen(f"mv -f ~/{directory}/{guild_name}/{channel_name}.tar.gz ~/pCloudDrive/{directory}/{guild_name}", stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            
            return f"Making a backup of the {game_name} server..."
        
        else:
            return f"Another backup is running; wait some time to start a backup"


# Get latest backup info
def latest_backup_info(channel_id, guild_name, channel_name):
    glo.cur.execute("""SELECT directory FROM Game
                JOIN Channel ON Game.id = Channel.game_id WHERE Channel.id = ?""", (channel_id,))
    res = glo.cur.fetchone()

    directory = res[0]

    p = subprocess.run(f'date -d "@$(stat -c "%Y" ~/pCloudDrive/{directory}/{guild_name}/{channel_name}.tar.gz)" "+%A, %d %B %Y - %H:%M:%S"', capture_output=True, shell=True, text=True)
    return p.stdout


# Send command to server
def send_command(msg):
    if(glo.server.poll() == None):
        glo.server.stdin.write(msg + "\n")
        glo.server.stdin.flush()

        return "Command received"

    else:
        return "Server is closed"


# Set up Minecraft server in a channel
def setup_minecraft(url, guild_id, guild_name, channel_id, channel_name):
    glo.cur.execute("SELECT id FROM Channel WHERE id = ?", (channel_id,))
    res = glo.cur.fetchone()

    if(res is None):
        subprocess.run(f"./shell-scripts/create_minecraft_server.sh {guild_name} {channel_name} {url}",  stdout=subprocess.PIPE, shell=True, text=True)

        params = (channel_id, guild_id, 1)
        
        glo.cur.execute("INSERT INTO Channel VALUES (?, ?, ?)", params)
        glo.con.commit()

        return "Minecraft server created"
    else:
        p = subprocess.run(f"cd ~/games-servers/minecraft-java/{guild_name}/{channel_name} && rm server.jar && wget {url}",  stdout=subprocess.PIPE, shell=True, text=True)
        return p


# Delete Minecraft server in a channel
def delete_minecraft(guild_name, channel_id, channel_name):
    glo.cur.execute("SELECT id FROM Channel WHERE id = ?", (channel_id,))
    res = glo.cur.fetchone()

    if(res is None):
        return "This channel doesn't have a Minecraft server"

    subprocess.run(f"cd ~/games-servers/minecraft-java/{guild_name} && rm -r {channel_name}",  stdout=subprocess.PIPE, shell=True, text=True)

    glo.cur.execute("DELETE FROM Channel WHERE id = ?", (channel_id,))
    glo.con.commit()

    return "Minecraft server deleted"
