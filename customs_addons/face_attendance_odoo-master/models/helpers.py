# -*- coding: utf-8 -*-

from websocket import create_connection

import re
import requests
import json

BASE = 'localhost:3000/socket.io/?EIO=3'


def socket_emit(event, data):
    resp = requests.get('http://{}&transport=polling'.format(BASE))

    json_data = json.loads(
        resp.content[resp.content.find('{'):resp.content.find('}') + 1])
    sid = json_data['sid']

    ws = create_connection(
        'ws://{}&transport=websocket&sid={}'.format(BASE, sid))

    ws.send("5")
    ws.send('42["{}", {}]'.format(event, json.dumps(data)))


def deaccent(text):
    INTAB = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸĐ"
    INTAB = [ch.encode('utf8') for ch in unicode(INTAB, 'utf8')]

    OUTTAB = "a" * 17 + "o" * 17 + "e" * 11 + "u" * 11 + "i" * 5 + "y" * 5 + "d" + \
             "A" * 17 + "O" * 17 + "E" * 11 + "U" * 11 + "I" * 5 + "Y" * 5 + "D"

    r = re.compile("|".join(INTAB))
    replaces_dict = dict(zip(INTAB, OUTTAB))

    return r.sub(lambda m: replaces_dict[m.group(0)], text)
