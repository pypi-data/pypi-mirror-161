import base64
import requests
import json, uuid
def get_voice(text,root_path, langeCode='vi-VN',name=None,effect="telephony-class-application"):
    try:
        if name==None:
            name=f"{langeCode}-Wavenet-B"
        headers = {
            'x-origin': 'https://explorer.apis.google.com',
            'content-type': 'application/json',
            'Content-Type': 'text/plain',
        }

        params = (
            ('key', 'AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM'),
            ('alt', 'json'),
        )

        data_request = {
            "input": {
                "text": text
            },
            "voice": {
                "languageCode": langeCode,
                "name": name
            },
            "audioConfig": {
                "audioEncoding": "MP3_64_KBPS",
                "pitch": 0,
                "speakingRate": 1,
                "effectsProfileId": [effect]
            }
        }

        response = requests.post('https://content-texttospeech.googleapis.com/v1beta1/text:synthesize', headers=headers, params=params, json=data_request)

        data = json.loads(response.text)
        base64_message = data['audioContent']

        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        str(uuid.uuid4())
        path_voice = f"{root_path}/voice-{str(uuid.uuid4())}.mp3"
        with open(path_voice, 'wb') as file_to_save:
            file_to_save.write(message_bytes)
    except:
        pass
        return None
    return path_voice