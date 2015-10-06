#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import riak

messageStack = Flask(__name__)
myClient = riak.RiakClient(pb_port=10017, protocol='pbc')
myBucket = myClient.bucket('message_test')

class SimpleMessage:
    count = 0

    def __init__(self, increment=True):
        self.sender = "John Doe"
        self.recipient = "To whom it may concern"
        self.body = "Message"
        self.key = SimpleMessage.count
        if increment:
            SimpleMessage.count += 1

    def serialize(self):
        return { 'sender': self.sender, 'recipient': self.recipient, 'body': self.body, 'key': self.key }

    @classmethod
    def deserialize(other, serial):
        other = SimpleMessage(False)
        other.sender = serial['sender']
        other.recipient = serial['recipient']
        other.body = serial['body']
        other.key = serial['key']
        return other

    def reply(self, body):
        replyString = "\n-------\n|Reply|\n-------\n\n"
        other = SimpleMessage()
        other.body = body + replyString + self.body
        other.sender = self.recipient
        other.recipient = self.sender
        return other

    def store(self):
        serial = self.serialize()
        riakKey = myBucket.new(str(self.key), data=serial)
        riakKey.store()


@messageStack.route('/message/<int:keyID>', methods=['GET'])
def get_message(keyID):
    fetch = myBucket.get(str(keyID))
    if (fetch.data is None):
        abort(404)
    return jsonify({'message': fetch.data})

@messageStack.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@messageStack.route('/message', methods=['POST'])
def create_message():
    if not request.json or not ('sender' in request.json and 'recipient' in request.json):
        abort(400)
    newMessage = SimpleMessage()
    newMessage.sender = request.json['sender']
    newMessage.recipient = request.json['recipient']
    newMessage.body = request.json.get('body',"")
    newMessage.store()
    return jsonify({'message': newMessage.serialize()}), 201

@messageStack.route('/message/reply', methods=['POST'])
def reply_message():
    if not request.json or not ('key' in request.json and 'body' in request.json):
        abort(400)
    fetch = myBucket.get(str(request.json['key']))
    if (fetch.data is None):
        abort(400)
    storedMessage = SimpleMessage.deserialize(fetch.data)
    replyMessage = storedMessage.reply(request.json['body'])
    replyMessage.store()
    return jsonify({'message': replyMessage.serialize()}), 201

if __name__ == '__main__':
        messageStack.run(debug=True)
