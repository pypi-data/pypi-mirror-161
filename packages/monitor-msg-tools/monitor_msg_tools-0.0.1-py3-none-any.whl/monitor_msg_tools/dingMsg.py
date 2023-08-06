import json
import requests

def msgFormat(Title:str, raw_dic:dict, pat=32,fliter=''):
    '''
    :param Title: msg title
    :param raw_dic: {"a":[1,2,3,4],"b":[2,4,5,6]}
    :param fliter:
    :param pat: '#' length
    :return:
    '''
    # Get failed cases
    topic = '{}:\n{}\n'.format(Title,'#'*pat)
    k = list(raw_dic.keys())
    length = len(k)
    v = list(raw_dic.values())
    valueLength = len(raw_dic[list(raw_dic.keys())[0]])
    if fliter:
        for j in range(valueLength):
            topic_sub = ''
            for i in range(length):
                topic_sub += '{}: {}\n'.format(k[i], v[i][j])
            topic_sub += '\n{}\n'.format('*'*(pat-2))
            if fliter in topic_sub:
                topic += topic_sub
    else:
        for j in range(valueLength):
            for i in range(length):
                topic += '{}: {}\n'.format(k[i], v[i][j])
            topic += '\n{}\n'.format('*'*(pat-2))
    tail = '{}\n'.format('#'*pat)
    return topic + tail

def send_request(msg,url,mobile):
    '''
    :param msg:
    :param url: get it from dingding robot
    :param mobile: 12345678910
    :return:
    '''
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    datas =  {
        "msgtype": "text",
        "text": {
            "content": msg
        },
        "at": {
            "atMobiles": [
                mobile
            ],
            "isAtAll": False
        }
    }
    payload = json.dumps(datas)
    requests.post(url, headers=header,data=payload)

if __name__ == '__main__':
    pass
