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
DMX_UNIVERSE = '01'
DMX = {
	#	Values correspond to individual spotlight assignments
	'WILLIAM_PITT': '00',
	'PLYMOUTH_POLL': '01',
	'GIRL_GUIDE': '02',
	'CHARLES_LITTLE': '03',
	'JACK_TAR': '04',
	'NELSON': '05',
	'CALDWELL': '06',
	'DEITY': '07',
	'CHARLES_FOX': '08',
	'PERSON_OF_SEA': '09',
	'LIARDET': '10',
	'BRITANNIA': '11',
	'5': '99'
}
for key in sorted(DMX.iterkeys()):
	print key + ': ' + str(DMX[key])


#	Load conversations from XML
conversationObjects = []
execfile('loadConversations.py')


def sendTestCommand(s):
	for x in range(5):
		print x + 1
		s.send(TEST_ON)
		time.sleep(0.1)
		s.send(TEST_OFF)
		time.sleep(0.1)

def longTest(s):
	for x in range(3):
		print x + 1
		s.send(TEST_ON)
		time.sleep(2)
		s.send(TEST_OFF)
		time.sleep(2)


def turnAllOff(s):
	for key in DMX:
		command = '*C9' + DMX_UNIVERSE + DMX[key] + '00#'
		print command
		s.send(command)
		getResponse(s)


def launch():
	while 1:
		command = raw_input("Enter command: ")
		sendCommand(command)


def sendCommand(command):
	sent = False
	while not sent:
		try:
			#	Establish TCP socket with LanBox
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((LANBOX_IP, LANBOX_PORT))
			s.send(LANBOX_PW)

			# Send command
			if command == 'test':
				sendTestCommand(s)
			elif command == 'longTest':
				longTest(s)
			elif command == 'off':
				turnAllOff(s)
			elif command == 'fadesOn':
				command = "*4D0103#"
				s.send(command)
			elif command == 'fadesOff':
				command = "*4D0100#"
				s.send(command)
			elif command == 'fadeFast':
				command = "*4E0102"
				s.send(command)
			elif command == 'fadeMed':
				command = "*4E010A"
				s.send(command)
			elif command == 'fadeLong':
				command = "*4E0114"
				s.send(command)
			else:
				s.send(command)

			response = getResponse(s)
			print response

			# Close socket
			sent = True
			s.close()
		except:
			print "Not connected... retrying"
			time.sleep(1)

def getResponse(s):
	data = s.recv(BUFFER_SIZE)
	print "Response from LANBOX:", data
	return data


launch()