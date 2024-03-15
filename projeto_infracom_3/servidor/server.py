import socket 
import time
import random
import threading

BUFFERSIZE = 1024
HOST = 'localhost'
PORT = 5000
server = (HOST, PORT)
TIMEOUT = 1

#Classe para armazenar os horários disponíveis e quem reservou a sala
class dia:
    def __init__(self):
        self.owner = [(), (), (), (), (), (), (), (), (), ()]
        self.horarios = [True, True, True, True, True, True, True, True, True, True]

#Classe para atribuir e armazenar os dias da semana como instâncias da classe "dia", representadas pelas iniciais
class week:
    def __init__(self):
        self.day = {
            'Seg': dia(),
            'Ter': dia(),
            'Qua': dia(),
            'Qui': dia(),
            'Sex': dia()
        }
#Numero do dado enviado (RDT 3.0)
sendNum = 0
#Cria um socket
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#"Aloca" o socket
udp.bind(server)
#Tabela onde são guardados os usuários e seus IPs e portas
users = {}
#Tabela das possíveis salas, como instâncias da classe "week" (semana)
salas = {
    "E101": week(),
    "E102": week(),
    "E103": week(),
    "E104": week(),
    "E105": week()
}
#Gerador de erros
def errorGenerator():
    num = random.random()
    if num >= 0.25 :
        return 0
    #erro no envio
    return 1

#Verificar se o dia é válido
def verificaDia(dia):
    comp = week()
    if dia in comp.day:
        return True
    else:
        return False

#Verificar se a hora é válida
def verificaHora(hora):
    if 8 <= hora <= 17:
        return True
    else:
        return False

#Verificar se a sala é válida
def verificaSala(sala):
    if sala in salas:
        return True
    else:
        return False

#Enviar dados
def send(message, orig):
    global sendNum
    udp.settimeout(TIMEOUT)
    sendNum = not sendNum
    message = str(int(sendNum)) + message
    messageE = message.encode()
    if errorGenerator() == 0:
        udp.sendto(messageE, orig)   
    while True:
        try:
            messageR, _ = udp.recvfrom(BUFFERSIZE)
            if messageR.decode() == '0ack' and sendNum == 0:
                break
            elif messageR.decode() == '1ack' and sendNum == 1:
                break
        except socket.timeout:
            #Estouro no temporizador
            if errorGenerator() == 0:
                udp.sendto(messageE, orig)

#Receber dados
def receive():
    udp.settimeout(None)
    messageR, sender = udp.recvfrom(BUFFERSIZE)
    messageR = messageR.decode()
    if messageR[1:] != 'ack':
        message = messageR[0] + 'ack'
        udp.sendto(message.encode(), sender)
    return messageR, sender

#Main do servidor
while True:
    receivedMsg, sender = receive()
    receivedMsg = receivedMsg[1:]
    if 'connect as ' in receivedMsg:
        nameAlreadyUsed = False
        parts = receivedMsg.split(' ')
        for i in users:
            if i == parts[2]: nameAlreadyUsed = True
        if not nameAlreadyUsed:
            users[parts[2]] = sender
            print(users)
            msg = parts[2] + " está avaliando reservas\n"
            for i in users:
                if i != parts[2]: send(msg, users[i])
        else: 
            msg = "Nome já está em uso"
            send(msg, sender)
    elif receivedMsg == 'bye':
        userFound = False
        for i in users:
            if users[i] == sender:
                msg = i + " saiu do sistema de reservas\n"
                users.pop(i)
                userFound = True
                break
        if userFound: 
            for x in users:
                send(msg, users[x])
    elif receivedMsg == 'list':
        userFound = False
        for i in users:
            if users[i] == sender:
                msg = ''
                for i in users:
                    msg = msg + i + ' [' + users[i][0] + ':' + str(users[i][1]) + ']\n'
                send(msg, sender)
                userFound = True
                break
        if not userFound: send('Login não realizado\n', sender)
    else:
        userFound = False
        for i in users:
            if users[i] == sender:
                userFound = True
                break
        if not userFound: send('Login não realizado\n', sender)
        else:
            receivedMsg = receivedMsg.split(' ')
            if receivedMsg[0] == 'check':
                if verificaSala(receivedMsg[1]) and verificaDia(receivedMsg[2]):
                    msg = 'Horários: '
                    for cont, i in enumerate(salas[receivedMsg[1]].day[receivedMsg[2]].horarios, 8):
                        if i:
                            msg += str(cont) + ' '
                    msg += '\n'
                    send(msg, sender)
                else:
                    msg = "Parâmetros Inválidos\n"
                    send(msg, sender)
            
            elif receivedMsg[0] == 'reservar':
                if verificaSala(receivedMsg[1]) and verificaDia(receivedMsg[2]) and verificaHora(int(receivedMsg[3])):
                    if salas[receivedMsg[1]].day[receivedMsg[2]].horarios[int(receivedMsg[3])-8]:
                        salas[receivedMsg[1]].day[receivedMsg[2]].horarios[int(receivedMsg[3])-8] = False
                        msg = " reservou a sala " + receivedMsg[1]
                        for i in users:
                            if users[i] == sender:
                                send("Você [" + users[i][0] + ':' + str(users[i][1]) + ']' + msg + '\n', sender)
                                salas[receivedMsg[1]].day[receivedMsg[2]].owner[int(receivedMsg[3])-8] = (i, sender)
                                msg = i + ' [' + users[i][0] + ':' + str(users[i][1]) + ']' + msg + " na " + receivedMsg[2] + " às " + receivedMsg[3] + " horas\n"
                        for i in users:
                            if users[i] != sender:
                                send(msg, users[i])
                    else:
                        msg = 'Sala já reservada por ' + str(salas[receivedMsg[1]].day[receivedMsg[2]].owner[int(receivedMsg[3])-8][0]) + '\n'
                        send(msg, sender)
                else:
                    msg = "Parâmetros Inválidos\n"
                    send(msg, sender)

            elif receivedMsg[0] == 'cancelar':
                if verificaSala(receivedMsg[1]) and verificaDia(receivedMsg[2]) and verificaHora(int(receivedMsg[3])):
                    var = salas[receivedMsg[1]].day[receivedMsg[2]].owner[int(receivedMsg[3])-8]
                    if var != ():
                        if var[1] == sender:
                            salas[receivedMsg[1]].day[receivedMsg[2]].horarios[int(receivedMsg[3])-8] = True
                            salas[receivedMsg[1]].day[receivedMsg[2]].owner[int(receivedMsg[3])-8] = ()
                            msg = 'Você [' + users[i][0] + ':' + str(users[i][1]) + '] cancelou a reserva da sala ' + receivedMsg[1] + '\n'
                            send(msg, sender)
                            msg = var[0] + ' [' + users[i][0] + ':' + str(users[i][1]) + '] cancelou a reserva da sala ' + receivedMsg[1] + " na " + receivedMsg[2] + " às " + receivedMsg[3] + " horas\n"
                            for i in users:
                                if users[i][1] != sender:
                                    send(msg, users[i])
                        else:
                            msg = 'Essa sala não foi reservada por você\n'
                            send(msg, sender)
                    else:
                        msg = 'Essa sala não foi reservada\n'
                        send(msg, sender)
                else:
                    msg = "Parâmetros Inválidos\n"
                    send(msg, sender)


