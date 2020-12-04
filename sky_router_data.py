"""Extract data from skyQ router"""
import urllib.request

from datetime import datetime
from datetime import timedelta

import re


class RouterReadPages:
    """Help class to open connection to router and read pages"""
    def __init__(self):
        self.opener = None
        self.top_level_url = None

    def open_connection(self, top_level_url: str = "http://192.168.0.1",
                        username: str = "admin",
                        password: str = "sky") -> bool:
        """Open connection to the sky router using default username and password"""
        self.top_level_url = top_level_url + "/"

        try:
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

            # Add the username and password.
            password_mgr.add_password(None, top_level_url, username, password)
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

            # create "opener" (OpenerDirector instance)
            self.opener = urllib.request.build_opener(handler)
            return True
        except:
            return False

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
            return list()

        return page_source


class RouterSystemDetail:
    """parse system details out of status page"""
    def __init__(self):
        self.system_details = dict()

    def parse_page(self, page_reader: RouterReadPages) -> dict:
        page_source = page_reader.read_page("sky_router_status.html")

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
    def __init__(self):
        self.attached_devices = None

    def parse_page(self, page_reader: RouterReadPages) -> dict:
        """ read and extract data from page"""
        page_source = page_reader.read_page("sky_attached_devices.html")

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
    def __init__(self):
        self.connected = False
        self.connect_time_sec = 0
        self.date_connected = datetime.min
        self.line_stats = dict()

    def parse_page(self, page_reader: RouterReadPages) -> bool:
        """ parse the router pages to extract status"""
        if self.parse_system_html(page_reader) and self.parse_sky_st_poe_html(page_reader):
            return True

        return False

    def parse_sky_st_poe_html(self, page_reader: RouterReadPages) -> bool:
        """ read and extract data from the connection status page"""
        page_source = page_reader.read_page("sky_st_poe.html")

        if page_source is None:
            return False

        found_data = False

        try:
            for page_line in page_source:
                if page_line.find("var wanStatus =") != -1:
                    wan_status = page_line.split("_")

                    time_elements = wan_status[11].split(":")
                    self.connect_time_sec = (int(time_elements[0]) * 60 * 60) +\
                                            (int(time_elements[1]) * 60) +\
                                            int(time_elements[2])

                    self.date_connected = datetime.now() - timedelta(seconds=self.connect_time_sec)
                    found_data = True
        except IndexError:
            found_data = False

        return found_data

    def parse_system_html(self, page_reader: RouterReadPages) -> bool:
        """ read and extract data from the show statistics page"""
        page_source = page_reader.read_page("sky_system.html")

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


class RouterStatus:
    """Connect to the sky router and extract connection information"""
    def __init__(self):
        self.system_details = RouterSystemDetail()
        self.line_stats = RouterLineStats()
        self.attached_devices = RouterAttachedDevices()
        self.page_reader = RouterReadPages()

    def open_connection(self) -> bool:
        """Open connection to the sky router using default username and password"""
        return self.page_reader.open_connection()

    def get_system_details(self) -> dict:
        return self.system_details.parse_page(self.page_reader)

    def get_line_status(self) -> bool:
        return self.line_stats.parse_page(self.page_reader)

    def get_attached_devices(self) -> dict:
        return self.attached_devices.parse_page(self.page_reader)

    def reload_status(self) -> bool:
        """Extract connection data from router web page"""
        if not self.line_stats.parse_page(self.page_reader):
            return False

        if not self.attached_devices.parse_page(self.page_reader):
            return False

        return True
