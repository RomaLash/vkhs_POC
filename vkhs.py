# -*coding: utf-8 -*-
import base64
import codecs
import datetime
import hashlib
import lzma
import os
import re
import time
import zlib as z
from urllib.request import urlretrieve
import shutil
import requests
import vk
from Crypto.Cipher import AES
from pymongo import MongoClient

"""
Функции сжатия+шифрования/разжатия+дешифрования
"""


def encrypto_tel(message):
    """
    сжимаем и шифруем сообщение.
    :param message: 
    :return: hh: зашифрованное сообщение
    """
    print("message = ", message, "\nlen = ", len(message))
    aa = str.encode(message)  # декодируем русские символы
    b = z.compress(aa, 9)  # сжимаем
    obj = AES.new(b'This is a key123', AES.MODE_CFB, b'This is an Yattt')
    ciphertext = obj.encrypt(b)  # шифруем
    print("\nchip = ", ciphertext, "\nlen = ", len(ciphertext))
    j = codecs.encode(ciphertext, 'hex')  # конвентируем в хекс
    print(j, type(j))

    strr = str(j)[2:-1]  # преобразуем из байтэрр в строку т.к. питон при заполнении списка
    hh = []  # автоматически преобразует байты в их номера
    i = 0  # делаем преобразование, чтобы этого избежать
    while i < len(strr):  # разбиваем в массив по 2 символа
        hh.append(strr[i] + strr[i + 1])
        i += 2
    print("\nhexarray = ", hh)
    return hh


def decrypto_tel(chiper):
    """
    дешифруем и "разжимаем"
    :param chiper: 
    :return: aaa - расшифрованное сообщение
    """
    b = ""  # соединяем в строку
    for h in chiper:
        b = b + h

    n = bytes(b, encoding='utf-8')  # декодируем
    l = codecs.decode(n, 'hex')
    obj2 = AES.new(b'This is a key123', AES.MODE_CFB, b'This is an Yattt')
    a = obj2.decrypt(l)
    v = z.decompress(a)
    aaa = v.decode()
    return aaa


def imagehash(path):
    """
    получаем из массива картинок зашифрованное сообщение
    :param path: путь к скачанным картинкам
    :return: 
    """
    i = 1
    nn = []
    while i < (len(os.listdir(path)) + 1):
        try:
            a = path + "/{}.jpg".format(i)
            with open(a, "rb") as image_file:
                encoded_string = hashlib.sha224(base64.b64encode(image_file.read())).hexdigest()
                image_file.close()
                nn.append(encoded_string[:2])
                i = i + 1
        except:
            i = i + 1
            continue
    return nn


"""
Скачивание фотографий
"""


def auth(login, password, albumurl):
    vk_app_id = '6189318'
    return login, password, vk_app_id, albumurl


def get_id(url):
    user_id, album_id = re.split('_', re.split('album', url)[1])
    return user_id, album_id


def get_photos(user_id, album_id, auth_data, path):
    """
    Скачивание фотографий с альбома
    :param user_id: 
    :param album_id: 
    :param auth_data: 
    :param path: папка, в которую сохраняются картинки
    :return: 
    """
    login, password, vk_app_id = auth_data[0:3]
    session = vk.AuthSession(app_id=vk_app_id, user_login=login, user_password=password)
    vkapi = vk.API(session)
    print("Login success")
    counter = 0
    if not os.path.exists(path):
        os.mkdir(path)
        photo_folder = path + '/album{0}_{1}'.format(user_id, album_id)
    else:
        photo_folder = path + '/album{0}_{1}'.format(user_id, album_id)
    if not os.path.exists(photo_folder):
        os.mkdir(photo_folder)
    photos = vkapi.photos.get(owner_id=user_id, album_id=album_id, count=1000, v=5.68)
    for photo in photos['items']:
        counter += 1
        url = photo['photo_604']
        print(counter)
        try:
            urlretrieve(url, photo_folder + "/" + str(counter) + ".jpg")
        except Exception:
            print('Произошла ошибка, файл пропущен.')
            continue


def encrypt(messagearr, login, password, album):
    """
    Шифрование сообщения и аплод в альбом Вк
    :param messagearr: 
    :param login: 
    :param password: 
    :param album: 
    :return: 
    """
    message = ""
    for m in messagearr:
        message = message + ' ' + m
    client = MongoClient()
    db = client.test_database_im
    coll = db.test_image
    a = encrypto_tel(message)
    finlist = []

    """
    print("start_list:")
    for h in a:
        for c in coll.find({"hash": h}):
            print(c)
            """

    for h in a:
        try:
            b = []
            for c in coll.find({"hash": h}):
                b.append(c)
            while len(b) != 1:
                if b[0]["last_usage"] > b[1]["last_usage"]:
                    b.pop(0)
                else:
                    b.pop(1)
            finlist.append(b[0])
        except:
            print("cant find image for: {}".format(h))
            continue

    # print("fin = \n",finlist)
    n = []
    for f in finlist:
        n.append(f["path"])
    for f in finlist:
        coll.update({"_id": f["_id"]}, {"$set": {"last_usage": datetime.datetime.utcnow()}})

    answer = input("Upload message?")
    if answer == "y":
        session = vk.AuthSession(app_id='6186029', user_login=login, user_password=password, scope='photos')
        vkapi = vk.API(session)
        get_photos = vkapi.photos.getUploadServer(album_id=album)
        data_album_id = get_photos['aid']
        data_upload_url = get_photos['upload_url']
        i = 0
        while i < len(n):
            try:
                a = n[i:(i + 5)]
            except:
                a = n[i:]
            for aa in a:
                files = {'file': open(aa, 'rb')}
                post_request = requests.post(data_upload_url, files=files).json()
                data_server = post_request['server']
                data_photos_list = post_request["photos_list"]
                data_hash = post_request["hash"]
                vkapi.photos.save(album_id=data_album_id, server=data_server, photos_list=data_photos_list,
                                  hash=data_hash)
            if (i % 100) == 0:
                time.sleep(5)
            i += 5
        print("Total uploaded: ", len(n))


def setup_config(login, password, albumid, albumurl):
    """
    создание конфиг файла
    :param login: 
    :param password: 
    :param albumid: 
    :param albumurl: 
    :return: 
    """
    data = login + "," + password + "," + albumid + "," + albumurl
    with lzma.open("conf.xz", 'w') as f:
        f.write(data.encode())


def conf_enc():
    """
    декодирование конфиг файла для отправки
    :return: 
    """
    with lzma.open('conf.xz') as c:
        data = c.read()
        setup = re.split(",", data.decode())
        return setup[0:3]


def conf_dec():
    """
    декодирование конфиг файла для получения
    :return: 
    """
    with lzma.open('conf.xz') as c:
        data = c.read()
        setup = re.split(",", data.decode())
        setup.pop(2)
        return setup


def decrypt(login, password, albumurl):
    """
    скачивание и расшифрование сообщения
    :param login: 
    :param password: 
    :param albumurl: 
    :return: 
    """
    auth_data = auth(login, password, albumurl)
    id_data = get_id(auth_data[3])
    get_photos(id_data[0], id_data[1], auth_data, "saved")
    print("message: ", decrypto_tel(imagehash("saved/" + albumurl)))
    ans = input("очистить папку с фалами?")
    if ans == 'y':
        shutil.rmtree("saved/" + albumurl)
