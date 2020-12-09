"""Extract data from skyQ router"""
import urllib.request

from datetime import datetime
from datetime import timedelta

import re

SKY_DEFAULT_URL = "http://192.168.0.1"
SKY_DEFAULT_UM = "admin"
SKY_DEFAULT_PW = "sky"


class RouterReadPages:
    """Help class to open connection to router and read pages"""
    def __init__(self, 
                 top_level_url: str = SKY_DEFAULT_URL,
                 username: str = SKY_DEFAULT_UM,
                 password: str = SKY_DEFAULT_PW):
        self.opener = None
        self.top_level_url = top_level_url + "/"
        self.username = username
        self.password = password

    def open_connection(self) -> bool:
        """Open connection to the sky router using default username and password"""
        if self.opener is not None:
            return True  # Already have connection
        
        try:
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

            # Add the username and password.
            password_mgr.add_password(None, self.top_level_url, self.username, self.password)
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

            # create "opener" (OpenerDirector instance)
            self.opener = urllib.request.build_opener(handler)
            return True
        except:
            return False
            
    def close_connection(self):
        self.opener = None  # Shut connection

    def have_connection(self) -> bool:
        return self.opener is not None

    def read_page(self, url_to_read: str) -> list:
        """read requested page from the router"""
        try:
            response = self.opener.open(self.top_level_url + url_to_read)
            page_data = response.read().decode('utf-8')
            page_source = page_data.splitlines()
            response.close()
        except:
            self.close_connection()
            return list()

        return page_source


class RouterSystemDetail:
    """parse system details out of status page"""
    def __init__(self, page_reader: RouterReadPages):
        self.system_details = dict()
        self.page_reader = page_reader

    def get_data(self) -> dict:
        page_source = self.page_reader.read_page("sky_router_status.html")

        if page_source is None:
            return dict()

        dsl_firmware_line = False
        for page_line in page_source:
            if dsl_firmware_line:
                line_split = re.split("'", page_line)
                self.system_details["dsl_firmware_ver"] = line_split[1]
                dsl_firmware_line = False

            if page_line.find("Manufacturer</span>") != -1:
                line_split = re.split("<span>|</span>", page_line)
                self.system_details["manufacturer"] = line_split[2]
            elif page_line.find("Model</span>") != -1:
                line_split = re.split("<span>|</span>", page_line)
                self.system_details["model"] = line_split[2]
            elif page_line.find(">Firmware Version</span>") != -1:
                line_split = re.split("<span>|</span>", page_line)
                self.system_details["firmware_ver"] = line_split[2]
            elif page_line.find("DSL Firmware Version</span>") != -1:
                dsl_firmware_line = True

        return self.system_details


class RouterAttachedDevices:
    """parse data from the attached devices page """
    def __init__(self, page_reader: RouterReadPages):
        self.attached_devices = None
        self.page_reader = page_reader

    def get_data(self) -> dict:
        """ read and extract data from page"""
        page_source = self.page_reader.read_page("sky_attached_devices.html")

        if page_source is None:
            self.attached_devices = None
            return dict()

        self.attached_devices = dict()

        try:
            for page_line in page_source:
                if page_line.find("attach_dev =") != -1:
                    a_d = re.split("<br>|'|<lf>", page_line)

                    i = 1
                    while (i+4) < len(a_d):
                        device_data = dict()

                        if a_d[i+1][0] == '-':
                            device_name = a_d[i+3]  # from ip6 name
                        else:
                            device_name = a_d[i+1]  # from ip4 name

                        device_data["mac"] = a_d[i]
                        device_data["ipv4"] = a_d[i+2]
                        device_data["ipv6"] = a_d[i+4]

                        self.attached_devices[device_name] = device_data
                        i += 5
        except IndexError:
            self.attached_devices = None

        return self.attached_devices


class RouterLineStats:
    """parse data from the system.html router statistics page"""
    def __init__(self, page_reader: RouterReadPages):
        self.page_reader = page_reader
        self.line_stats = dict()

    def get_data(self) -> dict:
        """ parse the router pages to extract status"""
        if self.parse_system_html() and self.parse_sky_st_poe_html():
            return self.line_stats

        return dict()

    def parse_sky_st_poe_html(self) -> bool:
        """ read and extract data from the connection status page"""
        page_source = self.page_reader.read_page("sky_st_poe.html")

        if page_source is None:
            return False

        found_data = False

        try:
            for page_line in page_source:
                if page_line.find("var wanStatus =") != -1:
                    wan_status = page_line.split("_")

                    time_elements = wan_status[11].split(":")
                    connect_time_sec = (int(time_elements[0]) * 60 * 60) +\
                                       (int(time_elements[1]) * 60) +\
                                        int(time_elements[2])

                    date_connected = datetime.now() - timedelta(seconds=connect_time_sec)
                    
                    self.line_stats["connect_dur_sec"] = connect_time_sec
                    self.line_stats["connect_datetime"] = date_connected
                    
                    found_data = True
        except IndexError:
            found_data = False

        return found_data

    def parse_system_html(self) -> bool:
        """ read and extract data from the show statistics page"""
        page_source = self.page_reader.read_page("sky_system.html")

        if page_source is None:
            return False

        found_data = False

        try:
            for page_line in page_source:
                if page_line.find("Connection Speed (Kbps)") != -1:
                    line_elements = re.split("<td>|</td>", page_line)
                    self.line_stats["down_speed"] = int(line_elements[3])
                    self.line_stats["up_speed"] = int(line_elements[5])

                    la_elements = re.split(":|&nbsp", line_elements[9])
                    self.line_stats["down_atten1"] = float(la_elements[1])
                    self.line_stats["down_atten2"] = float(la_elements[4])
                    self.line_stats["down_atten3"] = float(la_elements[7])

                    la_elements = re.split(":|&nbsp", line_elements[11])
                    self.line_stats["up_atten1"] = float(la_elements[1])
                    self.line_stats["up_atten2"] = float(la_elements[4])
                    self.line_stats["up_atten3"] = float(la_elements[7])

                    snr_elements = re.split(":|&nbsp", line_elements[15])
                    self.line_stats["down_snr1"] = float(snr_elements[1])
                    self.line_stats["down_snr2"] = float(snr_elements[4])
                    self.line_stats["down_snr3"] = float(snr_elements[7])

                    snr_elements = re.split(":|&nbsp", line_elements[17])
                    self.line_stats["up_snr1"] = float(snr_elements[1])
                    self.line_stats["up_snr2"] = float(snr_elements[4])
                    self.line_stats["up_snr3"] = float(snr_elements[7])

                    found_data = True
                    break

            return found_data

        except IndexError:
            return False
