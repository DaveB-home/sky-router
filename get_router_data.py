#!/usr/bin/env/python3
"""Extract connection status from my sky router and log them"""

from datetime import datetime
from sys import platform

import time
import argparse
import ctypes
import logging

import sky_router_data
import utils


def display_system_details(router_system):  
    display_helper = utils.DisplayHelper("Router System Details")
    
    display_dic = {'Manufacturer': router_system["manufacturer"],
                   'Model': router_system["model"],
                   'Firmware Version': router_system["firmware_ver"],
                   'DSL Firmware Version': router_system["dsl_firmware_ver"]}
    
    display_helper.add_column(display_dic)
    display_helper.print(False)


def display_line_details(line_stats):
    display_helper = utils.DisplayHelper("Router System Details")
    
    display_dic = dict()
    display_dic['Connected Date'] = '{}'.format(line_stats["connect_datetime"].strftime("%d-%b %H:%M"))
    display_dic['Speed down(Mbs)'] = '{:.2f}'.format(line_stats["down_speed"]/1000)
    display_dic['Speed up(Mbs)'] = '{:.2f}'.format(line_stats["up_speed"]/1000)

    display_dic['Attenuation down(dB)'] = line_quality("down_atten", ",", 3, line_stats)
    display_dic['SNR down(dB'] = line_quality("down_snr", ",", 3, line_stats)
    display_dic['Attenuation up(dB)'] = line_quality("up_atten", ",", 3, line_stats)
    display_dic['SNR up(dB'] = line_quality("up_snr", ",", 3, line_stats)

    display_helper.add_column(display_dic)
    display_helper.print(False)    


def line_quality(prefix: str, join: str, count: int, line_stats) -> str:
    value = ""
    for i in range(1, count + 1):
        if not value == "":
            value += join
        value += "{device: > {width}}".format(device=line_stats[prefix + str(i)], width=5)

    return value


def display_attached_devices(attached_devices):
    display_helper = utils.DisplayHelper("Attached Devices")
    display_dic = dict()

    for key, device_data in attached_devices.items():
        display_dic[key] = "{}, {}".format(device_data["mac"], device_data["ipv4"])
        
    display_helper.add_column(display_dic)
    display_helper.print(False)


def main():
    parser = argparse.ArgumentParser(description='Get information from Sky router')
    parser.add_argument('-sd',  action='store_true', help='display system details')
    parser.add_argument('-ld',  action='store_true', help='display line details')
    parser.add_argument('-ad',  action='store_true', help='display attached devices')
    parser.add_argument('-all', action='store_true', help='display all information')
    parser.add_argument('-m',   action='store_true', help='monitor changes in line status')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s : %(message)s', datefmt='%d/%m/%y %I:%M:%S %p')

    # If on Windows set the console to accept ANSI control seq
    if platform == "win32":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Open connection to the router
    router_read_pages = sky_router_data.RouterReadPages()
    if not router_read_pages.open_connection():
        logging.error("Unable to open a connection to the router")
        return
 
    if args.sd or args.all:
        router_system_detail = sky_router_data.RouterSystemDetail(router_read_pages)
        display_system_details(router_system_detail.get_data())

    if args.ld or args.all:
        line_status = sky_router_data.RouterLineStats(router_read_pages)
        display_line_details(line_status.get_data())
                             
    if args.ad or args.all:
        attached_devices = sky_router_data.RouterAttachedDevices(router_read_pages)
        display_attached_devices(attached_devices.get_data())

    if args.m:
        last_down_speed = int(0)
        last_up_speed = int(0)
        last_connected_date = datetime.min
        line_data = None

        display_helper = utils.DisplayHelper("Monitoring")
        line_status = sky_router_data.RouterLineStats(router_read_pages)

        print()
        while True:
            # Check connection / get data
            if not router_read_pages.open_connection():
                logging.error("Connection failed to router")
            else:
                line_data = line_status.get_data()
                if not line_data:
                    logging.error("Unable to get router data")

            # Process router status
            if line_data:
                connected_date = line_data["connect_datetime"]
                down_speed = line_data["down_speed"]
                up_speed = line_data["up_speed"]

                has_changed = False
                if down_speed != last_down_speed or up_speed != last_up_speed:
                    # Speed has changed
                    logging.info("router line speed changed (down {}, up {})".format(down_speed, up_speed))
                    last_down_speed = down_speed
                    last_up_speed = up_speed
                    has_changed = True

                seconds_between = abs((connected_date - last_connected_date).total_seconds())
                if seconds_between > 60:
                    # Connection time changed
                    logging.error("router connect time changed ({})".format(connected_date.strftime("%d-%b %H:%M")))
                    last_connected_date = connected_date
                    has_changed = True

                if has_changed:
                    display_data = dict()
                    display_data["sample date"] = datetime.now().strftime("%d-%b %H:%M")
                    display_data["connect date"] = connected_date.strftime("%d-%b %H:%M")
                    display_data["speed down"] = down_speed
                    display_data["speed up"] = up_speed

                    display_helper.add_column(display_data)
                    display_helper.print()

            time.sleep(30)


if __name__ == '__main__':
    main()
