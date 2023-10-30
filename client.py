#!/usr/bin/env python3

from helperC import *

'''
usage: ./client.py <ip address> <port> <UDP Port>

example usage:
    ./client.py 127.0.0.1 12000 5432
    python3 client.py 127.0.0.1 12000 5432

Run an client instance.
Implementation details can be found in
helperC.py.
'''


def main():
    prompt = 'Enter one of the following commands ' + \
             '(msgto, activeuser, creategroup, joingroup, groupmsg, logout, p2pvideo): '

    connection = getConnection()
    host, port, udp = connection.host, int(connection.port), connection.udpPort
    client = ClientInstance(host, port, udp)
    client.connect()

    lock = threading.Lock()
    connected = True
    authenticated = False
    loggedInUser = None

    while connected:

        if not authenticated:
            loggedInUser, password = getLogin(loggedInUser)
            client.tcpSend(f'{loggedInUser} {password} {udp}')

            '''Case where we exit before we login'''

            if loggedInUser == 'OUT' and password == 'OUT':
                break

            recvMsg = client.tcpRecv()
            print(recvMsg, end='')

            connected, authenticated = checkLoginStatus(recvMsg)
            if authenticated:
                '''Successful authentication'''

                udpConn = client.udpServer(loggedInUser, udp, lock)
                client.login(loggedInUser)

        else:
            try:
                input_message = input(prompt)
                command = re.split(r'\s', input_message)[0]
                # print('command client input is {}'.format(command))
                # if not command or command not in prompt:
                #     print('Error.Invalid command!')
                #     continue

                # if command == 'EDG':
                #     success, error = \
                #         client.EDG(input_message, loggedInUser)
                #     if not success:
                #         print(error, end='')
                #     continue
                #
                # if command == 'UED':
                #
                #     '''
                #     Upload data files. No query is sent
                #     to the server if an error occurs.
                #     '''
                #
                #     success, message = \
                #         client.UED(input_message, loggedInUser)
                #     if not success:
                #         print(message)
                #         continue
                # else:

                if command == 'msgto':
                    sender = loggedInUser
                    receiver = re.split(r'\s', input_message)[1]
                    msg = re.split(r'\s', input_message)[2]
                    client.tcpSend(f'{command} {sender} {receiver} {msg}')
                    continue

                if command == 'logout':
                    '''Disconnect from server.'''
                    client.tcpSend(input_message)
                    connected = False

                recvMsg = client.tcpRecv()
                print('logout receive msg from server {}'.format(recvMsg))

                # if command == 'UVF':
                #
                #     '''Upload file to another client'''
                #
                #     success, error = \
                #         client.UVF(input_message, recvMsg, udpConn)
                #     if not success:
                #         print(error, end='')
                #     continue

                if 'DISCONNECTED' in recvMsg:
                    '''
                    Confirmation from server
                    of OUT request.
                    '''
                    connected = False

                print(recvMsg, end='')

            except (EOFError, KeyboardInterrupt, TypeError):
                client.tcpSend('OUT')
                recvMsg = client.tcpRecv()
                print('\n' + recvMsg, end='')
                break

    client.disconnect()


if __name__ == '__main__':
    main()

# import json
# import os
# import sys
# import threading
# import time
# from socket import *
#
#
# class Client:
#     def __init__(self, serverPort=12000):
#         print("Client is running...")
#         serverName = 'localhost'
#         self.sock = socket(AF_INET, SOCK_STREAM)
#         self.sock.connect((serverName, serverPort))
#
#         t = threading.Thread(target=self.listen)
#         t.start()
#
#         login = False
#         while not login:
#             user_name = input('Enter username: ')
#             psw = input('Enter password: ')
#
#             self.sock.send(json.dumps({'user_name': user_name, 'password': psw}).encode())
#             buffer = self.sock.recv(1024)
#             print("buffer is {}".format(buffer))
#
#             try:
#                 status = json.loads(buffer.decode()).get('status')
#             except json.JSONDecodeError as e:
#                 print("JSON decoding error:", e)
#                 status = False
#
#             if not status:
#                 continue
#             else:
#                 login = True
#
#         client_status = True
#         while client_status:
#             client_status = CMDHandler(self.sock).status
#             time.sleep(0.5)
#
#         self.sock.close()
#         sys.exit(0)
#
#     def listen(self):
#         '''
#         监听所有的消息
#         :return: None
#         '''
#         # 监听所有收到的消息, 并打印出来
#         while True:
#             try:
#                 msg = self.sock.recv(1024)
#                 if msg:
#                     print(msg.decode())
#
#                 if 'download' in msg.decode() and 'filecontent' in msg.decode():
#                     # 保存文件
#                     filename = json.loads(msg.decode()).get('data').get('filename')
#                     filecontent = json.loads(msg.decode()).get('data').get('filecontent')
#                     CMDHandler.save_file(filename, filecontent)
#                     print(msg.decode())
#                     print(f'file {filename} saved!')
#             except Exception as e:
#                 print(f'An Error {e} occur with msg: ', msg.decode())
#                 sys.exit(0)
#
#
# class CMDHandler:
#     # 用来处理你的命令
#     def __init__(self, sock):
#         self.status = True
#         cmd = input("What do you want to send:")
#         # sock.send(cmd.encode())
#         print('send', cmd, 'to server!')
#
#         # 当你输入的命令是logout, 则登出
#         if cmd == 'logout':
#             print("Actively close.")
#             self.status = False
#
#         elif 'sendfile' in cmd:
#             # 当用户输入指令 sendfile filename的时候, 发送文件
#             filename = cmd.split(' ')[1]
#             if filename not in os.listdir():
#                 print(f'Filename {filename} not exist!')
#             else:
#                 msg = json.dumps({'type': 'sendfile', 'data': self.read_files(filename)})
#                 sock.send(msg.encode())
#
#         elif 'download' in cmd:
#             filename = cmd.split(' ')[1]
#             msg = json.dumps({'type': 'download', 'data': {'filename': filename}})
#             sock.send(msg.encode())
#
#
#
#         # 当你输入的命令是登录...
#         # elif cmd == 'login':
#         #     do_something()
#         # 当你输入的命令是xxx.....
#         else:
#             msg = cmd
#             sock.send(msg.encode())
#
#     def read_files(self, filename: str) -> dict:
#         with open(filename, 'r') as file:
#             data = file.read()
#         return {'filename': filename, 'filecontent': data}
#
#     @staticmethod
#     def save_file(filename, fs):
#         if not os.path.exists('recv_client'):
#             os.mkdir('recv_client')
#         with open('recv_client\\' + filename, 'w+') as file:
#             file.write(fs)
#
#
# def example(attr1: int, attr2: str) -> dict:
#     '''
#     描述你的函数逻辑
#         1. 第一步干嘛
#         2. 第二步干嘛
#         3. 第三步干嘛
#     :param attr1: 描述这个参数的类型/意义
#     :param attr2: 描述这个参数的类型/意义
#     :return: 返回的东西是怎么样的
#     '''
#     return dict({attr1: attr2})
#
#
# if __name__ == '__main__':
#     c = Client()
#
#     # import doctest
#     # doctest.testmod()
