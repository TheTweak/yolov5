import json
import os
import time
import requests

YC_TC_API_KEY = os.getenv("YC_TEXT_CLASS_API_KEY")
assert YC_TC_API_KEY
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/fewShotTextClassification"

def text_is_eula(text):
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
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {:s}".format(YC_TC_API_KEY),
    }
    r = requests.post(URL, data=json.dumps(data), headers=headers)
    r.raise_for_status()
    rj = r.json()
    for p in rj["predictions"]: 
        if p["confidence"] > 0.8:
            return p["label"] == "eula"
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str)
    args = parser.parse_args()
    print(text_is_eula(args.text))
