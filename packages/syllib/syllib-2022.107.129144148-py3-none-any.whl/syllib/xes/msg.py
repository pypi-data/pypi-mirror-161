from .api import get_run_token
import requests
import json
import time


def send(mobile: int, content: str) -> bool:
    params = {'mobile': mobile, 'content': content}
    headers = {'Cookie': f'xes_run_token={get_run_token()};'}
    res = requests.get('https://code.xueersi.com/api/ai/python_sms/send', params=params, headers=headers)
    res.encoding = 'utf-8'
    try:
        res_dict = json.loads(res.text)
        if res_dict["stat"] != 1:
            return False
        if res_dict["data"]["state"] != 'SUCCESS':
            return False
        params = {'batchId': res_dict["data"]["batchId"], "mobile": mobile}
        time.sleep(5)
        for i in range(4):
            res = requests.get("https://code.xueersi.com/api/ai/python_sms/report", params=params, headers=headers)
            res.encoding = 'utf-8'
            res_dict = json.loads(res.text)
            if res_dict["data"]["msg"] is not None:
                return False
            time.sleep(4)
        return True
    except:
        return False
