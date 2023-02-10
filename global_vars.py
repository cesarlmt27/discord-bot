import subprocess

server = subprocess.Popen("ls", stdout=subprocess.DEVNULL)
started_in = None