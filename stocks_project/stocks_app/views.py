from email.quoprimime import quote
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from django.conf import settings

import re
import os

import finnhub
import pandas as pd
finnhub_client = finnhub.Client(api_key=settings.STOCKS_API_KEY)

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
    incoming_message_word_list = re.compile('\w+').findall(incoming_message)
    valid_response = False

    if "hello" in incoming_message:
        valid_response = True
        return send_message(hello())
    
    quote_dict = {}
    for word in incoming_message_word_list: # evaluate each word in message to look for ticker symbol
        symbol = word.upper() # convert symbol string to uppercase
        if symbol in column_symbol: # verify is ticker symbol is valid based on whether it exists in database
            valid_response = True
            resp_attr_dict = finnhub_client.quote(symbol) # obtain data for each valid symbol
            quote_dict[symbol] = resp_attr_dict # create a new entry in dictionary
        else:
            valid_response = False
        if not valid_response:
            return send_message(invalid())
    return send_message(format_quote_dict(quote_dict))

    """
    extracts data from quote dictionary of quote data dictionaries and
    stores it in appropriate variables

    :param dict_2D: double dimensional dictionary
    :return: formatted string

    """ 
def format_quote_dict(dict_2D):
    dictionary_string = ""
    for key, value in dict_2D.items():
        symbol = key
        current_price = value.get('c')
        change = value.get('d')
        percent_change = value.get('dp')
        high_price = value.get('h')
        low_price = value.get('l')
        open_price = value.get('o')
        previous_close = value.get('pc')

        dictionary_string += """{symbol}
        Current price : ${current_price}
        Change : {change}
        Percent change : {percent_change}%
        High price : ${high_price}
        Low price : ${low_price}
        Open price : ${open_price}
        Previous close : ${previous_close}\n""".format(symbol = symbol, 
                current_price = current_price, 
                change = change,
                percent_change = percent_change,
                high_price = high_price,
                low_price = low_price,
                open_price = open_price,
                previous_close = previous_close)

    return dictionary_string

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
    return """Greetings!
Enter *<symbols>* to get quote data for stocks."""

# greetings and menu options
def invalid():
    """
    sends a outgoing WhatsApp message for invalid input

    :return: invalid input alert message

    """
    return "Sorry, I don't understand. Please check your input."

