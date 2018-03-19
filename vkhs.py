# -*coding: utf-8 -*-

"""
Консольная оболочка. В строковых параметрах задаются желаемые настройки.
"""
from core import *
import argparse
import getpass

parser = argparse.ArgumentParser(description='Parse args')
parser.add_argument('-set', '--setup', action='store_true', help='инициализация конфиг файла')
parser.add_argument('-sto', '--store', action='store_true', help='использование конфиг файла')
parser.add_argument('-e', '--encrypt', action='store_true', help='шифрование и отправка')
parser.add_argument('-d', '--decrypt', action='store_true', help='получение и дешифрование')
parser.add_argument('-l', '--login', nargs='?', help='логин')
parser.add_argument('-aid', '--albumid', nargs='?', help='album id - нужно только при отправке')
parser.add_argument('-aurl', '--albumurl', nargs='?', help='albumurl - нужно при получении и при создании конфиг файла)')
parser.add_argument('-m', '--message', nargs='*', help='передаваемое сообщение (желательно - не больше 100 знаков)')

args = parser.parse_args()

if args.encrypt and args.decrypt:
    parser.error('отправка и получение сообщение не выполняются вместе')

if not args.encrypt and not args.decrypt:
    parser.error('не выбрано действие')

if args.encrypt and args.store:
    sett = conf_enc()
    print(*sett)
    encrypt(args.message, *sett)

if args.decrypt and args.store:
    sett = conf_dec()
    decrypt(*sett)

if not args.store:
    password = getpass.getpass('Password:')

if args.encrypt and not args.store:
    encrypt(args.message, args.login, password, args.albumid)

if args.decrypt and not args.store:
    decrypt(args.login, password, args.albumurl)

if args.setup:
    setup_config(args.login, password, args.albumid, args.albumurl)
