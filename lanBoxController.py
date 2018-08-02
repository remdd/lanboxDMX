#!/usr/bin/env python
import socket, time, copy, datetime, sys, random

#	change to true when running on Raspberry Pi
runningOnPi = False

if runningOnPi:
	# import RPi GPIO pin controllers
	import RPi.GPIO as GPIO

# tcflush used to clear input buffer before requesting new input - prevents multi button presses queuing up multiple commands
from termios import tcflush, TCIFLUSH

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
timeStamp = 0
#	Min and max times of inactivity before next 'snippet' plays, in seconds
snippetMinWait = 5
snippetMaxWait = 10
#	details of queued snippet and last one played
nextSnippetTime = 0
nextSnippetID = 0
lastSnippetID = 0

#	Load settings from XML
# DMX_CHANNELS = {}
snippetObjects = []
conversationObjects = []
execfile('loadXML.py')

#	Configure Raspberry Pi and trigger buttons
if runningOnPi:
	GPIO.setmode(GPIO.BCM)

for conversation in conversationObjects:
	if runningOnPi:
		GPIO.setup(conversation.pin, GPIO.IN, pull_up_down=GPI.PUD_UP)
		print "Conversation " + str(conversation.id) + " is triggered through pin " + str(conversation.pin) + " on the Raspberry Pi."


def sendTestCommand(s):
	for x in range(3):
		print x + 1
		s.send(COMMANDS['TEST_ON'])
		time.sleep(0.4)
		s.send(COMMANDS['TEST_OFF'])
		time.sleep(0.4)

def longTest(s):
	for x in range(3):
		print x + 1
		s.send(COMMANDS['TEST_ON'])
		time.sleep(3)
		s.send(COMMANDS['TEST_OFF'])
		time.sleep(3)


def turnAllOff(s):
	print "Turning all lights off..."
	for key in DMX_CHANNELS:
		command = '*C9' + DMX_UNIVERSE + DMX_CHANNELS[key] + '00#'
		print command
		s.send(command)
#		getResponse(s)
	print "All lights turned off"


def launch():
	###########	Code to run once on first load ##########
	# Turn all lights off
	sendCommand('off')

	########### Main loop ##########
	while 1:
		if runningOnPi:
			if not playing:
				print "Not playing!"
				time.sleep(1)
			else:
				print "Playing..."
				time.sleep(1)

		else:
			if not playing:
				queueNextSnippet()
				tcflush(sys.stdin, TCIFLUSH)
				command = raw_input("Enter command: ")
				while not command:
					print "Waiting"
					time.sleep(1)
				sendCommand(command)
			else:
				time.sleep(1)


def queueNextSnippet():
	print "Queueing snippet..."
	wait = random.randint(snippetMinWait, snippetMaxWait)
	nextSnippetTime = datetime.datetime.now() + datetime.timedelta(seconds=wait)
	print "Next snippet in " + str(wait) + " seconds"
	rand = random.randint(0, len(snippetObjects)-1)
	print "Next snippet ID is " + str(rand)
	snippet_next = rand


def unqueueSnippet():
	print "Unqueuing snippet..."


def playSnippet(s, snippetID):
	print snippetID


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
			elif command.upper() == 'PLAY':
				conversationID = raw_input("Enter conversation ID: ")
				validID = False
				for conversation in conversationObjects:
					if conversation.id == int(conversationID):
						validID = True
						playConversation(s, int(conversationID))
				if not validID:
					print "No conversation found with ID " + conversationID
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


def getDMXCommand(characterID, value):
	command = "*C9" + DMX_UNIVERSE + characterID + value + '#'
	print "DMX command: " + command
	return command


def playConversation(s, conversationID):
	global playing
	if not playing:
		#	Set playState to prevent further conversations from starting
		playing = True

		#	Turn off all lights just in case
		turnAllOff(s)

		#	Create a deep copy of the conversation to be played from the master list, sort by time value
		triggerQueue = copy.deepcopy(conversationObjects[conversationID].triggers)
		triggerQueue.sort(key = lambda x: x.time)

		#	Set timeStamp to the time the button was pressed
		global timeStamp
		timeStamp = datetime.datetime.now()
		print timeStamp

		#	Check for hit triggers every 100ms while there are any in the queue
		while len(triggerQueue) > 0:
			time.sleep(0.1)
			if datetime.datetime.now() - timeStamp > datetime.timedelta(seconds = triggerQueue[0].time):
				print datetime.datetime.now()
				print "Trigger! Time: " + str(triggerQueue[0].time)
				command = getDMXCommand(triggerQueue[0].channel, triggerQueue[0].value)
				sendCommand(command)
				print "Command sent"
				triggerQueue.pop(0)
				print len(triggerQueue)

		print("Conversation playback complete.")
		playing = False

	else:
		print("A conversation is already playing!")

launch()