import sys
import socket

# Verifica se foram fornecidos argumentos suficientes
if len(sys.argv) < 3:
    print("Uso: python3 cliente.py <endereço IP> <porta>")
    sys.exit(1)

# Obtém os argumentos da linha de comando
HOST = sys.argv[1]
PORT = int(sys.argv[2])

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
    print('Resposta do servidor:\n', received_message)

# Fecha o socket do cliente
client_socket.close()
