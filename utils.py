#!/usr/bin/env python3
"""Utility functions"""

from datetime import datetime


class AnsiiColors:
    """ANSII control strings to change colours"""
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AnsiiCursor:
    """ANSII control strings to control the cursor"""
    UP = "\033[F"


class DisplayHelper:
    """Class to help display columns of information
       Assumes all columns contain the same information - will need to change this"""

    def __init__(self, num_columns=3, title_width=20, value_width=20):
        self.num_columns = num_columns
        self.title_width = title_width
        self.value_width = value_width
        self.cols_data = list()

    def get_title_str(self, value: str) -> str:
        """return a padded string for the title column"""
        return "{title:<{width}}".format(title=value, width=self.title_width)

    def get_value_str(self, value: str) -> str:
        """return a padded string for the value column"""
        return "{value:<{width}}".format(value=value, width=self.value_width)

    def add_column(self, col_data: dict):
        """Add a new column of data, all columns need to have same keys"""
        self.cols_data.insert(0, col_data)
        if len(self.cols_data) > self.num_columns:
            self.cols_data.pop()

    def print_info(self, reset_cursor=True) -> bool:
        """Print to console all columns"""
        if not self.cols_data:
            return False  # No data to display

        up_cursor = AnsiiCursor.UP
        for title in self.cols_data[0]:
            print(self.get_title_str(title + ":"), end="")
            for inx in range(len(self.cols_data)):
                if inx+1 < len(self.cols_data):
                    if self.cols_data[inx][title] != self.cols_data[inx+1][title]:
                        print(AnsiiColors.RED, end="")

                print(self.get_value_str(self.cols_data[inx][title]), end="")
                print(AnsiiColors.ENDC, end="")

            print("")
            up_cursor += AnsiiCursor.UP

        if reset_cursor:
            print(up_cursor)

        return True


class RouterStatusLogger:
    """Write router status to display and log file"""
    def __init__(self, filename):
        self.f_log = open(filename, "a")
        self.file_open = True

    def __del__(self):
        self.f_log.close()

    def print_log(self, text):
        """Write log entry to display and file if it is open"""
        output_string = datetime.now().strftime("%d-%m-%y %H:%M:%S") + "   , " + text
        print(output_string)
        if self.file_open:
            self.f_log.write(output_string)
