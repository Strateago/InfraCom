import socket
import time
import random
import threading

#Variáveis padrão
BUFFERSIZE = 1024
HOST = 'localhost'
PORT = 5000
server = (HOST, PORT)
TIMEOUT = 1

#Numero do dado enviado (RDT 3.0)
sendNum = 0
#Variável global para encerrar as threads
on = True
#Impedir mensagens duplicadas
lastMsg = None
#Cria o socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#"Aloca" o socket
client.bind((HOST, 0))

#Gerador de erros
def errorGenerator():
    num = random.random()
    if num >= 0.25 :
        return 0
    return 1

#Enviar a mensagem para o servidor e esperar o ACK
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
                    break
                elif messageR.decode() == '1ack' and sendNum == 1:
                    break
            #Estouro do temporizador
            except socket.timeout:
                if errorGenerator() == 0:
                    client.sendto(messageE, server)

#Receber mensagens do servidor e enviar o ACK   
def receive(client, lock):
    global on, lastMsg
    client.settimeout(TIMEOUT)
    count = 0
    messageR = None
    while on:
        if count == 2:
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

#Função da thread que envia as mensagens
def input_thread(client, server, lock):
    global on
    while on:
        msg = input()
        send(msg, client, server, lock)
        if msg == 'bye': on = False
    return

#Função da thread que recebe as mensagens
def receive_thread(client, server, lock):
    global on, lastMsg
    while on:
        rcvMsg = receive(client, lock)
        if rcvMsg != lastMsg:
            print(rcvMsg[1:])
            lastMsg = rcvMsg
    return
    
# Main do cliente
#Menu
print("Gerenciamento de Reservas de Salas")
print("connect as <nome> -> Conectar ao servidor como <nome>")
print("list -> Listar os usuários conectados ao servidor")
print("check <sala> <dia> -> Verificar os horários disponíveis da <sala> no <dia>")
print("reservar <sala> <dia> <horário> -> reservar a <sala> no <dia> no <horário>")
print("cancelar <sala> <dia> <horário> -> cancelar reserva da <sala> no <dia> no <horário>")
print("bye -> Desconectar do servidor e sair do programa")
print("OBS:\nSalas: E101 - E105\nDias: Seg, Ter, Qua, Qui, Sex\nHorários: 8 - 17")
#Cria o lock
lock = threading.Lock()
#Thread para enviar mensagens para o servidor
thread1 = threading.Thread(target=input_thread, args=(client, server, lock))
#Thread para receber mensagens do servidor
thread2 = threading.Thread(target=receive_thread, args=(client, server, lock))
#Inicia threads
thread2.start()
thread1.start()
#Espera threads voltarem
thread1.join()
thread2.join()
#Encerra o socket
client.close()
