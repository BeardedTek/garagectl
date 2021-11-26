#!/usr/bin/python

############################## Start Config ##############################

# host: full url string prior to first slash.
# i.e.: `http(s)://10.0.0.10:8123` or `http(s)://ha.url/`
host = "http://10.0.0.10:8123"

# api_path: path to webhook api
api_path = "/api/webhook/"

# webhook: webhook id to curl
base_webhook = "garage_door"

# enable_path: path that if exists enables operation.
enable_path = "/srv/ctl/garage_door"

# GPIO Pin to operate
gpio = 23
##############################   End Config   ##############################

# Concatenate host and api_path to form url
baseurl = host + api_path + base_webhook
gctlver = "0.2"

from sys import version
import lgpio
from time import sleep
from os.path import exists
import subprocess
import cgi
import os

def build_webhook(base,function): # Builds and returns the full webhook url
    full_webhook = base + "-" + function
    return full_webhook

def operate(base,function,gpio):
# "Presses" Garage Door Button and curls a webhook to home assistant.
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, gpio)
    # Turn the GPIO pin on
    lgpio.gpio_write(h, gpio, 0)
    # "Hold" for 1 second
    sleep(1)
    # Turn the GPIO pin off
    lgpio.gpio_write(h, gpio, 1)
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
def get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip
def usage(title):
# Prints usage
    print("<div class='title'>"+title+" <a title='Close' href='?'><img src='../img/close.svg'></a></div>")
    print("<div class='usage'>")
    print("<span class='subtitle'>API Access using the following structure:</span><br/><br/>")
    print("<span class='subtitle'>http(s)://"+get_local_ip()+"?function=`command`</span><br><br>")
    print("<span class='subtitle'>Commands:</span><br>")
    print("<span class='command'>enable :</span><span class='spacer'> </span> Enables Garage Door Control<br>")
    print("<span class='command'>disable :</span><span class='spacer'> </span> Disables Garage Door Control<br>")
    print("<span class='command'>open :</span><span class='spacer'> </span> Opens the garage door<br>")
    print("<span class='command'>close :</span><span class='spacer'> </span> Closes the garage door<br>")
    print("</div>")

def clicker(path,title):
    print("<div class=title>"+title+" <a title='More Info' href='?function=info'><img src='../img/question.svg'></div>")
    print("<div class=button_container>")
    print("<a title='Open Garage Door' href='?function=open'><div id=up class='button_up button'><img src='../img/garage_door_open.svg'></div></a>")
    print("<a title='Close Garage Door' href='?function=close'><div id=down class='button_dn button'><img src='../img/garage_door_close.svg'></div></a></div>")

    if check_enable(path):
        print("<a title='Click to Disable' href='?function=disable'><div class='status'><img src='../img/unlocked.svg'></div></a>")
        print("<div class='footer enabled'>System Enabled</a></div></div>")
    else:
        print("<a title='Click to Enable' href='?function=enable'><div class='status'><img src='../img/locked.svg'></div></a>")
        print("<div class='footer disabled'>System Disabled</a></div>")

def display(function):
    title = "garageCTL v"+gctlver
    print("Content-Type: text/html")
    print()
    print("<html lang='en' xml:lang='en' xmlns='http://www.w3.org/1999/xhtml'><head><title>"+title+"</title>")
    print("<meta charset='UTF-8'>")
    print("<meta name='google' content='notranslate'>")
    print("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    print("<meta http-equiv='content-language' content='en-us'>")
    print("<link rel='stylesheet' href='../css/garagectl.css'>")
    print("</head><body>")


    if function == "info":
        print("<div class='hidden'>")
        #clicker()
        print("</div>")
        print("<div class='menu'>")
        usage(title)
        print("</div>")
    else:
        print("<div class='menu'>")
        clicker(enable_path,title)
        print("</div>")
        print("<div class='hidden'>")
        #usage()
        print("</div>")
def main():
    # Let's get down to business... to open the... garage. < Bad Mulan Reference
    data=get_param()

    # if elif statement for 'function' querystring
    if data.getvalue('function') == "open":
        if check_enable(enable_path):
            operate(baseurl,"opening",gpio)
    elif data.getvalue('function') == "close":
        if check_enable(enable_path):
            operate(baseurl,"closing",gpio)
    elif data.getvalue('function') == "enable":
        enable(baseurl,enable_path)
    elif data.getvalue('function') == "disable":
        disable(baseurl,enable_path)
    elif data.getvalue('function') == "status":
        status(baseurl,enable_path)
    display(data.getvalue('function'))
main()

