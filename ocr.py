import base64
import pytesseract
import requests
import time
import json
import cv2
import os

YC_API_KEY = os.getenv("YC_API_KEY")
assert YC_API_KEY
print(f"api_key: {YC_API_KEY[:8]}")

def ocr(np_img):
    try:
        return pytesseract.image_to_string(np_img, lang='eng')
    except RuntimeError as err:
        print(f"ocr err: {err}")
        return ""


def numpy_to_base64(np_img):
    # Encode image as jpeg
    _, img_encoded = cv2.imencode('.jpg', np_img)
    # Convert to base64
    base64_string = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
    return base64_string


def ocr_yc(np_img):
    data = {"mimeType": "JPEG",
            "languageCodes": ["*"],
            "content": numpy_to_base64(np_img=np_img)}

    url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {:s}".format(YC_API_KEY),
        "x-data-logging-enabled": "true"
    }
    start = time.monotonic()
    w = requests.post(url=url, headers=headers, data=json.dumps(data))
    w.raise_for_status()
    print('*** Text Detection Time Taken:%.3fs ***' % (time.monotonic() - start))
    result = []
    for block in w.json()["result"]["textAnnotation"]["blocks"]:
        for line in block["lines"]:
            for w in line.get("words", []):
                result.append(w["text"])

    return " ".join(result)