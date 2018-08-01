#!/usr/bin/env python

import socket, time, copy, datetime

#	Lanbox settings
LANBOX_IP = '192.168.1.77'
LANBOX_PORT = 777
LANBOX_PW = '777\n'
BUFFER_SIZE = 1024

#	General lanbox commands
COMMANDS = {
	'TEST_ON': '*C901057E#',
	'TEST_OFF': '*C9010500#',
	'FADE_ON': '*4D0103#',
	'FADE_OFF': '*4D0100#',
	'FADE_FAST': '*4E0104#',
	'FADE_MED': '*4E0108#',
	'FADE_SLOW': '*4E0110#',
	'SAVE': '*A9#'
}

#	Controller settings
playing = False

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
		s.send(COMMANDS['TEST_ON'])
		time.sleep(0.25)
		s.send(COMMANDS['TEST_OFF'])
		time.sleep(0.25)

def longTest(s):
	for x in range(3):
		print x + 1
		s.send(COMMANDS['TEST_ON'])
		time.sleep(2)
		s.send(COMMANDS['TEST_OFF'])
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
			if command.upper() in COMMANDS:
				command = COMMANDS[command.upper()]
				s.send(command)
			elif command.upper() == 'TEST':
				sendTestCommand(s)
			elif command.upper() == 'TEST_LONG':
				longTest(s)
			elif command.upper() == 'OFF':
				turnAllOff(s)
			# elif command == 'fadesOn':
			# 	command = "*4D0103#"
			# 	s.send(command)
			# elif command == 'fadesOff':
			# 	command = "*4D0100#"
			# 	s.send(command)
			# elif command == 'fadeFast':			#	sets global fade time to 200ms
			# 	command = "*4E0104#"
			# 	s.send(command)
			# elif command == 'fadeMed':			#	global fade time to 400ms
			# 	command = "*4E0108#"
			# 	s.send(command)
			# elif command == 'fadeLong':			#	global fade time to 800ms
			# 	command = "*4E0110#"
			# 	s.send(command)
			# elif command == 'save':					#	save global fade settings to flash ROM
			# 	command = "*A9#"
			# 	s.send(command)
			else:
				s.send(command)

			print "Command is " + command

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