from django.shortcuts import render

# Create your views here.

import json, requests, random, re
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

PAGE_ACCESS_TOKEN = "EAAC7hsC2C0sBAOdnesyZAKMZAhRZC9EvVxW9j1RscX7TZByH2ZA9WFnUyqmy9ywvBXZBVHq9Nvu9SZBk6vfutctQuvhqcSIQ6IMyrPbcBDvj5gQzOSIl01JS2FnKEA4ylbP35pNedZBkHIGFKO9d0nZBVaA37W6CHyqYFRtD96EZBLAwZDZD"
VERIFY_TOKEN = "2318934571"


quotes = { 
         'happy': 
         ["Be happy for this moment. This moment is your life.",
                   "The most important thing is to enjoy your life - to be happy - it's all that matters.",
                   "I just find myself happy with the simple things. Appreciating the blessings God gave me."], 

         'inspiration': 
         ["The best preparation for tomorrow is doing your best today.",
                     "Put your heart, mind, and soul into even your smallest acts. This is the secret of success.",
                     "Keep your face always toward the sunshine - and shadows will fall behind you."],

          'friendship' : 
          ["Friends show their love in times of trouble, not in happiness.",
           "The greatest gift of life is friendship, and I have received it.",
           "There is nothing on this earth more to be prized than true friendship."
            ],
}

convos = {
    'hi': ["Hi!! B)", 
           """Hey there, you ain't using whatsapp :P""", 
           "Hey Pudding",
           ],
         
}

convos_end = {
	'bye': ["Bbye buddy! See ya :D",
			"Jaa na velle!! :/"],
	'tata': ["Bbye buddy! See ya :D",
			"Jaa na velle!! :/"],
}

convos_overhead = {
    'quotes' : """Type happy or inspiration or friendship to get happy/inspiration/friendship quotes""",
}

joke_lines = {
    'jokes' : ["""Life is like toilet paper, you're either on a roll or taking shit from some asshole.""",
               """You know you're ugly when it comes to a group picture and they hand you the camera.""",
               """ My wife and I were happy for twenty years. Then we met.""",
               """Isn't it great to live in the 21st century? Where deleting history has become more important than making it.""",
               """You're not fat, you're just... easier to see.""",
               """Politicians and diapers have one thing in common. They should both be changed regularly, and for the same reason.""",
               ]
}

def post_facebook_message(fbid, recevied_message):           
    
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    send_text = ''
    flag = ''
    greeting_img = ''

            
    for token in tokens:
        if token in convos:
            flag = "overhead_message"
            greeting_img = "true"
            send_text = random.choice(convos[token])
            break

        elif token in convos_overhead:
            send_text = convos_overhead[token]
            # pprint(convos_overhead[token])
            break

        elif token in quotes:
            flag = "overhead_message"
            send_text = random.choice(quotes[token])
            break
        
        elif token in joke_lines:
            flag = "overhead_message"
            send_text = random.choice(joke_lines[token])
            break

        elif token in convos_end:
            send_text = random.choice(convos_end[token])
            break
        # elif token in quotes and flag != "quotes":
        #     send_text = """Type 'quotes' to get some quotes or 'jokes' to have some jokes"""
    if not send_text:
        flag = "marega"
        send_text = """I didn't understand! Type 'quotes' to get some quotes or 'jokes' to get cracked up"""



    # user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    # user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':'EAAC7hsC2C0sBAOdnesyZAKMZAhRZC9EvVxW9j1RscX7TZByH2ZA9WFnUyqmy9ywvBXZBVHq9Nvu9SZBk6vfutctQuvhqcSIQ6IMyrPbcBDvj5gQzOSIl01JS2FnKEA4ylbP35pNedZBkHIGFKO9d0nZBVaA37W6CHyqYFRtD96EZBLAwZDZD'} 
    # user_details = requests.get(user_details_url, user_details_params).json() 
    # for key in user_details.keys(): 
    #     pprint(key)
    # # pprint(user_details['first_name'])
    # send_text = 'Yo '+ user_details['first_name'] + '..! ' + send_text

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":send_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    if flag == "overhead_message":
        flag = ''
        response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":"""Type 'quotes' to get some quotes or 'jokes' to get cracked up"""}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg) 
    # if greeting_img == "true":
    #     greeting_img = ''
    #     response_img = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image","payload":{"url":"http://www.imagesbuddy.com/images/199/hi-friend-chicken-graphic.jpg"}}}})
    #     status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_img) 
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