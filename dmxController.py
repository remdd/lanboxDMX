#	DMX conversation player for RPi

import time

playState = 0
timeStamp = 0
conversationObjects = []

#	Load conversations from XML
execfile('loadConversations.py')

import copy
import datetime
from datetime import timedelta


def playConversation(number):
	global playState
	if playState == 0:
		#	Set playState to prevent further conversations from starting
		playState = 1

		#	Create a deep copy of the conversation to be played from the master list, sort by time value
		triggerQueue = copy.deepcopy(conversationObjects[number].triggers)
		triggerQueue.sort(key = lambda x: x.time)

		#	Set timeStamp to the time the button was pressed
		global timeStamp
		timeStamp = datetime.datetime.now()

		while len(triggerQueue) > 0:
			if datetime.datetime.now() - timeStamp > timedelta(seconds = triggerQueue[0].time):
				print("Trigger! Time: " + str(triggerQueue[0].time) + ', value: ' + str(triggerQueue[0].value))
				dmx.setChannel(triggerQueue[0].channel, triggerQueue[0].value)
				dmx.render()
				triggerQueue.pop(0)

		print("Conversation playback complete.")
		playState = 0

	else:
		print("A conversation is already playing!")


###################################
#	Link conversation player to RPi and hardware
execfile('piDMXController.py')



#	playConversation(0)
#	time.sleep(1)
#	playConversation(1)


