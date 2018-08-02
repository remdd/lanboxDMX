#	Class definitions
class Conversation:
	def __init__(self, conversationID, pin):
		self.id = conversationID
		self.pin = pin
		self.triggers = []

class Trigger:
	def __init__(self, tType, tTime, channel, value):
		self.tType = tType
		self.time = tTime
		self.channel = channel
		self.value = value

class Snippet:
	def __init__(self, snippetID, channel, duration):
		self.id = snippetID
		self.channel = channel
		self.duration = duration


import xml.dom.minidom
xml = xml.dom.minidom.parse('content.xml')


# Set DMX universe
DMX_UNIVERSE = str(xml.getElementsByTagName('DMXuniverse')[0].childNodes[0].nodeValue)
print "DMX Universe ID is: " + DMX_UNIVERSE


# Generate DMX Channel dictionary
DMXchannels = xml.getElementsByTagName('DMXchannel')
DMX_CHANNELS = {}
for DMXchannel in DMXchannels:
	DMX_CHANNELS[DMXchannel.getAttribute('name')] = DMXchannel.childNodes[0].nodeValue

for key in sorted(DMX_CHANNELS.iterkeys()):
	print key + ' is on DMX channel ' + str(DMX_CHANNELS[key])


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
		if trigger.getAttribute('type') == 'Lighting':
			tType = 'Lighting'
			tTime = float(trigger.getElementsByTagName('time')[0].childNodes[0].nodeValue) + offset
			channel = DMX_CHANNELS[str(trigger.getElementsByTagName('channel')[0].childNodes[0].nodeValue)]
			value = str(trigger.getElementsByTagName('value')[0].childNodes[0].nodeValue)
			if value.upper() == "ON":
				value = "FF"
			elif value.upper() == "OFF":
				value = "00"
		newTrigger = Trigger(tType, tTime, channel, value)
		newConversation.triggers.append(newTrigger)
	conversationObjects.append(newConversation)

print(str(len(conversationObjects)) + " conversations loaded...")


# Generate snippet object list
snippets = xml.getElementsByTagName('snippet')

for snippet in snippets:
	snippetID = int(snippet.getAttribute('id'))
	channel = DMX_CHANNELS[str(snippet.getElementsByTagName('channel')[0].childNodes[0].nodeValue)]
	duration = float(snippet.getElementsByTagName('duration')[0].childNodes[0].nodeValue)
	newSnippet = Snippet(snippetID, channel, duration)
	snippetObjects.append(newSnippet)


