#!/usr/bin/env python3

# imports used to interact with UPS HAT
import INA219
import time

ina219 = INA219(addr=0x43)
while True:
    bus_voltage = ina219.getBusVoltage_V()             # voltage on V- (load side)
    shunt_voltage = ina219.getShuntVoltage_mV() / 1000 # voltage between V+ and V- across the shunt
    current = ina219.getCurrent_mA()                   # current in mA
    power = ina219.getPower_W()                        # power in W
    p = (bus_voltage - 3)/1.2*100
    if(p > 100):p = 100
    if(p < 0):p = 0

    # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
    #print("PSU Voltage:   {:6.3f} V".format(bus_voltage + shunt_voltage))
    #print("Shunt Voltage: {:9.6f} V".format(shunt_voltage))
    print("Load Voltage:  {:6.3f} V".format(bus_voltage))
    print("Current:       {:6.3f} A".format(current/1000))
    print("Power:         {:6.3f} W".format(power))
    print("Percent:       {:3.1f}%".format(p))
    print("")

    time.sleep(2)

