#!/usr/bin/python

############################## Start Config ##############################

# host: full url string prior to first slash.
# i.e.: `http://192.168.1.200:8123` or `https://ha.url/`
host = "http://192.168.2.245:8123"

# api_path: path to webhook api
api_path = "/api/webhook/"

# webhook: webhook id to curl
base_webhook = "garage_door"

# enable_path: path that if exists enables operation.
enable_path = "/srv/ctl/garage_door"

##############################   End Config   ##############################

# Concatenate host and api_path to form url
baseurl = host + api_path + base_webhook
gctlver = "0.1"

from sys import version
import lgpio
from time import sleep
from os.path import exists
import subprocess
import cgi

def build_webhook(base,function): # Builds and returns the full webhook url
    full_webhook = base + "-" + function
    return full_webhook

def operate(base,function):
# "Presses" Garage Door Button and curls a webhook to home assistant.
    print("Button Pressed<br/>")
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, 23)
    # Turn the GPIO pin on
    lgpio.gpio_write(h, 23, 0)
    # "Hold" for 1 second
    sleep(1)
    # Turn the GPIO pin off
    lgpio.gpio_write(h, 23, 1)
    menu()
    # Send a webhook to HA to say we pressed the button and whether it was
    # Commanded open or closed
    subprocess.run(['curl','-X','POST','-s',build_webhook(base,function)])
    return "OK"

def get_param():
# Reads querystring through CGI interface
    data=cgi.FieldStorage()
    return data

def check_enable(path):
# Check to see if the temp enable file exists.  Returns True or False
    if exists(path):
        return True
    else:
        return False

def enable(base,path):
# Touches the defined path to save enabled state to disk
    subprocess.run(['touch',path])
    subprocess.run(['curl','-X','POST','-s',build_webhook(base,"enabled")])
    return "OK"

def disable(base,path):
# Removes the defined path to save enabled state to disk
    subprocess.run(['rm','-f',path])
    subprocess.run(['curl','-X','POST','-s',build_webhook(base,"disabled")])
    return "OK"
def status(base,path):
#Checks status and reports to Home Assistant
    if check_enable(path):
        return enable(base,path)
    else:
        return disable(base,path)
def menu():
# Prints the menu
    print("<h1>Garage Door Control Interface</h1>")
    if check_enable(enable_path):
        print("<h2>Garage Door Control Enabled</h2>")
        print("<a href=?function=disable&menu=true>Disable Garage Door Control</a>")
        print("<br/><br/>")
        print("<a href=?function=open&menu=true>Open Garage Door</a><br/>")
        print("<a href=?function=close&menu=true>Close Garage Door</a><br/>")
    else:
        print("<h2>Garage Door Control Disabled</h2>")
        print("<a href=?function=enable&menu=true>Enable Garage Door Control</a>")
    print("<p>Usage:</p>")
    print("<p>this_url?function=`command`")
    print("<p>Commands:</p>")
    print("<p>enable : Enables Garage Door Control</p>")
    print("<p>disable: Disables Garage Door Control</p>")
    print("<p>open   : Presses the garage door button and tells home assistant we requested it to open</p>")
    print("<p>close  : Presses the garage door button and tells home assistant we requested it to close</p>")
    print("<br/><br/>")
def headers():
# Prints out the headers and decides what to do.
    title = "Garage Door Controller v"+gctlver
    print("Content-Type: text/html")
    print()
    print("<html><head><title>"+title+"</title>")
    print("<link rel='stylesheet' href='garagectl.css'>")
    print("</head><body>")
    with open('menu.html', 'r') as f:
        print(f.read())

def main():
    headers()
    # Let's get down to business... to open the... garage. < Bad Mulan Reference
    data=get_param()

    # if elif to show/hide menu
    if data.getvalue('menu') == "true":
        print("<a href=?menu=false>Hide Menu</a>")
    else:
        print("<a href=?menu=true>Show Menu</a>")

    # if elif statement for 'function' querystring
    if data.getvalue('function') == "open":
        print(operate(baseurl,"opening"))
    elif data.getvalue('function') == "close":
        print(operate(baseurl,"closing"))
    elif data.getvalue('function') == "enable":
        print(enable(baseurl,enable_path))
    elif data.getvalue('function') == "disable":
        print(disable(baseurl,enable_path))
    elif data.getvalue('function') == "status":
        print(status(baseurl,enable_path))

    # if elif statement for 'menu' querystring
    if data.getvalue('menu') == "true":
        menu()
main()
