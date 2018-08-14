#!/usr/bin/env python
import socket, time, copy, datetime, sys, random, threading

#	change to true when running on Raspberry Pi
runningOnPi = False

if runningOnPi:
	# import RPi GPIO pin controllers
	import RPi.GPIO as GPIO

# tcflush used to clear input buffer before requesting new input - prevents multi button presses queuing up multiple commands
from termios import tcflush, TCIFLUSH

#	MultiDAP settings
MULTIDAP_IP = '172.16.4.201'
MULTIDAP_PORT = 4023							#	Nb TCP port is 4024, UDP is 4023
BUFFER_SIZE = 1024

#	General lanbox commands
COMMANDS = {
	'INFO': 'ID02MS011',
	'VOL20': 'ID02VA020',
	'TEST2': 'ID02PF001',
	'TEST3': 'ID03PF001',
}

#	Controller settings
playing = False


def launch():
	###########	Code to run once on first load ##########
	while True:
		command = raw_input("Enter command: ")
		if command.upper() in COMMANDS:
			multiDAPcommand = COMMANDS[command.upper()] + '\r\n'
			print multiDAPcommand	
			sendCommand(multiDAPcommand)
		else:
			print "Command not recognized!"


def sendCommand(command):
	sent = False
	print "Attempting to send command: " + command
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
	s.connect((MULTIDAP_IP, MULTIDAP_PORT))
	s.send(command)
	s.close()


launch()
