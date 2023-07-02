import socket
# Configurações do cliente
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345       # Porta de conexão do servidor
# Criação do socket TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Conecta-se ao servidor
client_socket.connect((HOST, PORT))
while True:
    # Solicita ao usuário para digitar um comando
    command = input('Digite um comando: ')
    # Envia o comando para o servidor
    client_socket.sendall(command.encode())
    if command.lower() == 'bye':
        # Se o usuário digitar 'bye', encerra a conexão
        break
    # Recebe a resposta do servidor
    data = client_socket.recv(1024)
    # Processa a resposta recebida
    received_message = data.decode()
    print('Resposta do servidor:', received_message,)
# Fecha o socket do cliente
client_socket.close()