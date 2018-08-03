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
MULTIDAP_PORT = 4024
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


def sendCommand(command, snippetID=0):
	sent = False
	print "Attempting to send command: " + command
	while not sent:
		try:
			#	Establish TCP socket with LanBox
			print "Attempting to connect..."
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print "Socket created..."
			s.connect((MULTIDAP_IP, MULTIDAP_PORT))
			print "Connection established..."
			s.send(command)
			response = getResponse(s)
			# Close socket
			if response != '':
				print "Closing due to response received: " + response
				sent = True
				s.close()
		except:
			print "Not connected - retrying..."
			time.sleep(1)

def getResponse(s):
	print "Getting response..."
	data = s.recv(BUFFER_SIZE)
	if data != '':
		print "Response received: " + data
	return data

launch()
