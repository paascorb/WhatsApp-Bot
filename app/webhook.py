import os
from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder

class WhatsAppWrapper:

    API_URL = "https://graph.facebook.com/v18.0/"
    WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")
    WHATSAPP_CLOUD_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self.API_URL = self.API_URL + self.WHATSAPP_CLOUD_NUMBER_ID

    def send_template_message(self, template_name, language_code, phone_number):

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        print(self.WHATSAPP_API_TOKEN)
        response = requests.post(f"{self.API_URL}/messages", json=payload,headers=self.headers)
        print(response)
        print(response.status_code)
        print(response.text)

        assert response.status_code == 200, "Error sending message"
        return response.status_code
    
    def send_text_message(self,message, phone_number):
        payload = {
            "messaging_product": 'whatsapp',
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        response = requests.post(f"{self.API_URL}/messages", json=payload,headers=self.headers)
        print(response.status_code)
        print(response.text)
        assert response.status_code == 200, "Error sending message"
        return response.status_code
    
    def process_notification(self, data):
        entries = data["entry"]
        for entry in entries:
            for change in entry["changes"]:
                value = change["value"]
                if value:
                    if "messages" in value:
                        for message in value["messages"]:
                            if message["type"] == "text":
                                from_no = message["from"]
                                message_body = message["text"]["body"]
                                prompt = message_body
                                print(f"Ack from FastAPI-WtsApp Webhook: {message_body}")
                                return {
                                    "statusCode": 200,
                                    "body": prompt,
                                    "from_no": from_no,
                                    "isBase64Encoded": False
                                }

        return {
            "statusCode": 403,
            "body": json.dumps("Unsupported method"),
            "isBase64Encoded": False
        }

app = FastAPI()

WHATSAPP_HOOK_TOKEN = os.environ.get("WHATSAPP_HOOK_TOKEN")

@app.get("/")
def I_am_alive():
    return "¡Estoy vivo!"
    
@app.get("/webhook/")
async def subscribe(request: Request):
    print("Se ha llamado a subscribe")
    if request.method == "GET":
        print("Hola")
        if request.query_params.get('hub.verify_token') == WHATSAPP_HOOK_TOKEN:
            return int(request.query_params.get('hub.challenge'))
        print("Hola2")
        wtsapp_client = WhatsAppClient()
        data = await request.json()
        print ("We received " + str(data))
        response = wtsapp_client.process_notification(data)
        if response["statusCode"] == 200:
            if response["body"] and response["from_no"]:
                openai_client = OpenAIClient()
                reply = openai_client.complete(prompt=response["body"])
                print ("\nreply is:"  + reply)
                wtsapp_client.send_text_message(message=reply, phone_number=response["from_no"], )
                print ("\nreply is sent to whatsapp cloud:" + str(response))
    
        return jsonable_encoder({"status": "success"}, 200)
        #return "Authentication failed. Invalid Token."
    

@app.post("/webhook/")
async def process_notifications(request: Request):
    print("Se ha llamado a callback")
    wtsapp_client = WhatsAppClient()
    data = request.json()
    print ("We received " + str(data))
    response = wtsapp_client.process_notification(data)
    if response["statusCode"] == 200:
        if response["body"] and response["from_no"]:
            openai_client = OpenAIClient()
            reply = openai_client.complete(prompt=response["body"])
            print ("\nreply is:"  + reply)
            wtsapp_client.send_text_message(message=reply, phone_number=response["from_no"], )
            print ("\nreply is sent to whatsapp cloud:" + str(response))

    return jsonable_encoder({"status": "success"}, 200)
