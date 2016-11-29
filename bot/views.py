
import json, requests, random, re
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

PAGE_ACCESS_TOKEN = "EAAC7hsC2C0sBAOdnesyZAKMZAhRZC9EvVxW9j1RscX7TZByH2ZA9WFnUyqmy9ywvBXZBVHq9Nvu9SZBk6vfutctQuvhqcSIQ6IMyrPbcBDvj5gQzOSIl01JS2FnKEA4ylbP35pNedZBkHIGFKO9d0nZBVaA37W6CHyqYFRtD96EZBLAwZDZD"
VERIFY_TOKEN = "2318934571"


convos = { 
         'hi': ["Hi!! Type happy - for mood lightening quotes, inspirational - for some life lesson quotes, friendship - to get some friendship quotes "],
         
         'quotes': ["Type happy-inspirational-friendship to get the quotes"],
         
         'happy': 
         ["Be happy for this moment. This moment is your life.",
                   "The most important thing is to enjoy your life - to be happy - it's all that matters.",
                   "I just find myself happy with the simple things. Appreciating the blessings God gave me."], 

         'inspirational': 
         ["The best preparation for tomorrow is doing your best today.",
                     "Put your heart, mind, and soul into even your smallest acts. This is the secret of success.",
                     "Keep your face always toward the sunshine - and shadows will fall behind you."],

          'friendship' : 
          ["Friends show their love in times of trouble, not in happiness.",
           "The greatest gift of life is friendship, and I have received it.",
           "There is nothing on this earth more to be prized than true friendship."
            ],
}


def post_facebook_message(fbid, recevied_message):           
    
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    quote_text = ''
    for token in tokens:
        if token in convos:
            quote_text = random.choice(convos[token])
            break
    if not quote_text:
        quote_text = "I didn't understand! Type happy-inspirational-friendship to get the quotes"



    # user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
    # user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':'EAAC7hsC2C0sBAOdnesyZAKMZAhRZC9EvVxW9j1RscX7TZByH2ZA9WFnUyqmy9ywvBXZBVHq9Nvu9SZBk6vfutctQuvhqcSIQ6IMyrPbcBDvj5gQzOSIl01JS2FnKEA4ylbP35pNedZBkHIGFKO9d0nZBVaA37W6CHyqYFRtD96EZBLAwZDZD'} 
    # user_details = requests.get(user_details_url, user_details_params).json() 
    # quote_text = 'Yo '+user_details['first_name']+'..! ' + quote_text

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAC7hsC2C0sBAOdnesyZAKMZAhRZC9EvVxW9j1RscX7TZByH2ZA9WFnUyqmy9ywvBXZBVHq9Nvu9SZBk6vfutctQuvhqcSIQ6IMyrPbcBDvj5gQzOSIl01JS2FnKEA4ylbP35pNedZBkHIGFKO9d0nZBVaA37W6CHyqYFRtD96EZBLAwZDZD' 
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":quote_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())


class RadonBotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)  
                    post_facebook_message(message['sender']['id'], message['message']['text'])    
        return HttpResponse()