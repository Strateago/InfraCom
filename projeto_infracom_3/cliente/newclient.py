import socket
from socket import timeout
import time
import random
import threading
import sys

BUFFERSIZE = 1024
HOST = 'localhost'
PORT = 5000
server = (HOST, PORT)
TIMEOUT = 1

sendNum = 0
on = True
lastMsg = None

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.bind((HOST, 0))
# mySocket = client.getsockname()[1]

tamanho = 12

def errorGenerator():
    num = random.random()
    if num >= 0.25 :
        return 0
    #print("Erro no envio")
    return 1

def send(message, client, server, lock):
    global sendNum
    client.settimeout(TIMEOUT)
    with lock:
        sendNum = not sendNum
        message = str(int(sendNum)) + message
        messageE = message.encode()
        if errorGenerator() == 0:
            client.sendto(messageE, server)   
        while True:
            try:
                messageR, _ = client.recvfrom(BUFFERSIZE)
                if messageR.decode() == '0ack' and sendNum == 0:
                    #print("Enviada com sucesso")
                    break
                elif messageR.decode() == '1ack' and sendNum == 1:
                    #print("Enviada com sucesso")
                    break
            except socket.timeout:
                #print("Estouro no temporizador")
                if errorGenerator() == 0:
                    client.sendto(messageE, server)
                
def receive(client, lock):
    global on, lastMsg
    client.settimeout(TIMEOUT)
    count = 0
    messageR = None
    while on:
        if count == 1:
            time.sleep(1)
            count = 0
        with lock:
            count += 1
            try:
                messageR, sender = client.recvfrom(BUFFERSIZE)
            except socket.timeout:
                pass
            if messageR is not None:
                messageR = messageR.decode()
                #print("Mensagem recebida:", messageR[1:])
                message = messageR[0] + 'ack'
                client.sendto(message.encode(), sender)
                return messageR
        
def input_thread(client, server, lock):
    global on
    while on:
        msg = input()
        send(msg, client, server, lock)
        if msg == 'bye': on = False
        
def receive_thread(client, server, lock):
    global on, lastMsg
    while on:
        rcvMsg = receive(client, lock)
        if rcvMsg != lastMsg:
            print(rcvMsg[1:])
            lastMsg = rcvMsg
    
# Programa
print("Gerenciamento de Reservas de Salas")
print("connect as <nome> -> Conectar ao servidor como <nome>")
print("list -> Listar os usuários conectados ao servidor")
print("check <sala> <dia> -> Verificar os horários disponíveis da <sala> no <dia>")
print("reservar <sala> <dia> <horário> -> reservar a <sala> no <dia> no <horário>")
print("cancelar <sala> <dia> <horário> -> cancelar reserva da <sala> no <dia> no <horário>")
print("bye -> Desconectar do servidor e sair do programa")
print("OBS:\nSalas: E101 - E105\nDias: Seg, Ter, Qua, Qui, Sex\nHorários: 8 - 17")
lock = threading.Lock()
thread1 = threading.Thread(target=input_thread, args=(client, server, lock))
thread2 = threading.Thread(target=receive_thread, args=(client, server, lock))
thread2.start()
thread1.start()
thread1.join()
thread2.join()
client.close()