import os
import requests
import flask
from app.whatsapp_client import WhatsAppClient

app = flask.Flask(__name__)

nest_asyncio.apply()

WHATSAPP_HOOK_TOKEN = os.environ.get("WHATSAPP_HOOK_TOKEN")

@app.route('/')
def I_am_alive():
    return "¡Estoy vivo!"

@app.route("/webhook/", methods=['GET', 'POST'])
def subscribe(request: Request):
    print("subscribe ha sido llamado")
    if request.query_params.get('hub.verify_token') == WHATSAPP_HOOK_TOKEN:
        return int(request.query_params.get('hub.challenge'))
    return "Authentication failed. Invalid Token."

@app.route("/webhook/", methods=['GET', 'POST'])
async def callback(request: Request):
    print("callback ha sido llamado")
    wtsapp_client = WhatsAppClient()
    data = await request.json()
    print ("We received " + str(data))
    response = wtsapp_client.process_notification(data)
    if response["statusCode"] == 200:
        if response["body"] and response["from_no"]:
            reply = response["body"]
            print ("\nreply is:"  + reply)
            wtsapp_client.send_text_message(message=reply, phone_number=response["from_no"], )
            print ("\nreply is sent to whatsapp cloud:" + str(response))

    return {"status": "success"}, 200


if __name__ == '__main__':
    app.run()
