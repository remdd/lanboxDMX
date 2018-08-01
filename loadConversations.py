#	Conversation class definitions
class Conversation:
	def __init__(self, number):
		self.number = number
		self.triggers = []

class Trigger:
	def __init__(self, tType, tTime, channel, value):
		self.tType = tType
		self.time = tTime
		self.channel = channel
		self.value = value


# Read XML and build up conversation object list
import xml.dom.minidom
xml = xml.dom.minidom.parse('conversations.xml')
conversations = xml.getElementsByTagName('conversation')

for conversation in conversations:
	newConversation = Conversation(int(conversation.getAttribute('number')))

	triggers = conversation.getElementsByTagName('trigger')
	for trigger in triggers:
		if trigger.getAttribute('type') == 'Lighting':
			tType = 'Lighting'
			tTime = float(trigger.getElementsByTagName('time')[0].childNodes[0].nodeValue)
			channel = DMX[str(trigger.getElementsByTagName('channel')[0].childNodes[0].nodeValue)]
			value = str(trigger.getElementsByTagName('value')[0].childNodes[0].nodeValue)

		newTrigger = Trigger(tType, tTime, channel, value)
		print newTrigger.value
		newConversation.triggers.append(newTrigger)

	conversationObjects.append(newConversation)

print(str(len(conversationObjects)) + " conversations loaded...")

# print conversationObjects[0].triggers[0].channel
