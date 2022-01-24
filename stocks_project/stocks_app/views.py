from email.quoprimime import quote
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
import json
import finnhub
import spacy
import pandas as pd
from django.conf import settings

finnhub_client = finnhub.Client(api_key=settings.STOCKS_API_KEY)
nlp = spacy.load('en_core_web_sm')
df = pd.read_csv('stocks.csv')
column_symbol = df['Symbol'].tolist()

@csrf_exempt
def stocks(request):
    """
    handles the conversation on whatsapp chatbot

    :param request: message request
    :return: HTTP response

    """ 
    
    incoming_message = receive_message(request)
    incoming_message_doc = nlp(incoming_message)
    valid_response = False
    final_response = {}
    if "hello" in incoming_message:
        valid_response = True
        return send_message(hello())
    
    if "quote" in [token.text for token in incoming_message_doc]:
        valid_response = True
        for token in incoming_message_doc: # evaluate each word in message to look for ticker symbol
            symbol = token.text.upper() # convert symbol string to uppercase
            if symbol in column_symbol: # verify is ticker symbol is valid based on whether it exists in database
                quote_data = finnhub_client.quote(symbol) #obtain data for each valid symbol
                final_response[symbol] = quote_data # create a new entry in dictionary
        json_string = json.dumps(final_response, indent = 6) # convert dictionary to json object
        print(json_string)
        return send_message(json_string)

    if not valid_response:
        valid_response = True
        return send_message(invalid())

def send_message(message, media_url = None):
    """
    sends an outgoing WhatsApp message

    :param message: message body
    :param media_url: optional message media
    :return: HTTP response

    """ 
    response = MessagingResponse()
    response.message().body(message)
    response.message().media(media_url)
    return HttpResponse(str(response))

def receive_message(request):
    """
    receives an incoming WhatsApp message

    :param request: message request 
    :return: message body

    """ 
    if request.method == 'POST':
        return request.POST.get('Body').lower()

# greetings and menu options
def hello():
    """
    sends an outgoing WhatsApp message showing menu options

    :return: menu option string

    """
    return "Greetings! \
            \nEnter *quote <symbols>* to get quote data for stocks.\
            "

# greetings and menu options
def invalid():
    """
    sends a outgoing WhatsApp message for invalid input

    :return: invalid input alert message

    """
    return "Sorry, I don't understand. Please enter *hello* to get started."

