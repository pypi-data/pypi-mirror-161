import requests
from typing import Optional


REST = "https://translate.googleapis.com/translate_a/single?hl=ko&dt=t&client=gtx&ie=utf-8"


def translateWithGoogleAPI(text: str, sl: str = 'en', hl: str = 'en', tl: str = 'ko') -> Optional[str]:
    with requests.get(REST, params={"q": text, "sl": sl, "hl": hl, "tl": tl}) as req:
        result = req.json()[0][0][0]
    return result




