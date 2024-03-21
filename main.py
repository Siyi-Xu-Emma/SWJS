import time
from anyio import sleep
from controller.controller import Controller
from model.OpenAiModel.count_tokens import num_tokens_from_messages
from web_api.dialogue_api import dialogue_api_handler
from flask import Flask, Response, render_template
from flask_restful import Api, reqparse
from flask_cors import CORS
from model.OpenAiModel.envVar import *
import threading
import requests
from PIL import Image
from io import BytesIO

client = CLIENT

app = Flask(__name__)
api = Api(app)
CORS(app)

MainController = Controller()
dialogue_api_hl = dialogue_api_handler()

thread1 = client.beta.threads.create()
thread2 = client.beta.threads.create()
thread3 = client.beta.threads.create()
## create several assistants for different purposes 


parser = reqparse.RequestParser()
parser.add_argument('user_input',type=str,location='json')

def respond(res):
    return {'code':0,'message':'success','res':res}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return "Pong"

@app.route("/echo")
def echo():
    args = parser.parse_args()
    user_request_input = args['user_input']
    return respond(user_request_input)

@app.route("/chat", methods=['POST'])
def chat():
    userInput = parser.parse_args()['user_input']
    if userInput:
        MainController.get_ai_res(userInput)
        print(MainController.output)
        return respond(MainController.output)
    return respond("No input"), 400

@app.route("/post_accident", methods=['POST'])
def post_accident():
    userInput = parser.parse_args()['user_input']
    if userInput and token_check(userInput):
        queue = MainController.route_info_res(userInput, thread3)

        def consumer():
            while True:
                try:
                    message = queue.get()
                    print(f"message is {message}")
                    yield f"data: {message}\n\n"  # Yield messages in the correct format
                except:
                    break
        return Response(consumer(), mimetype='text/event-stream')
    return respond("No input")

@app.route("/route_planner", methods=['POST'])
def route_planner():
    userInput = parser.parse_args()['user_input']
    if userInput and token_check(userInput):
        queue = MainController.route_info_res(userInput, thread2)

        def consumer():
            while True:
                try:
                    message = queue.get()
                    print(f"message is {message}")
                    yield f"data: {message}\n\n"  # Yield messages in the correct format
                except:
                    break
        return Response(consumer(), mimetype='text/event-stream')
    return respond("No input")

@app.route("/route_info", methods=['POST'])
def route_info():
    userInput = parser.parse_args()['user_input']
    if userInput and token_check(userInput):
        queue = MainController.route_info_res(userInput, thread3)

        def consumer():
            while True:
                try:
                    message = queue.get()
                    print(f"message is {message}")
                    yield f"data: {message}\n\n"  # Yield messages in the correct format
                except:
                    break
        return Response(consumer(), mimetype='text/event-stream')
    return respond("No input")

@app.route("/poc", methods=['GET'])
def poc():
    queue = MainController.route_info_res("Please introduce Singapore", thread3)

    def consumer():
        while True:
            try:
                message = queue.get()
                print(f"message is {message}")
                yield f"data: {message}\n\n"  # Yield messages in the correct format
            except:
                break

    return Response(consumer(), mimetype='text/event-stream')


@app.route("/stream", methods=['GET'])
def stream():
    def event_stream():
        for i in range(10):
            message = f"data: {time.time()}\n\n"
            print(f" the type of message is {type(message)}")
            yield message  # Send data to frontend
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')

def token_check(message):
    return len(message) < 4096


prompt_history = []

@app.route("/image", methods = ['GET'])
def image():
    image_url = MainController.get_ai_image_url(prompt_history)  # Replace with your image URL
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        image.show()  # Display the image
        return "Image displayed successfully"
    else:
        return "Failed to retrieve image"



'''
print(MainController.route_info_res("hi", thread3))
print(MainController.route_planner_res("hi", thread2))
print(MainController.post_accident_bot_res("hi", thread1))
'''
print("\n\n\nnow try run route_info_res\n\n\n")


##########################
# Test the event handler #
##########################


def process_stream():
    MainController.route_info_res("hi, please provide specific road info on a rainy day in singapore, better include pricing models", thread3)

def monitor_output():
    output = ""
    while MainController.isProcessing :
        if MainController.output and MainController.output != output:
            print(MainController.output, end = "")
            output = MainController.output

# Create threads
t1 = threading.Thread(target = process_stream)
t2 = threading.Thread(target = monitor_output)

# Start threads
#t1.start()
#t2.start()




'''
MainController.route_info_res("hi", thread3)
i = 0
while(MainController.eventHandler.isProcessing):
    print(f"yes{i}")
    if i > 10:
        break
    print(MainController.eventHandler.output)
    i += 1
'''








if __name__ == '__main__':
    print("Starting server on port :80")
    app.run(host='0.0.0.0', port=80, debug=True)


