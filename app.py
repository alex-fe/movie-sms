from datetime import datetime
from flask import Flask, render_template, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from private_info import TWILIO_AUTH_TOKEN, TWILIO_SID

from query import movie_data_query, showtimes_query


COMMANDS = ['info', 'showtimes']
DEFAULT_ERR_MESSAGE = "{reason}. Please try again using 'info' or 'showtimes'."

app = Flask(__name__,  template_folder='templates')
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)


@app.route("/", methods=['GET'])
def check_app():
    return render_template('main.html', messages=client.messages.list())


@app.template_filter('strftime')
def _filter_datetime(date):
    return datetime.strftime(date, '%c')


@app.route("/movies", methods=['GET', 'POST'])
def inbound_sms():
    """Navigate sms conversation based on received command.
    Returns:
        String response to text back.
    """
    received_sms = request.values.get('Body', None)
    resp = MessagingResponse()
    try:
        command, received_sms = received_sms.lower().split(maxsplit=1)
    except AttributeError:
        resp.message(
            DEFAULT_ERR_MESSAGE.format(reason='Incoming message was blank')
        )
    else:
        if command == 'info':
            resp.message(movie_data_query(t=received_sms))
        elif command == 'showtimes':
            title, zipcode = received_sms.rsplit(maxsplit=1)
            date = datetime.today().strftime('%m-%d-%Y')
            showtime_str = showtimes_query(
                t=title, zip=zipcode, start_date=date
            )
            resp.message(showtime_str)
        else:
            resp.message(
                DEFAULT_ERR_MESSAGE
                .format(
                    reason="Command '{}' not included in acceptable commands"
                    .format(command)
                )
            )
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
