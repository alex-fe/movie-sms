from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse

from query import movie_data_query

app = Flask(__name__)


@app.route("/")
def check_app():
    # returns a simple string stating the app is working
    return Response("Hello world"), 200


@app.route("/twilio", methods=['GET', 'POST'])
def inbound_sms():
    received_sms = request.values.get('Body', None)
    command, *title, zipcode = received_sms.lower().split()

    resp = MessagingResponse()
    if command == 'info':
        resp.message(movie_data_query(t=title))
    else:
        resp.message(title)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
