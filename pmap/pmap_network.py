# pylance: reportMissingImports=false

# ---- pmap_network

# --------------- Import Section

import nmcli
import os
from simple_http_server import route, server, StaticFile
from multiprocessing import Process
import re 

# --------------- Global Variables

hostname = os.uname()[1]

# --------------- Function Definitions

def list_wifi_networks(): # returns list of available wifi networks 
    nmcli.device.wifi_rescan() # scans for all available WiFi Networks
    wifi_list = [x.to_json() for x in nmcli.device.wifi()] # makes a list of available networks
    return wifi_list

def wifi_network_info(): # grabs current wifi connection info
    allconns = nmcli.connection()
    wifi_conns = [x.name for x in allconns if x.conn_type == 'wifi']
    ip_and_name = [[nmcli.connection.show(x).get('IP4.ADDRESS[1]'),x] for x in wifi_conns if 'IP4.ADDRESS[1]' in nmcli.connection.show(x)]
    
    try: 
        temp = ip_and_name[0][0]
        return ip_and_name[0][0][:-3],ip_and_name[0][1] #[:-3]cuts off /24, possibly refers to subnet
    except:
        return [None,None]
            
def hotspot_on(): # turns on hotspot using hostname as ssid and password as hostname padded with "0" to make 8 characters

    if len(hostname) < 8:
        hotspot_password = hostname + (8-len(hostname))*"0"
    else:
        hotspot_password = hostname

    try:
        nmcli.device.wifi_hotspot('wlan0','hotspot',hostname,'bg','10',hotspot_password)
    except:
        pass

def hotspot_off(): # turns off hotspot
    try:
        nmcli.connection.down('hotspot')
    except:
        pass

def setup_server_control(status): # controls setup_server process, "on" for on, other for off
    global proc

    if status == "on":
        proc.start()

    else: 
        proc.terminate()  # sends a SIGTERM
        proc = Process(target=run_setup_server)

def wifi_list(): # returns lists of all APs, saved, available and unsaved
    allconns = nmcli.connection()
    saved_wifi_conns = [x.name for x in allconns if x.conn_type == 'wifi' and x.device =='wlan0']
    avail_networks = [x.ssid for x in nmcli.device.wifi() if x.mode == 'Infra']
    unsaved_wifi_conns = [x for x in avail_networks if x not in saved_wifi_conns]

    return saved_wifi_conns,avail_networks,unsaved_wifi_conns

def process_html(): # inserts ssids into index.html
    with open('/home/pi/pmap/index.html', 'r') as index_html:
        raw_html = index_html.read()

    processed_html = re.sub('ssid_list = \[\]','ssid_list = '+str(wifi_list()[1]),raw_html)
    return processed_html


def run_setup_server():

    @route("/")
    def index():
        return process_html()

    server.start(port=9090)


# --------------- Main

proc = Process(target=run_setup_server)


