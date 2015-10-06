#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import riak

messageStack = Flask(__name__)
myClient = riak.RiakClient(pb_port=10017, protocol='pbc')
myBucket = myClient.bucket('message_test')
count = 0

class SimpleMessage:
    def __init__(self):
        global count
        self.sender = "John Doe"
        self.recipient = "To whom it may concern"
        self.body = "Message"
        self.key = count
        count += 1

    def serialize(self):
        return { 'sender': self.sender, 'recipient': self.recipient, 'body': self.body, 'key': self.key }



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
    serial = newMessage.serialize()
    riakKey = myBucket.new(str(newMessage.key), data=serial)
    riakKey.store()
    return jsonify({'message': serial}), 201

if __name__ == '__main__':
        messageStack.run(debug=True)
