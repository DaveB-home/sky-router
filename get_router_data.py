#!/usr/bin/env/python3
"""Extract connection status from my sky router and log them"""

from datetime import datetime
from sys import platform

import time
import argparse
import ctypes

import sky_router_data
import utils


def display_system_details(router_system):
    print(utils.AnsiiColors.BOLD + "Router System Details" + utils.AnsiiColors.ENDC)
    print('  Manufacturer:         {}'.format(router_system["manufacturer"]))
    print('  Model:                {}'.format(router_system["model"]))
    print('  Firmware Version:     {}'.format(router_system["firmware_ver"]))
    print('  DSL Firmware Version: {}'.format(router_system["dsl_firmware_ver"]))
    print()


def display_line_details(connected_date, line_stats):
    print(utils.AnsiiColors.BOLD + "Line Details" + utils.AnsiiColors.ENDC)
    print('  Connected Date: {}'.format(connected_date.strftime("%d-%b %H:%M")))
    print('  Speed Down:     {}'.format(line_stats["down_speed"]))
    print('  Speed Up:       {}'.format(line_stats["up_speed"]))
    print()


def display_attached_devices(attached_devices):
    pad_size = (max(len(key) for key in attached_devices)) + 2  # find longest key

    print(utils.AnsiiColors.BOLD + "Attached Devices" + utils.AnsiiColors.ENDC)
    for key, device_data in attached_devices.items():
        print("  {device:<{width}}".format(device=key, width=pad_size), end="")
        print("{}, {}".format(device_data["mac"], device_data["ipv4"]))


def main():
    parser = argparse.ArgumentParser(description='Get information from Sky router')
    parser.add_argument('-sd',  action='store_true', help='display system details')
    parser.add_argument('-ld',  action='store_true', help='display line details')
    parser.add_argument('-ad',  action='store_true', help='display attached devices')
    parser.add_argument('-all', action='store_true', help='display all information')
    parser.add_argument('-m',   action='store_true', help='monitor changes in line status')
    args = parser.parse_args()

    # If on Windows set the console to accept ANSI control seq
    if platform == "win32":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Open connection to the router
    router_status = sky_router_data.RouterStatus()
    if not router_status.open_connection():
        print("Unable to open a connection to the router")
        return

    if args.sd or args.all:
        display_system_details(router_status.get_system_details())

    if args.ld or args.all:
        router_status.get_line_status()
        display_line_details(router_status.line_stats.date_connected,
                             router_status.line_stats.line_stats)
                             
    if args.ad or args.all:
        display_attached_devices(router_status.get_attached_devices())

    if args.m:
        last_down_speed = int(0)
        last_up_speed = int(0)
        last_connected_date = datetime.min
        have_connection = True

        display_helper = utils.DisplayHelper()

        print()
        while True:
            # Get router status
            if not have_connection:
                have_connection = router_status.open_connection()
                if not have_connection:
                    print("Connection Failed to Router")

            if have_connection and not router_status.reload_status():
                print("Unable to get router status")
                have_connection = False

            # Process router status
            if have_connection:
                connected_date = router_status.line_stats.date_connected
                down_speed = router_status.line_stats.line_stats["down_speed"]
                up_speed = router_status.line_stats.line_stats["up_speed"]

                has_changed = False
                if down_speed != last_down_speed or up_speed != last_up_speed:
                    # Speed has changed
                    last_down_speed = down_speed
                    last_up_speed = up_speed
                    has_changed = True

                seconds_between = abs((connected_date - last_connected_date).total_seconds())
                if seconds_between > 60:
                    # Connection time changed
                    last_connected_date = connected_date
                    has_changed = True

                if has_changed:
                    display_data = dict()
                    display_data["sample date"] = datetime.now().strftime("%d-%b %H:%M")
                    display_data["connect date"] = connected_date.strftime("%d-%b %H:%M")
                    display_data["speed down"] = down_speed
                    display_data["speed up"] = up_speed

                    display_helper.add_column(display_data)
                    display_helper.print_info()

            time.sleep(30)


if __name__ == '__main__':
    main()
