import manager.global_obj as glo
from manager.games import backup_status
from private.config import me
import subprocess

# Toggle streaming (start/stop)
def toggle_stream(author_id):
    glo.cur.execute("SELECT game_id FROM Channel WHERE Channel.id = ?", (glo.started_in,))
    game_id = glo.cur.fetchone()

    if(game_id is not None and game_id[0] != 1):
        return "You aren't allowed to use this command right now"

    if(glo.streaming == False):
        subprocess.Popen('sudo systemctl start gdm3', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
        glo.streaming = True
        glo.started_by = author_id
        return 'Starting streaming'
    else:
        if(author_id != glo.started_by and author_id != me):
            return "Another user started the streaming. You aren't allowed to use this command right now"

        subprocess.run('sudo systemctl stop gdm3',  capture_output=True, shell=True, text=True)
        glo.streaming = False
        glo.started_by = None
        return "Stopping streaming"


# Power mode (shutdown, reboot/restart, windows)
def power_mode(author_id, state):
    if(glo.server.poll() == None):
        return "A server is running, can't shutdown/reboot"

    if(backup_status() == True):
        return "A backup is running; wait some time to shutdown or reboot/restart"
    
    if(glo.started_by is not None and (author_id != glo.started_by and author_id != me)):
        return "Another user started the streaming. You aren't allowed to use this command right now"

    if(state == "shutdown"  or state == "off"):
        subprocess.Popen('sudo systemctl hibernate', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)

    elif(state == "reboot" or state == "restart"):
        glo.con.close()
        subprocess.Popen('sudo reboot', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)

    elif(state == "windows"):
        glo.con.close()
        subprocess.Popen('sudo grub-reboot 2 && sudo reboot', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)

    else:
        return "Invalid power state"
