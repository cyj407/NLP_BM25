#!/usr/bin/python
#-*- encoding: UTF-8 -*-

from collections import OrderedDict
from multiprocessing import Pool
import math
import json
import sys
import socket
import time

target_host = "140.116.245.151"
target_port = 2001

def bm25():
    QA = {}
    q_seg_sorted = []   # every element is sorted -- dictionary
    D = []      # every document length
    with open('./CTBC.json','r',encoding='utf-8') as data:
        QA = json.load(data) 
    for q in QA:
        tmp = seg(q['question'])
        q_subset = {}
        for segment in tmp:
            q_subset[segment] = tmp.count(segment)
        q_seg_sorted.append(q_subset)
        D.append(len(tmp))

    N = len(D)
    avgdl = sum(map(int,D))/N       # all document length = sum(map(int,D))
    k1 = 2
    b = 0.75

    term_num = {}
    for qi in word_list:
        term_num[qi] = word_list.count(qi)

    nq = []
    fq = []
    for sub_list in q_seg_sorted:
        nqi = {}
        fqi = {}
        for qi in word_list:
            nqi[qi] = 0
            fqi[qi] = 0
            if qi in sub_list:
                nqi[qi] += 1
                fqi[qi] = sub_list[qi]
        nq.append(nqi)
        fq.append(fqi)

    score = []
    for doc,NQ,FQ in zip(D,nq,fq): 
        q_score = 0
        K = k1*((1-b) + b*(doc/avgdl))
        for qi in word_list:
            idf = math.log10((N-NQ[qi]+0.5)/(NQ[qi]+0.5))
            tf = FQ[qi]/doc
            q_score = q_score + idf*(tf*(k1+1)/(tf+k1*K))
        score.append(q_score)
    ans = score.index(max(score))
    return (QA[ans]['answer'])

def seg(sentence):
    # create socket
    # AF_INET 代表使用標準 IPv4 位址或主機名稱
    # SOCK_STREAM 代表這會是一個 TCP client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client 建立連線
    client.connect((target_host, target_port))
    # 傳送資料給 target
    data = "seg@@" + sentence
    client.send(data.encode("utf-8"))
    
    # 回收結果信息
    data = bytes()
    while True:
        request = client.recv(8)
        if request:
            data += request
            begin = time.time()
        else:
            break

    word_list = []
    response = data

    if(response is not None or response != ''):
        response = response.decode('utf-8').split()
        for resp in response:
            resp = resp.strip()
            resp = resp[0:len(resp)-1]
            temp = resp.split('(')
            word = temp[0]
            pos = temp[1]

            if len(pos) < 5 and pos != 'FW':    # delete the stopword mark
                word_list.append(word)
    return word_list

sentence = input("請輸入問題：")
word_list = seg(sentence)
print("回答：",bm25(),"\n")