import re
import requests

BASE = 'https://m.search.naver.com/p/csearch/ocontent/spellchecker.nhn'
CALLBACK = 'jQuery112401798084558511126_1659174678572'

HEADER = {
    'referer': 'https://search.naver.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/57.0.2987.133 Safari/537.36 '
}


def extract(text: str) -> dict:
    text = re.sub(CALLBACK + "\(", "", text)
    text = re.sub("\);$", "", text)
    return eval(text)['message']['result']


def spell_check(text: str, only_text=True) -> str:
    try:
        with requests.Session() as req:
            payload = {'_callback': CALLBACK, 'q': text}
            original_text = req.get(BASE, params=payload, headers=HEADER).text
        data = extract(original_text)
        if only_text:
            return data['notag_html']
        return data
    except Exception as e:
        return text
