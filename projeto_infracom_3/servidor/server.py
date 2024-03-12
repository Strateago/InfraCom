import socket 
import time
import random

HOST = 'localhost'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
PORT2 = 5001

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT2)
orig = (HOST, PORT)
bufferSize = 1024

send_base = 0
rcv_base = 0
nextSeqNum = 0
tamanho = 12

udp.bind(orig)

def errorGenerator():
    num = random.random()
    if num >= 0.25 :
        return 0
    print("Erro no envio")
    return 1

def sendFile(fileName):
    udp.settimeout(2)
    global rcv_base, nextSeqNum, send_base
    fileEncoded = fileName.encode()
    udp.sendto ((str(nextSeqNum).zfill(tamanho) + str(rcv_base).zfill(tamanho) + str(len(fileEncoded)).zfill(tamanho)).encode() + fileEncoded, dest)
    nextSeqNum = nextSeqNum + len(fileEncoded)

    msg, cliente = udp.recvfrom(bufferSize + tamanho*3)
    msg = msg.decode()
    if int(msg[:tamanho]) == rcv_base:
        send_base = int(msg[tamanho:2*tamanho])
    
    with open(fileName, 'rb') as file:
        fileBytes = file.read()
    
    i = 0
    while i < len(fileBytes):
        error = errorGenerator()
        if error == 0:
            udp.sendto((str(nextSeqNum).zfill(tamanho) + str(rcv_base).zfill(tamanho) + str(len(fileBytes[i:i + bufferSize])).zfill(tamanho)).encode() + fileBytes[i:i + bufferSize], dest)
            # Numero de Sequencia / Ack / tamanho do dado / dados
            nextSeqNum = nextSeqNum + len(fileBytes[i:i + bufferSize])
            print("Pacote Enviado")
        tempo1 = time.time()
        try:
            msg, cliente = udp.recvfrom(bufferSize + tamanho*3)
            msg = msg.decode()
            if int(msg[:tamanho]) == rcv_base:
                send_base = int(msg[tamanho:2*tamanho])
                i = i + bufferSize
            tempo2 = time.time()
            print("Pacote enviado com sucesso, levou ", tempo2 - tempo1, "segundos.")
        except:
            tempo2 = time.time()
            print("Estourou temporizador: ", tempo2 - tempo1, " segundos. Reenviar pacote")

    msgFim = "thiago grangeiro".encode()
    udp.sendto((str(nextSeqNum).zfill(tamanho) + str(rcv_base).zfill(tamanho) + str(len(msgFim)).zfill(tamanho)).encode() + msgFim, dest)
    nextSeqNum = nextSeqNum + len(msgFim)
   
    msg, cliente = udp.recvfrom(bufferSize + tamanho*3)
    msg = msg.decode()
    if int(msg[:tamanho]) == rcv_base:
        send_base = int(msg[tamanho:2*tamanho])
    print(f"File '{fileName}' sent successfully to the client!")

while True:
    udp.settimeout(None)
    msg, cliente = udp.recvfrom(bufferSize+tamanho*3)
    cabeçalho = msg[:tamanho*3].decode()
    msg = msg[(tamanho*3):]
    rcv_base = int(cabeçalho[:tamanho]) + len(msg)
    fileNameReceive = msg.decode()

    msg = (str(nextSeqNum).zfill(tamanho) + str(rcv_base).zfill(tamanho) + str(0).zfill(tamanho)).encode()
    udp.sendto(msg, dest)
    print("Ack enviado")

    qtdBytes = b''
    i = 0

    while True:
        tempo1 = time.time()
        msg, cliente = udp.recvfrom(bufferSize+tamanho*3)
        tempo2 = time.time()
        print("Recebido em ", tempo2 - tempo1, " segundos")
        cabeçalho = msg[:tamanho*3].decode()
        if int(cabeçalho[:tamanho]) == rcv_base:
            send_base = int(cabeçalho[tamanho:2*tamanho])
            rcv_base = rcv_base + int(cabeçalho[2*tamanho:3*tamanho])
        msg = msg[(tamanho*3):]
        if not msg:
            break
        if msg == "thiago grangeiro".encode():
            msg = (str(nextSeqNum).zfill(tamanho) + str(rcv_base).zfill(tamanho) + str(0).zfill(tamanho)).encode()
            udp.sendto(msg, dest)
            print("File totally received! Ack sent")
            break
        qtdBytes += msg
        i += len(msg)
        with open(fileNameReceive, 'wb') as newFile:
            newFile.write(qtdBytes)
        print("File", i, "received successfully!")
        
        msg = (str(nextSeqNum).zfill(tamanho) + str(rcv_base).zfill(tamanho) + str(0).zfill(tamanho)).encode()
        udp.sendto(msg, dest)
        print("Ack enviado")
    
    sendFile(fileNameReceive)
    
udp.close()