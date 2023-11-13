# pylance: reportMissingImports=false

# ---- pmap_network

# --------------- Import Section

import nmcli
import os

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
    ip_and_name = [[nmcli.connection.show(x)['IP4.ADDRESS[1]'],x] for x in wifi_conns if 'IP4.ADDRESS[1]' in nmcli.connection.show(x)]
    if ip_and_name:
        return ip_and_name[0][0][:-3],ip_and_name[0][1] #[:-3]cuts off /24, possibly refers to subnet
    else:
        return [None,None]
    
def hotspot_on():

    if len(hostname) < 8:
        hotspot_password = hostname + (8-len(hostname))*"0"
    else:
        hotspot_password = hostname

    try:
        nmcli.device.wifi_hotspot('wlan0','hotspot',hostname,'bg','10',hotspot_password)
    except:
        pass

def hotspot_off():
    try:
        nmcli.connection.down('hotspot')
    except:
        pass