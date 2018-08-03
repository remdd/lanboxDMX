#!/usr/bin/env python
import socket, time, copy, datetime, sys, random, threading

#	change to true when running on Raspberry Pi
runningOnPi = False

if runningOnPi:
	# import RPi GPIO pin controllers
	import RPi.GPIO as GPIO

# tcflush used to clear input buffer before requesting new input - prevents multi button presses queuing up multiple commands
from termios import tcflush, TCIFLUSH

#	Socket buffer size
BUFFER_SIZE = 1024

#	General commands
LANBOX_COMMANDS = {
	'TEST_ON': '*C901057E#',
	'TEST_OFF': '*C9010500#',
	'FADE_ON': '*4D0103#',
	'FADE_OFF': '*4D0100#',
	'FADE_FAST': '*4E0104#',
	'FADE_MED': '*4E0108#',
	'FADE_SLOW': '*4E0110#',
	'SAVE': '*A9#'
}

MULTIDAP_COMMANDS = {
	'INFO': 'ID02MS011',
	'VOL20': 'ID02VA020',
	'TEST2': 'ID02PF001',
	'TEST3': 'ID03PF001',
}

#	Controller settings
playing = False
timeStamp = 0
userLanboxCommand = ''
#	details of queued snippet and last one played
nextSnippetTime = 0
nextSnippetID = 0
lastSnippetID = 0

#	Load settings from XML
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
		s.send(LANBOX_COMMANDS['TEST_ON'])
		time.sleep(0.4)
		s.send(LANBOX_COMMANDS['TEST_OFF'])
		time.sleep(0.4)

def longTest(s):
	for x in range(3):
		print x + 1
		s.send(LANBOX_COMMANDS['TEST_ON'])
		time.sleep(3)
		s.send(LANBOX_COMMANDS['TEST_OFF'])
		time.sleep(3)

def turnAllOff(s):
	print "Turning all lights off..."
	for key in DMX_CHANNELS:
		command = '*C9' + DMX_UNIVERSE + DMX_CHANNELS[key] + '00#'
		print command
		s.send(command)
	print "All lights turned off"

def kbdListener():
	global userLanboxCommand
	userLanboxCommand = raw_input()
	print "Input: " + userLanboxCommand

def piListener():
	global userLanboxCommand
	while True:
		btn_0_state = GPIO.input(conversationObjects[0].pin)
		btn_1_state = GPIO.input(conversationObjects[1].pin)
		btn_2_state = GPIO.input(conversationObjects[2].pin)
		if btn_0_state == False:
			print "Button 0 pressed"
			userLanboxCommand = 'play0'
		elif btn_1_state == False:
			print "Button 1 pressed"
			userLanboxCommand = 'play1'
		elif btn_2_state == False:
			print "Button 2 pressed"
			userLanboxCommand = 'play2'
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
	sendLanboxCommand('off')
	# Queue up a first snippet
	queueNextSnippet()
	#	Start input listener
	startListenerThread()
	global userLanboxCommand, listener

	########### Main loop ##########
	while 1:

		if not playing:
			if userLanboxCommand:
				print "Keyboard command! " + userLanboxCommand
				sendLanboxCommand(userLanboxCommand)
				userLanboxCommand = ''
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
	#	Prevent the same snippet playing twice on the trop
	while wait == lastSnippetID:
		wait = random.randint(snippetMinWait, snippetMaxWait)
	nextSnippetTime = datetime.datetime.now() + datetime.timedelta(seconds=wait)
	print nextSnippetTime
	print "Next snippet in " + str(wait) + " seconds"
	rand = random.randint(0, len(snippetObjects)-1)
	print "Next snippet ID is " + str(rand)
	nextSnippetID = rand


def playSnippet(snippetID):
	global lastSnippetID
	print "Playing snippet " + str(snippetID)
	lastSnippetID = snippetID
	sendLanboxCommand('snippet', snippetID)
	print "Command sent!"
	queueNextSnippet()


def sendLanboxCommand(command, snippetID=0):
	sent = False
	print "Sending Lanbox command"
	while not sent:
		try:
			#	Establish TCP socket with LanBox
			print "Establishing Lanbox TCP socket"
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print LANBOX_IP + " ------- " + str(LANBOX_PORT)
			print "Connecting to TCP socket"
			s.connect((LANBOX_IP, LANBOX_PORT))
			print "Sending PW"
			s.send(LANBOX_PW)
			#	Set to 16-bit mode
			s.send("*65FF#")
			# Send command
			if command.upper() in LANBOX_COMMANDS:
				command = LANBOX_COMMANDS[command.upper()]
				s.send(command)

			elif command.upper() == 'TEST':
				sendTestCommand(s)
				queueNextSnippet()

			elif command.upper() == 'TEST_LONG':
				longTest(s)
				queueNextSnippet()

			elif command.upper() == 'OFF':
				turnAllOff(s)

			#	Play Conversation
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

			# Play Snippet
			elif command.upper() == 'SNIPPET':
				for snippet in snippetObjects:
					if snippetID == snippet.id:
						#	Send all lighting trigger ON commands
						for trigger in snippet.lightingTriggers:
							command = '*C9' + DMX_UNIVERSE + trigger.channel + 'FF#'
							print 'Sending DMX command: ' + command
							s.send(command)
						for trigger in snippet.audioTriggers:
							print "Triggering file " + trigger.file + " on flux " + trigger.flux
							playMultiDapFile(trigger.flux, trigger.file)
						#	Sleep for duration of snippet
						time.sleep(snippet.duration)
						#	Send all lighting trigger OFF commands
						for trigger in snippet.lightingTriggers:
							command = '*C9' + DMX_UNIVERSE + trigger.channel + '00#'
							s.send(command)

			else:
				s.send(command)

			getLanboxResponse(s)

			# Close socket
			sent = True
			s.close()
		except:
			print "No connection to LanBox... retrying"
			time.sleep(1)

def getLanboxResponse(s):
	data = s.recv(BUFFER_SIZE)
	print "Response from LanBox:", data
	return data


def getDMXCommand(characterID, value):
	command = "*C9" + DMX_UNIVERSE + characterID + value + '#'
	print "DMX command: " + command
	return command


########################

def playMultiDapFile(flux, file):
	sent = False
	print "Attempting to play track " + file + " on flux " + flux
	while not sent:
		try:
			#	Establish TCP socket with MultiDAP
			print "Attempting to connect to MultiDAP..."
			m = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			m.connect((MULTIDAP_IP, MULTIDAP_PORT))
			command = 'ID' + flux + 'PF' + file + '\r\n'
			print "MultiDAP command: " + command
			m.send(command)
			response = getMultiDapResponse(m)
			# Close socket
			if response != '':
				sent = True
				m.close()
		except:
			print "No connection with MultiDAP - retrying..."
			time.sleep(1)

def getMultiDapResponse(m):
	print "Getting response from MultiDAP..."
	data = m.recv(BUFFER_SIZE)
	if data != '':
		print "Response received from MultiDAP: " + data
	return data


########################

def playConversation(s, conversationID):
	global playing
	if not playing:
		#	Set playState to prevent further conversations from starting
		playing = True

		#	Turn off all lights just in case
		turnAllOff(s)

		#	Create a deep copy of the conversation to be played from the master list, sort by time value
		triggerQueue = copy.deepcopy(conversationObjects[conversationID].lightingTriggers)
		triggerQueue.sort(key = lambda x: x.time)

		#	Set timeStamp to the time the button was pressed
		global timeStamp
		timeStamp = datetime.datetime.now()
		print timeStamp

		audioTriggers = copy.deepcopy(conversationObjects[conversationID].audioTriggers)
		for trigger in audioTriggers:
			print "Playing file " + trigger.file + " on flux " + trigger.flux
			playMultiDapFile(trigger.flux, trigger.file)

		#	Check for hit triggers every 100ms while there are any in the queue
		while len(triggerQueue) > 0:
			time.sleep(0.1)
			if datetime.datetime.now() - timeStamp > datetime.timedelta(seconds = triggerQueue[0].time):
				print "Trigger! Time: " + str(triggerQueue[0].time)
				command = getDMXCommand(triggerQueue[0].channel, triggerQueue[0].value)
				sendLanboxCommand(command)
				triggerQueue.pop(0)
				print len(triggerQueue)

		print("Conversation playback complete.")
		# Flush input
		tcflush(sys.stdin, TCIFLUSH)
		queueNextSnippet()
		playing = False

	else:
		print("A conversation is already playing!")

launch()
