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

class OCR:
    def __init__(self):
        self.last_call = None

    def ocr(self, np_img):
        try:
            return pytesseract.image_to_string(np_img, lang='eng')
        except RuntimeError as err:
            print(f"ocr err: {err}")
            return ""

    def numpy_to_base64(self, np_img):
        # Encode image as jpeg
        _, img_encoded = cv2.imencode('.jpg', np_img)
        # Convert to base64
        base64_string = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
        return base64_string

    def rate_limit(self):
        if self.last_call and int(time.monotonic() - self.last_call) < 1:
            time.sleep(1)
        self.last_call = time.monotonic()

    def ocr_yc(self, np_img):
        self.rate_limit()
        
        data = {"mimeType": "JPEG",
                "languageCodes": ["*"],
                "content": self.numpy_to_base64(np_img=np_img)}

        url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {:s}".format(YC_API_KEY),
            "x-data-logging-enabled": "true"
        }
        start = time.monotonic()
        resp = requests.post(url=url, headers=headers, data=json.dumps(data))
        
        try:
            resp.raise_for_status()
        except Exception as e:
            print(f'OCR request failed: {e}')
            return ""
        
        # print('*** Text Detection Time Taken:%.3fs ***' % (time.monotonic() - start))
        result = []
        jresp = resp.json()
        # print(f"{json.dumps(jresp, indent=2)}")
        for block in jresp["result"]["textAnnotation"]["blocks"]:
            for line in block["lines"]:
                for w in line.get("words", []):
                    result.append(w["text"])

        return " ".join(result)