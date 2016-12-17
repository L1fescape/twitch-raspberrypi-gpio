import datetime
import socket
import select
import re

import requests
import json

import RPi.GPIO as GPIO
import time

ledPin = 18
lightsOn = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.output(ledPin, GPIO.LOW)

secrets = __import__("secrets")

''' Change the following settings if you wish to run the program '''
channel = 'l1fescape'
username = secrets.user
oauth = secrets.oauth

# Definitions to use while connected
def ping():
    ''' Respond to the server 'pinging' (Stays connected) '''
    client_socket.send('PONG :pingis\n')
    print('PONG: Client > tmi.twitch.tv')

def sendmsg(chan,msg):
    ''' Send specified message to the channel '''
    client_socket.send('PRIVMSG '+chan+' :'+msg+'\n')
    print('[BOT] -> '+chan+': '+msg+'\n')

def getmsg(msg):
    ''' GET IMPORTANT MESSAGE '''
    msg_edit = msg.split(':',2)
    global lightsOn
    if(len(msg_edit) > 2):
        user = msg_edit[1].split('!',1)[0] # User
        message = msg_edit[2] # Message
        channel = msg_edit[1].split(' ',2)[2][:-1] # Channel

        msg_split = str.split(message)

        datelog = datetime.datetime.now()

        if len(msg_split) > 0:
            command = msg_split[0].strip().lower()
            if(command == '!lights'):
                if len(msg_split) > 1:
                    lightsOn = True if msg_split[1] == "1" else False
                else:
                    lightsOn = not lightsOn

                if lightsOn:
                    GPIO.output(ledPin, GPIO.HIGH)
                else:
                    GPIO.output(ledPin, GPIO.LOW)

                requests.post("http://192.168.1.81:3001/lights",
                    data=json.dumps({'user': user, 'state': "on" if lightsOn else "off"}),
                    headers={'content-type': 'application/json'}
                )


# Connect to the server using the provided details
client_socket = socket.socket()
''' Connect to the server using port 6667 & 443 '''
client_socket.connect(('irc.twitch.tv',6667))

'''Authenticate with the server '''
client_socket.send('PASS '+oauth+'\n')
''' Assign the client with the nick '''
client_socket.send('NICK '+username+'\n')

''' Join the specified channel '''
client_socket.send('JOIN #'+channel+'\n')

print('Connected to irc.twitch.tv on port 6667')
print('USER: '+username)
print('OAUTH: oauth:'+'*'*30)
print('\n')

try:
    temp = 0
    while True:
        msg = client_socket.recv(2048)
        if(msg == ''):
            temp + 1
            if(temp > 5):
                print('Connection might have been terminated')

        ''' Remove any linebreaks from the message '''
        msg = msg.strip('\n\r')

        ''' DISPLAY MESSAGE IN SHELL '''
        getmsg(msg)

        ''' Respond to server pings '''
        if msg.find('PING :') != -1:
            print('PING: tmi.twitch.tv > Client')
            ping()
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    client_socket.close()
    GPIO.cleanup()
