import json
import os
import time
import requests

YC_TC_API_KEY = os.getenv("YC_TEXT_CLASS_API_KEY")
assert YC_TC_API_KEY
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/fewShotTextClassification"

class TextClassifier:
    def __init__(self):
        self.last_call = None

    def rate_limit(self):
        if self.last_call and int(time.monotonic() - self.last_call) < 1:
            time.sleep(1)
        self.last_call = time.monotonic()

    def make_prediction(self, data, target_label):
        self.rate_limit()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key {:s}".format(YC_TC_API_KEY),
        }
        r = requests.post(URL, data=json.dumps(data), headers=headers)

        try:
            r.raise_for_status()
        except Exception as e:
            print(f"text classification request failed: {e}")
            return ""

        rj = r.json()
        for p in rj["predictions"]: 
            if p["confidence"] > 0.8:
                return p["label"] == target_label
        return False


    def text_is_eula(self, text):
        data = {
            "modelUri": "cls://b1gf95a5ggkka05fjvk6/yandexgpt/latest",
            "taskDescription": "detect EULA",
            "labels": [
                "eula",
                "non-eula"
            ],
            "text": text,
            "samples": [
                {
                    "text": "Please read this agreement in its entirety. You must agree to the terms of the EULA to play",
                    "label": "eula"
                },
                {
                    "text": "Cloud data is out of sync",
                    "label": "non-eula"
                }
            ]
        }
        return self.make_prediction(data, "eula")


    def text_is_accept(self, text):
        data = {
            "modelUri": "cls://b1gf95a5ggkka05fjvk6/yandexgpt/latest",
            "taskDescription": "detect accept buttons",
            "labels": [
                "accept",
                "non-accept"
            ],
            "text": text,
            "samples": [
                {
                    "text": "Accept",
                    "label": "accept"
                },
                {
                    "text": "OK",
                    "label": "accept"
                },
                {
                    "text": "Yes",
                    "label": "accept"
                },
                {
                    "text": "Принять",
                    "label": "accept"
                },
                {
                    "text": "Да",
                    "label": "accept"
                },
                {
                    "text": "Continue",
                    "label": "accept"
                },
                {
                    "text": "Продолжить",
                    "label": "accept"
                },                                            
                {
                    "text": "Cancel",
                    "label": "non-accept"
                },
                {
                    "text": "No",
                    "label": "non-accept"
                },
                {
                    "text": "Abort",
                    "label": "non-accept"
                },
                {
                    "text": "Exit",
                    "label": "non-accept"
                },
                {
                    "text": "Отмена",
                    "label": "non-accept"
                },
                {
                    "text": "Нет",
                    "label": "non-accept"
                }
            ]
        }
        return self.make_prediction(data, "accept")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str)
    args = parser.parse_args()
    tc = TextClassifier()
    print(tc.text_is_accept(args.text))
