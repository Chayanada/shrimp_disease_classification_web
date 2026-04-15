from machine import Pin, ADC, PWM
import time
import urequests
import json

ACCESS_TOKEN = "+rHViq1UWymb2fR3eLMz9IBcbtsK2nvoEzs/7tIuy2upHfYV5WiHWLNJPed4UrMnp1qqGsdFzyIoZr7hP4ssN1uQSzgnUKPVS3Oh4z1vSRVDi1EKwKwwfExGwBeYMcDKw56wo3Z6AkXtvwA4CZ2bpgdB04t89/1O/w1cDnyilFU="
USER_ID = "Ubee98d43c45dadb842391e26aa1835d1"


def send_to_line(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + ACCESS_TOKEN
    }
    payload = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": str(text)
            }
        ]
    }
    body = json.dumps(payload)
    print("payload =", body)
    response = None
    try:
        body = json.dumps(payload)
        response = urequests.post(url, headers=headers, data=body.encode("utf-8"))
        print("status =", response.status_code)
        print("response =", response.text)
    except Exception as e:
        print("LINE error =", e)
    finally:
        if response is not None:
            response.close()