#	Class definitions
class Conversation:
	def __init__(self, conversationID, pin):
		self.id = conversationID
		self.pin = pin
		self.lightingTriggers = []
		self.audioTriggers = []

class lightingTrigger:
	def __init__(self, tType, tTime, channel, value):
		self.tType = tType
		self.time = tTime
		self.channel = channel
		self.value = value

class audioTrigger:
	def __init__(self, tType, flux, file):
		self.tType = tType
		self.flux = flux
		self.file = file

class Snippet:
	def __init__(self, snippetID, duration):
		self.id = snippetID
		self.duration = duration
		self.lightingTriggers = []
		self.audioTriggers = []

import xml.dom.minidom
xml = xml.dom.minidom.parse('content.xml')


# Configure MultiDAP
MULTIDAP_IP = str(xml.getElementsByTagName('multidapConfig')[0].getElementsByTagName('IP')[0].childNodes[0].nodeValue)
MULTIDAP_PORT = int(xml.getElementsByTagName('multidapConfig')[0].getElementsByTagName('port')[0].childNodes[0].nodeValue)
print "MultiDAP communication on Port " + str(MULTIDAP_PORT) + " at " + MULTIDAP_IP


# Configure LanBox
LANBOX_IP = str(xml.getElementsByTagName('lanboxConfig')[0].getElementsByTagName('IP')[0].childNodes[0].nodeValue)
LANBOX_PORT = int(xml.getElementsByTagName('lanboxConfig')[0].getElementsByTagName('port')[0].childNodes[0].nodeValue)
# LANBOX_PW = unicode(xml.getElementsByTagName('lanboxConfig')[0].getElementsByTagName('password')[0].childNodes[0].data.encode("latin-1"), "utf-8")
LANBOX_PW = '777\n'

print "LanBox communication on Port " + str(LANBOX_PORT) + " at " + LANBOX_IP


# Set DMX universe and generate DMX channel directory
DMX_UNIVERSE = str(xml.getElementsByTagName('DMXuniverse')[0].childNodes[0].nodeValue)
print "DMX Universe ID is: " + DMX_UNIVERSE
DMXchannels = xml.getElementsByTagName('DMXchannels')[0].getElementsByTagName('DMXchannel')
DMX_CHANNELS = {}
for DMXchannel in DMXchannels:
	DMX_CHANNELS[DMXchannel.getAttribute('name')] = DMXchannel.childNodes[0].nodeValue

for key in sorted(DMX_CHANNELS.iterkeys()):
	print key + ' is on DMX channel ' + str(DMX_CHANNELS[key])


#	Configure snippets
snippetMinWait = int(xml.getElementsByTagName('snippetConfig')[0].getElementsByTagName('minTime')[0].childNodes[0].nodeValue)
snippetMaxWait = int(xml.getElementsByTagName('snippetConfig')[0].getElementsByTagName('maxTime')[0].childNodes[0].nodeValue)


# Generate master conversation object list
conversations = xml.getElementsByTagName('conversation')

for conversation in conversations:
	#	Create conversation object
	conversationID = int(conversation.getAttribute('id'))
	pin = int(conversation.getElementsByTagName('pin')[0].childNodes[0].nodeValue)
	newConversation = Conversation(conversationID, pin)

	#	Get conversation master time offset
	offset = float(conversation.getElementsByTagName('offset')[0].childNodes[0].nodeValue)

	#	Add trigger objects to list
	triggers = conversation.getElementsByTagName('trigger')
	for trigger in triggers:
		if trigger.getAttribute('type').upper() == 'LIGHTING':
			tType = 'Lighting'
			tTime = float(trigger.getElementsByTagName('time')[0].childNodes[0].nodeValue) + offset
			channel = DMX_CHANNELS[str(trigger.getElementsByTagName('DMXchannel')[0].childNodes[0].nodeValue)]
			value = str(trigger.getElementsByTagName('value')[0].childNodes[0].nodeValue)
			if value.upper() == "ON":
				value = "FF"
			elif value.upper() == "OFF":
				value = "00"
			newTrigger = lightingTrigger(tType, tTime, channel, value)
			newConversation.lightingTriggers.append(newTrigger)
		elif trigger.getAttribute('type').upper() == 'AUDIO':
			tType = 'Audio'
			flux = trigger.getElementsByTagName('flux')[0].childNodes[0].nodeValue.zfill(2)
			file = trigger.getElementsByTagName('file')[0].childNodes[0].nodeValue.zfill(3)
			newTrigger = audioTrigger(tType, flux, file)
			newConversation.audioTriggers.append(newTrigger)

	conversationObjects.append(newConversation)

print(str(len(conversationObjects)) + " conversations loaded...")


# Generate snippet object list
snippets = xml.getElementsByTagName('snippet')

for snippet in snippets:
	snippetID = int(snippet.getAttribute('id'))
	duration = float(snippet.getElementsByTagName('duration')[0].childNodes[0].nodeValue)

	newSnippet = Snippet(snippetID, duration)

	triggers = snippet.getElementsByTagName('trigger')
	for trigger in triggers:
		if trigger.getAttribute('type').upper() == 'LIGHTING':
			tType = 'Lighting'
			channel = DMX_CHANNELS[str(snippet.getElementsByTagName('DMXchannel')[0].childNodes[0].nodeValue)]
			newTrigger = lightingTrigger(tType, 0, channel, 'FF')
			newSnippet.lightingTriggers.append(newTrigger)
		elif trigger.getAttribute('type').upper() == 'AUDIO':
			tType = 'Audio'
			flux = trigger.getElementsByTagName('flux')[0].childNodes[0].nodeValue.zfill(2)
			file = trigger.getElementsByTagName('file')[0].childNodes[0].nodeValue.zfill(3)
			newTrigger = audioTrigger(tType, flux, file)
			newSnippet.audioTriggers.append(newTrigger)

	print newSnippet.lightingTriggers[0].channel

	snippetObjects.append(newSnippet)

print snippetObjects[0].audioTriggers[0].file
