class SimpleMessage:

    def __init__(self, increment=True):
        self.sender = "John Doe"
        self.recipient = "To whom it may concern"
        self.body = "Message"

    def serialize(self):
        return { 'sender_s': self.sender, 'recipient_s': self.recipient, 'body_s': self.body }

    @classmethod
    def deserialize(other, serial):
        other = SimpleMessage(False)
        other.sender = serial['sender_s']
        other.recipient = serial['recipient_s']
        other.body = serial['body_s']
        return other

    def reply(self, body):
        replyString = "\n-------\n|Reply|\n-------\n\n"
        other = SimpleMessage()
        other.body = body + replyString + self.body
        other.sender = self.recipient
        other.recipient = self.sender
        return other
