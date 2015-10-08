#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import riak
from simplemessage import SimpleMessage

messageStack = Flask(__name__)
myClient = riak.RiakClient(pb_port=10017, protocol='pbc')
myClient.create_search_index('sendersearch')
myBucket = myClient.bucket('message_test')
myBucket.set_properties({'search_index': 'sendersearch'})

def store(message):
	riakObj = riak.RiakObject(myClient, myBucket)
	riakObj.data = message.serialize()
	riakObj.store()
        return riakObj

@messageStack.route('/message/view/<key>', methods=['GET'])
def get_message(key):
    fetch = myBucket.get(key)
    if (fetch.data is None):
        abort(404)
    print fetch.data
    return jsonify({'message': fetch.data}), 200

@messageStack.route('/message/<key>', methods=['DELETE'])
def delete_message(key):
    fetch = myBucket.get(key)
    if (fetch.data is None):
        abort(404)
    storedMessage = SimpleMessage.deserialize(fetch.data)
    fetch.delete()
    return jsonify({'message': storedMessage.serialize()}), 200

@messageStack.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@messageStack.route('/message/', methods=['POST'])
def create_message():
    if not request.json or not ('sender_s' in request.json and 'recipient_s' in request.json):
        abort(400)
    newMessage = SimpleMessage()
    newMessage.sender = request.json['sender_s']
    newMessage.recipient = request.json['recipient_s']
    newMessage.body = request.json.get('body_s',"")
    riakObj = store(newMessage)
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
    riakObj = store(replyMessage)
    return jsonify({'key': riakObj.key, 'message': replyMessage.serialize()}), 201

@messageStack.route('/message/search/bysender/<sender>', methods=['GET'])
def search_sender(sender):
    search_results = myClient.fulltext_search('sendersearch', 'sender_s:'+sender+'*')
    return jsonify({'messages': search_results}), 200

@messageStack.route('/message/search/byrecipient/<recipient>', methods=['GET'])
def search_recipient(recipient):
    search_results = myClient.fulltext_search('sendersearch', 'recipient_s:'+recipient+'*')
    return jsonify({'messages': search_results}), 200


if __name__ == '__main__':
        messageStack.run(debug=True)
