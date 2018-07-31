#!/usr/bin/env python

import socket, time

#	Lanbox settings
LANBOX_IP = '192.168.1.77'
LANBOX_PORT = 777
LANBOX_PW = '777\n'
BUFFER_SIZE = 1024


TEST_ON = '*C901057E#'
TEST_OFF = '*C9010500#'

#	Controller settings


#	DMX channels
DMX_UNIVERSE = 01
DMX = {
	'WILLIAM_PITT': 0,
	'PLYMOUTH_POLL': 1,
	'GIRL_GUIDE': 2,
	'CHARLES_LITTLE': 3,
	'JACK_TAR': 4,
	'NELSON': 5,
	'CALDWELL': 6,
	'DEITY': 7,
	'CHARLES_FOX': 8,
	'PERSON_OF_SEA': 9,
	'LIARDET': 10,
	'BRITANNIA': 11,
	'5': 99
}
for key in sorted(DMX.iterkeys()):
	print key + ': ' + str(DMX[key])


#	Load conversations from XML
conversationObjects = []
execfile('loadConversations.py')


def sendTestCommand():
	for x in range(5):
		print x
		s.send(TEST_ON)
		time.sleep(0.1)
		s.send(TEST_OFF)
		time.sleep(0.1)


def launch():
	while 1:
		command = raw_input("Enter command: ")
		sendCommand(command)


def sendCommand(command):
	sent = False
	while not sent:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((LANBOX_IP, LANBOX_PORT))
			s.send(LANBOX_PW)
			s.send(command)
			data = s.recv(BUFFER_SIZE)
			print "Response from LANBOX:", data
			sent = True
			s.close()
		except:
			print "Not connected... retrying"
			time.sleep(1)


launch()