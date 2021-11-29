import configparser
import random
import json
import time
import re
import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "cookie": ""
}
sleep_time = 3


def config():
    ck = []
    cp = configparser.RawConfigParser()
    cp.read('config.ini')
    ck.append(cp.get('cookies', 'cookie1'))
    return ck


def dt_list(id, cookie):
    dict = {}

    url = 'https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost_detail?dynamic_id={}'
    url2 = 'https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost_detail?dynamic_id={}&offset={}'
    headers['cookie'] = cookie
    res = requests.get(url.format(id), headers=headers)
    res = res.json()
    off = 0
    c = 0
    try:
        for i in res['data']['items']:
            dict[i['desc']['user_profile']['info']['uid']] = i['desc']['user_profile']['info']['uname']
        if 'offset' in res['data']:
            off = res['data']['offset']
        c += 1
    except:
        pass
    转发总数 = res['data']['total']
    while c < 转发总数 / 20:
        try:
            res = requests.get(url2.format(id, off), headers=headers)
            res = res.json()
            for i in res['data']['items']:
                dict[i['desc']['user_profile']['info']['uid']] = i['desc']['user_profile']['info']['uname']
            if 'offset' in res['data']:
                off = res['data']['offset']
            c += 1
        except:
            pass
    return dict


def 抽奖(dict):
    s = list(dict.keys())
    中奖序号 = random.randint(0, len(dict) - 1)
    return s[中奖序号]


def 关系(uid, cookie):
    url = 'http://api.bilibili.com/x/space/acc/relation?mid={}'
    headers['cookie'] = cookie
    res = requests.get(url.format(uid), headers=headers)
    res = res.json()
    if res['data']['be_relation']['attribute'] == 2 or res['data']['be_relation']['attribute'] == 6 or \
            res['data']['be_relation']['attribute'] == 1:
        return 1
    else:
        return 2


def 判定抽奖号(uid, cookie):
    抽奖次数 = []
    url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=903059&host_uid={}&offset_dynamic_id={}&need_top=1&platform=web'
    headers['cookie'] = cookie
    off = 0
    c = 0
    while c < 5:
        res = requests.get(url.format(uid, off), headers=headers)
        res = res.json()
        if 'cards' in res['data']:
            for i in res['data']['cards']:
                try:
                    if int(json.loads(i['card'])['item']['timestamp']) >= (
                            time.time() // 86400 * 86400 - 28800 - 86400 * 5):
                        if re.search('抽奖', json.loads(json.loads(i['card'])['origin'])['item']['description']) != None:
                            抽奖次数.append('抽奖')
                except:
                    pass
            off = res['data']['next_offset']
        c += 1
    if len(抽奖次数) >= 10:
        print(uid, '5天内抽奖次数：', len(抽奖次数), '判定为机器人')
        return 1
    else:
        print(uid, '5天内抽奖次数：', len(抽奖次数), '中奖有效')
        return 2


def 判定抽奖有效(uid, config):
    if 关系(uid, config) == 1:
        print(uid,"已关注UP")
        if 判定抽奖号(uid, config) == 2:
            return 1
        else:
            return 2
    else:
        return 2


if __name__ == '__main__':
    抽奖动态号 = 597251976022764517
    抽奖人数 = 1
    dict = dt_list(抽奖动态号, config()[0])
    有效中奖 = []
    while len(有效中奖) < 抽奖人数:
        uuid = 抽奖(dict)
        if 判定抽奖有效(uuid, config()[0]) == 1:
            if uuid not in 有效中奖:
                有效中奖.append(uuid)
    print('最终中奖名单如下：')
    for i in 有效中奖:
        print(i, dict[i])
