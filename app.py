from datetime import datetime
from flask import Flask, Markup, render_template, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from private_info import TWILIO_AUTH_TOKEN, TWILIO_SID

from query import movie_data_query, showtimes_query

app = Flask(__name__,  template_folder='templates')
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)


@app.route("/", methods=['GET'])
def check_app():
    return render_template('main.html', messages=client.messages.list())


@app.template_filter('number')
def _convert_phone_number(p):
    return p[:2] + '.' + p[2:5] + '.' + p[5:8] + '.' + p[8:]


@app.template_filter('newline')
def _breakline(text):
    return Markup(text.replace('\n', '<br>'))


@app.template_filter('strftime')
def _filter_datetime(date):
    return datetime.strftime(date, '%c')


@app.route("/movies", methods=['GET', 'POST'])
def inbound_sms():
    """Navigate sms conversation based on received command.
    Returns:
        String response to text back.
    """
    message_body = request.form['Body'].lower()
    message_body_split = message_body.split()
    resp = MessagingResponse()
    if not message_body:
        resp.message('Incoming message was blank.')
    elif message_body_split[0] != 'showtimes':
        resp.message(movie_data_query(t=message_body))
    else:
        title = client.messages.list()[2].body.strip().lower()
        zipcode = message_body_split[1]
        date = datetime.today().strftime('%m-%d-%Y')
        showtime_str = showtimes_query(t=title, zip=zipcode, start_date=date)
        resp.message(showtime_str)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
