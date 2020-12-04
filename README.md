# sky-router
Set of Python classes to read data from a sky router.

## Why?
After moving my broadband to Sky the connection because very unstable. 
To help track down the problem I developed this project to allow me to extract information from the router. 
A simple monitoring script was used to alert me in real time to issues with the connection. 

## Release Notes
* The monitor (-m) does not work on Windows
* There are a number of display issues on Windows because the ANSII terminal display strings are not supported
* The default Sky router username and password are embedded into the classes (see get_router_data.py)
* Generally the class structure needs tidying
* This is the first version of the project
* README.MD is missing information

## Installation 
This project is pure Python and was developed on Python 3.8. It is recommended that you use this version or above. 
It has been tested on Ubuntu 18.04/20.04 LTS and Windows 10 (19042.662)

#### Requirements
* Linux or Windows 10
* Python 3.8 (or above)
* git (optional)

#### Python and git install 

###### Linux
1. sudo apt-get install python3.8
1. sudo apt-get install git

###### Windows
1. Launch the "Microsoft Store" application. Can be found by typing "store" into the search box.
1. Search for "python 3.8"
1. Click the install button on the application
1. Download the git application directly from their site : https://git-scm.com/download/win
1. Run the downloaded installer, use all the default options

#### Install with git
open the terminal or command line prompt depending on O/S being used
* Change the directory to the location to install the project
* git clone https://github.com/DaveB-home/sky-router.git
* cd sky-router

#### Install via github website

## Current Functionality

## Usage 

## License
Code is released under MIT License 
