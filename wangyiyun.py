# coding : UTF-8

import requests,json,random,os
import base64
import codecs
from Crypto.Cipher import AES
#import xlwt
#from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA

 #在网易云获取四个参数

second_param = '010001'
third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
fourth_param = '0CoJUm6Qyw8W8jud'

def create_random_16():
    '''随机获取十六个字母拼接成字符串'''
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), str(os.urandom(16)))))[0:16]

random16 = create_random_16()

def aesEncrypt(text,secKey):
        #偏移量        iv = '0102030405060708'
        #文本
    pad = 16 - len(text) % 16
    if isinstance(text, bytes):
            # print("type(text)=='bytes'")
        text = text.decode('utf-8')
    text = text + str(pad * chr(pad))
    encryptor = AES.new(secKey,2,'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext

def get_params(text,page):
    '''获取第一个参数'''
    if page ==1:
        first_param = '{rid:"R_SO_4_25723157",offset :"0",total:"true",limit:"20",csrf_token:""}'
    else:
        first_param = ('{rid:"R_SO_4_25723157",offset :"%s",total:"false",limit:"20",csrf_token:""}'%str((page-1)*20))
    text = random16
    params = aesEncrypt(aesEncrypt(first_param,fourth_param).decode('utf-8'),text)
    return params

def rsaEncrypt(pubKey,text,modulus):
    '''进行rsa加密'''
    text = text[::-1]
    rs = int(codecs.encode(text.encode('UTF-8'),'hex_codec'),16)** int(pubKey,16)% int(modulus,16)
    return format(rs,'x').zfill(256)

def get_encSEcKey():
    '''获取第二个参数'''
    text = random16
    pubKey = second_param
    modulus = third_param
    encSecKey =rsaEncrypt(pubKey,text,modulus)
    return encSecKey

root_pattern = ''
url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_25723157?csrf_token='
header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
cookie = {'cookie': '_iuqxldmzr_=32; _ntes_nnid=fbc876e15279a5dbd36b2077152b6120,1527603035245; _ntes_nuid=fbc876e15279a5dbd36b2077152b6120; WM_TID=cwhT9qljXz7%2FTCr%2BEF1By7PSeb66GED0; __utmz=94650624.1527690632.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __f_=1527692624260; __utmc=94650624; __utma=94650624.292646942.1527603036.1527756782.1527780452.5; JSESSIONID-WYYY=IiTZTTd6rD1pPFOZfVH82g46qk28%2BtlrRSBV%5CD%2BevB97AJ%2FVlvcf8ZHAxuWTR70Bp1pYYap6nNPJPOI39T7obwmTSfnBlqG5yWpI7Hkax%5CKuBKhmEFZaT6TvUwoPd4SWQIlx1uTEEmiK%2B3Ozd3lnZqjrmUuJZDVjMM6ocQe935kmUoDA%3A1527782813892; __utmb=94650624.5.10.1527780452'}

def get_jsons( url,page):
    #获取两个参数
    text = random16
    params = get_params(text,page)
    encSecKey = get_encSEcKey()
    #params = '5FgqSPEOFPoLpHeVBoOX5zbda2cgU0ZzjhYnQ847VNn+5IPf1T6HViQxOyJx78Oys3/1NI2BijEgCFtdRVfxtt+ECC2+VW3n676XKojvdpI3Ak63W1ZKKKfFO908BKiTVjgWhCxVfLov0YvNvObTwkAnmIUbSruj9J0RkAynDR1/fAbhckubCL5pSw5R7YRB'
    #print(params)
    #print(encSecKey)
    #encSecKey = '7d8a64f2907c9496577a89f8c13b0f472ec35928412ecc8b7111845ec433837b2ea8f6c662ef724e535d5c841662215f37c85fe712358985043cc5f8aac79a8f60c063adabda3654901f9bb813d2563ac1515b3cf6c900081776a48f7ccff0a103ec5d2e62e339e437627fdd69adaa00aa3f142b2dcba7f4684941d6657262a4'
    fromdata = {'params':params,'encSecKey':encSecKey}
    jsons = requests.post(url=url,data=fromdata,headers=header,cookies=cookie)
    return jsons.text

def json2list(jsons):
    users = json.loads(jsons)
    comments = []
    #print(jsons.status_code)
    #print(jsons.raise_for_status())
    #print('-------')
    for user in users['comments']:
        #print(num,end=' ')
        #print(user['user']['nickname']+' : '+user['content']+' |点赞数： '+str(user['likedCount']))
        name = user['user']['nickname']
        content = user['content']
        likedCount = user['likedCount']
        user_dict = {'name':name,'content':content,'likedCount':likedCount}
        comments.append(user_dict)
    return comments


import pymysql


def get_conn():
    conn = pymysql.connect(host='localhost',user='root',password='qiangzai',db='jssdb',charset='utf8mb4')
    return conn




def add_data(comment):
    sql = 'insert into wangyiyun1(user,content,likedCount) values(%s,%s,%s)'
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(sql,[comment['name'],comment['content'],comment['likedCount']])
    conn.commit()




def write2sql(comments,page):
    print('正在写入第'+str(page)+'页数据')
    for comment in comments:
        add_data(comment)

def run():
    page = 1
    while True:
        print('第' + str(page) + '页正在获取')
        jsons = get_jsons(url,page)
        comments = json2list(jsons)
        write2sql(comments,page)
        print('第'+str(page)+'页获取完成')
        if len(comments)<20:
            print('评论获取完成')
            break
        page += 1

if __name__='__main__':
    run()

