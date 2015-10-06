#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import raik

messageStack = Flask(__name__)
myClient = riak.RiakClient(pb_port=10017, protocol='pbc')
myBucket = myClient.bucket('message_test')
count = 0

class SimpleMessage:
    sender
    recipient
    body
    key

    def __init__(self)
        sender = "John Doe"
        recipient = "To whom it may concern"
        body = "Message"
        key = count
        count++



@messageStack.route('/message/<int:keyID>', methods=['GET'])
def get_message(keyID):
    fetch = myBucket.get(keyID)
    if (fetch is None):
        abort(404)
    return jsonify({'message': fetch})

@messageStack.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@messageStack.route('/message/add', methods=['POST'])
def create_message():
    if not request.json or not ('sender' in request.json and 'recipient' in request.json):
        abort(400)
    newMessage = SimpleMessage()
    newMessage.sender = request.json['sender']
    newMessage.recipient = request.json['recipient']
    newMessage.body = request.json.get('body',"")
    raikKey = myBucket.new(newMessage.key, data=newMessage)
    raikKey.store()
    return jsonify({'message': newMessage}), 201
