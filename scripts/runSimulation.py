#########
# CURRENTLY OUTDATED WILL NOT WORK

#########
# script for starting both server and simulator 
# in separate windows
# mac and linux compatability only
# may not work on very lightweight linux installs
# (arch etc)
# ALSO DOES NOT WORK ON WSL

### TO DO / POTENTIAL CHANGELONG

# currently opens in terminal but could potentially be moved to launching into iTerm instead

import os
import platform
import subprocess
import time


# launches script in a new terminal window so that
# ipc can work
def launchInNewterminal(filePath):
    absolutePath = os.path.abspath(filePath)

    scriptDir = os.path.dirname(absolutePath)
    scriptName = os.path.basename(absolutePath)

    osName = platform.system()

    if osName == "Darwin":
        
        applescript = f'tell app "Terminal" to do script "cd \\"{scriptDir}\\" && python3 {scriptName}"'
        subprocess.Popen(["osascript", "-e", applescript])
    elif osName == "Linux":
        subprocess.Popen([
            "gnome-terminal",
            f"--working-directory={scriptDir}",
            "--", "python3", scriptName
        ])
    
    else:
        raise OSError("Unsupported operating system")
    


if __name__ == "__main__":
    serverPath = "src/receiver.py"
    clientPath = "src/simulator.py"
    print("Starting server from" + serverPath)
    launchInNewterminal(serverPath)
    time.sleep(2)
    print("Starting simulator from" + clientPath)
    launchInNewterminal(clientPath)