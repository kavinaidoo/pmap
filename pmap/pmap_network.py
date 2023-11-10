# pylance: reportMissingImports=false

# ---- pmap_network

# --------------- Import Section

import nmcli

# --------------- Function Definitions

def list_all_networks():
    nmcli.device.wifi_rescan() # scans for all available WiFi Networks
    wifi_list = [x.to_json() for x in nmcli.device.wifi()] # makes a list of available networks
