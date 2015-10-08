import riak

class SimpleMessage:

    def __init__(self, increment=True):
        self.sender = "John Doe"
        self.recipient = "To whom it may concern"
        self.body = "Message"

    def serialize(self):
        return { 'sender': self.sender, 'recipient': self.recipient, 'body': self.body }

    @classmethod
    def deserialize(other, serial):
        other = SimpleMessage(False)
        other.sender = serial['sender']
        other.recipient = serial['recipient']
        other.body = serial['body']
        return other

    def reply(self, body):
        replyString = "\n-------\n|Reply|\n-------\n\n"
        other = SimpleMessage()
        other.body = body + replyString + self.body
        other.sender = self.recipient
        other.recipient = self.sender
        return other


