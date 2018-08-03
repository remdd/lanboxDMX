#!/usr/bin/env python
import socket, time, copy, datetime, sys, random, threading

#	change to true when running on Raspberry Pi
runningOnPi = True

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
userCommand = ''
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
		GPIO.setup(conversation.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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


def kbdListener():
	global userCommand
	userCommand = raw_input()
	print "Input: " + userCommand

def piListener():
	global userCommand
	while True:
		btn_0_state = GPIO.input(conversationObjects[0].pin)
		btn_1_state = GPIO.input(conversationObjects[1].pin)
		btn_2_state = GPIO.input(conversationObjects[2].pin)
		if btn_0_state == False:
			print "Button 0 pressed"
			userCommand = 'play0'
		elif btn_1_state == False:
			print "Button 1 pressed"
			userCommand = 'play1'
		elif btn_2_state == False:
			print "Button 2 pressed"
			userCommand = 'play2'
		time.sleep(1)

def startListenerThread():
	if runningOnPi:
		listener = threading.Thread(target=piListener)
		listener.start()
	else:
		listener = threading.Thread(target=kbdListener)
		listener.start()


def launch():
	###########	Code to run once on first load ##########
	# Turn all lights off
	sendCommand('off')
	# Queue up a first snippet
	queueNextSnippet()
	#	Start input listener
	startListenerThread()
	global userCommand, listener

	########### Main loop ##########
	while 1:

		if not playing:
#			tcflush(sys.stdin, TCIFLUSH)
			if userCommand:
				print "Keyboard command! " + userCommand
				sendCommand(userCommand)
				userCommand = ''
				startListenerThread()
			else:
				time.sleep(1)
				if datetime.datetime.now() > nextSnippetTime:
					playSnippet(nextSnippetID)
		else:
			time.sleep(1)


def queueNextSnippet():
	global nextSnippetTime, nextSnippetID, lastSnippetID
	print "Queueing snippet..."
	wait = random.randint(snippetMinWait, snippetMaxWait)
	nextSnippetTime = datetime.datetime.now() + datetime.timedelta(seconds=wait)
	print nextSnippetTime
	print "Next snippet in " + str(wait) + " seconds"
	rand = random.randint(0, len(snippetObjects)-1)
	print "Next snippet ID is " + str(rand)
	nextSnippetID = rand


def playSnippet(snippetID):
	print "Playing snippet " + str(snippetID)
	lastSnippetID = snippetID
	sendCommand('snippet', snippetID)
	queueNextSnippet()


def sendCommand(command, snippetID=0):
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
				queueNextSnippet()

			elif command.upper() == 'TEST_LONG':
				longTest(s)
				queueNextSnippet()

			elif command.upper() == 'OFF':
				turnAllOff(s)

			elif command.upper() == 'PLAY0':
				playConversation(s, 0)

			elif command.upper() == 'PLAY1':
				playConversation(s, 1)

			elif command.upper() == 'PLAY2':
				playConversation(s, 2)

			elif command.upper() == 'PLAY':
				conversationID = raw_input("Enter conversation ID: ")
				validID = False
				for conversation in conversationObjects:
					if conversation.id == int(conversationID):
						validID = True
						playConversation(s, int(conversationID))
				if not validID:
					print "No conversation found with ID " + conversationID

			elif command.upper() == 'SNIPPET':
				for snippet in snippetObjects:
					if snippetID == snippet.id:
						command = '*C9' + DMX_UNIVERSE + snippet.channel + 'FF#'
						print 'DMX command: ' + command
						s.send(command)
						time.sleep(snippet.duration)
						command = '*C9' + DMX_UNIVERSE + snippet.channel + '00#'
						s.send(command)

			else:
				s.send(command)

			getResponse(s)

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
				print "Trigger! Time: " + str(triggerQueue[0].time)
				command = getDMXCommand(triggerQueue[0].channel, triggerQueue[0].value)
				sendCommand(command)
				triggerQueue.pop(0)
				print len(triggerQueue)

		print("Conversation playback complete.")
		queueNextSnippet()
		playing = False

	else:
		print("A conversation is already playing!")

launch()
