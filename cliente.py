import sys
import socket

# Dicionário de tradução de mensagens
message_translation = {
    'PASS-200': 'Tarefa adicionada com sucesso.',
    'PASS-201': 'Tarefa iniciada com sucesso.',
    'PASS-202': 'Tarefa pausada com sucesso.',
    'PASS-203': 'Tarefa finalizada com sucesso.',
    'PASS-213': 'Usuário registrado com sucesso.',
    'PASS-214': 'Login realizado com sucesso.',
    'PASS-215': 'Logout realizado com sucesso.',
    'ERRO-404': 'Tarefa não encontrada.',
    'ERRO-501': 'Nenhuma tarefa encontrada.',
    'ERRO-500': 'Comando desconhecido',
    'ERRO-700': 'Você não está logado.',
    'ERRO-701': 'Comando inválido.',
    'ERRO-702': 'Argumentos inválidos.',
    'ERRO-703': 'Usuário já existe.',
    'ERRO-704': 'Credenciais inválidas.',
    'ERRO-801': 'Tarefa já existe.',
    'ERRO-804': 'Operação inválida.',
    'ERRO-999': 'Comando desconhecido.'
}

# Obtém os argumentos da linha de comando ou usa valores padrão
if len(sys.argv) >= 3:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
# Se o usuário não definir HOST e porta, utiliza os metodos padrões abaixo:
else:
    HOST = '127.0.0.1'  # Valor padrão para o endereço IP
    PORT = 12345  # Valor padrão para a porta

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
    received_message = data.decode().strip()
    # Retorna a tradução da resposta enviada pelo servidor
    translated_message = message_translation.get(received_message, 'Resposta do servidor: ' + received_message)
    print(translated_message)

# Fecha o socket do cliente
client_socket.close()
