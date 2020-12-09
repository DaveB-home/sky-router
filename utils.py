#!/usr/bin/env python3
"""Utility functions"""

from dataclasses import dataclass


class AnsiiColors:
    """ANSII control strings to change colours"""
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AnsiiCursor:
    """ANSII control strings to control the cursor"""
    UP = "\033[F"


@dataclass
class DisplayColumn:
    display_size: int
    data: dict


class DisplayHelper:
    """Class to help display columns of information
       Assumes all columns contain the same information - will need to change this"""
    def __init__(self, section_title: str, num_columns=3, title_width: int = 0, value_width=0):
        self.section_title = section_title
        self.num_columns = num_columns
        self.title_width = title_width
        self.value_width = value_width
        
        self.cols_data = list()
        self.print_counter = 0
        self.PAD_SIZE = 5

    @staticmethod
    def get_title_str(value: str, title_width: int) -> str:
        """return a padded string for the title column"""
        return "{title:<{width}}".format(title=value, width=title_width)

    @staticmethod
    def get_value_str(display_col: DisplayColumn, key: str) -> str:
        """return a padded string for the value column"""
        return "{val:<{width}}".format(val=display_col.data[key], width=display_col.display_size)

    def add_column(self, col_data: dict):
        """Add a new column of data, all columns need to have same keys"""              
        if self.value_width == 0:
            value_width = (max(len('{}'.format(item)) for item in col_data.values())) + self.PAD_SIZE     
        else:
            value_width = self.value_width
        
        display_col = DisplayColumn(value_width, col_data)      
        self.cols_data.insert(0, display_col)
        if len(self.cols_data) > self.num_columns:
            self.cols_data.pop()

    def print_count(self, string: str, reset_count: bool = False):
        if reset_count:
            self.print_counter = 1
        else:
            self.print_counter += 1
            
        print(string)
        
    def move_cursor_up(self):
        for i in range(self.print_counter+1):
            print(AnsiiCursor.UP, end="")
        print()

    def print(self, reset_cursor=True) -> bool:
        if not self.cols_data:
            return False  # No data to display
    
        self.print_count(AnsiiColors.BOLD + self.section_title + AnsiiColors.ENDC, True)

        if self.title_width == 0:
            title_width = (max(len(key) for key in self.cols_data[0].data)) + self.PAD_SIZE
        else:
            title_width = self.title_width
            
        for title in self.cols_data[0].data:
            print("  " + self.get_title_str(title + ":", title_width), end="")
            for inx in range(len(self.cols_data)):
                if inx+1 < len(self.cols_data):
                    if self.cols_data[inx].data[title] != self.cols_data[inx+1].data[title]:
                        print(AnsiiColors.RED, end="")

                print(self.get_value_str(self.cols_data[inx], title), end="")
                print(AnsiiColors.ENDC, end="")

            self.print_count("")

        if reset_cursor:
            self.move_cursor_up()

        return True
