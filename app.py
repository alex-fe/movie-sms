from datetime import datetime
from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse

from query import movie_data_query, showtimes_query

app = Flask(__name__)


@app.route("/")
def check_app():
    # returns a simple string stating the app is working
    return Response("Hello world"), 200


@app.route("/twilio", methods=['GET', 'POST'])
def inbound_sms():
    """Navigate sms conversation based on received command.
    Returns:
        String response to text back.
    """
    received_sms = request.values.get('Body', None)
    command, received_sms = received_sms.lower().split(maxsplit=1)
    resp = MessagingResponse()
    if command == 'info':
        resp.message(movie_data_query(t=received_sms))
    elif command == 'showtimes':
        title, zipcode = received_sms.rsplit(maxsplit=1)
        date = datetime.today().strftime('%m-%d-%Y')
        showtime_str = showtimes_query(t=title, zip=zipcode, start_date=date)
        resp.message(showtime_str)
    else:
        resp.message("Incorrect command '{}' sent".format(command))
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
