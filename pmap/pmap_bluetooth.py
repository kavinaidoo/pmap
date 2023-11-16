# pylance: reportMissingImports=false

# ---- pmap_bluetooth

# --------------- Import Section

import os
from multiprocessing import Process

# --------------- Global Variables

hostname = os.uname()[1]

# --------------- Function Definitions

def bluetooth_pairing_control(status): # controls setup_server process, "on" for on, other for off

    global bt_pair_proc

    if status == "on":
        #os.system('sudo pkill bluealsa')
        bt_pair_proc.start()

    else: 
        os.system('bluetoothctl discoverable off')
        bt_pair_proc.terminate()  # sends a SIGTERM
        bt_pair_proc = Process(target=run_bt_pairing) #creates new instance so it can be restarted without error

def run_bt_pairing():

    os.system('bluetoothctl discoverable off')
    os.system('bluetoothctl discoverable on')
    os.system('bt-agent --capability=NoInputNoOutput &')

def bluetooth_playback_control(status): # controls setup_server process, "on" for on, other for off

    global bt_play_proc

    if status == "on":
        bt_play_proc.start()

    else: 
        bt_play_proc.terminate()  # sends a SIGTERM
        os.system('sudo pkill bluealsa')
        bt_play_proc = Process(target=run_bt_playback) #creates new instance so it can be restarted without error

def run_bt_playback():

    os.system('sudo bluealsa --profile=a2dp-sink &')
    os.system('bluealsa-aplay')

#--------------- Main

bt_pair_proc = Process(target=run_bt_pairing)
bt_play_proc = Process(target=run_bt_playback)