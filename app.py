from flask import Flask, Response
from twilio.twiml.messaging_response import Message, MessagingResponse


app = Flask(__name__)


@app.route("/")
def check_app():
    # returns a simple string stating the app is working
    return Response("Hello world"), 200


@app.route("/twilio", methods=["POST"])
def inbound_sms():
    # message_body = request.form['Body']
    resp = MessagingResponse()

    # replyText = getReply(message_body)
    resp.message('Hello')
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
