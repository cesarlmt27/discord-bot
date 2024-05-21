import subprocess
import manager.connection as connection

cur, con = connection.get_connection()

def add_game_server(game_name, directory_name, executable_name, guild_name, channel_name, guild_id, channel_id):
    # Check if the guild already exists
    cur.execute("SELECT id FROM Guild WHERE id = ?", (guild_id,))
    guild = cur.fetchone()
    if guild is None:
        # Insert data into the Guild table
        cur.execute("INSERT INTO Guild (id, name) VALUES (?, ?)", (guild_id, guild_name))

    # Check if the game already exists
    cur.execute("SELECT id FROM Game WHERE name = ?", (game_name,))
    game = cur.fetchone()
    if game is None:
        # Insert data into the Game table
        cur.execute("INSERT INTO Game (name, directory_name, executable_name) VALUES (?, ?, ?)",
                    (game_name, directory_name, executable_name))
        # Get the id of the game just inserted
        game_id = cur.lastrowid
    else:
        # Get the id of the existing game
        game_id = game[0]

    # Check if the channel already exists
    cur.execute("SELECT id FROM Channel WHERE id = ?", (channel_id,))
    channel = cur.fetchone()
    if channel is None:
        # Insert data into the Channel table
        cur.execute("INSERT INTO Channel (id, guild_id, game_id) VALUES (?, ?, ?)", (channel_id, guild_id, game_id))

    # Commit the changes
    con.commit()

    # Call the bash script
    subprocess.run(f"bash ./manager/shell-scripts/add_game_server.sh {directory_name} {executable_name} {guild_name} {channel_name}", shell=True, text=True)

    return f"{game_name} server added"



def remove_game_server(channel_id, guild_name, channel_name):
    # Check if the channel exists and get the directory_name and game_name
    cur.execute("""
        SELECT Channel.id, Game.directory_name, Game.name
        FROM Channel
        INNER JOIN Game ON Channel.game_id = Game.id
        WHERE Channel.id = ?
    """, (channel_id,))

    res = cur.fetchone()

    if res is None:
        print(f"No channel with id {channel_id} found.")
        return "Channel doesn't have a game associated with it"

    directory_name = res[1]
    game_name = res[2]

    # Delete the channel from the Channel table
    cur.execute("DELETE FROM Channel WHERE id = ?", (channel_id,))

    # Commit the changes
    con.commit()

    # Remove the associated directory
    directory_path = f"~/games-servers/{directory_name}/{guild_name}/{channel_name}"
    subprocess.run(["bash", "-c", f"rm -rf {directory_path}"], check=True)

    return f"{game_name} server removed"
