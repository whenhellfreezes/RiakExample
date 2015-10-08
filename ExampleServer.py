#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import riak
from simplemessage import SimpleMessage

messageStack = Flask(__name__)
myClient = riak.RiakClient(pb_port=10017, protocol='pbc')
myBucket = myClient.bucket('message_test')

def store(message, client, bucket):
	riakObj = riak.RiakObject(client, bucket)
	riakObj.content_type = 'application/json'
	riakObj.data = message.serialize()
	riakObj.store()
        return riakObj

@messageStack.route('/message/<key>', methods=['GET'])
def get_message(key):
    fetch = myBucket.get(key)
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
    riakObj = store(newMessage, myClient, myBucket)
    return jsonify({'key': riakObj.key, 'message': newMessage.serialize()}), 201

@messageStack.route('/message/reply', methods=['POST'])
def reply_message():
    if not request.json or not ('key' in request.json and 'body' in request.json):
        abort(400)
    fetch = myBucket.get(request.json['key'])
    if (fetch.data is None):
        abort(404)
    storedMessage = SimpleMessage.deserialize(fetch.data)
    replyMessage = storedMessage.reply(request.json['body'])
    riakObj = store(replyMessage, myClient, myBucket)
    return jsonify({'key': riakObj.key, 'message': newMessage.serialize()}), 201

if __name__ == '__main__':
        messageStack.run(debug=True)
