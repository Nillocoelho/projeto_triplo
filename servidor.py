import socket
import threading

# Configurações do servidor
HOST = '0.0.0.0'  # Endereço IP do servidor
PORT = 12345       # Porta de escuta do servidor

# Dicionário de tarefas
tasks = {}

# Dicionário de usuários logados
logged_users = {}

# Dicionário de usuários registrados
users = {}

def handle_client(client_socket, client_address):
    while True:
        # Recebe dados do cliente
        data = client_socket.recv(1024)
        if not data:
            # Se os dados estiverem vazios, o cliente encerrou a conexão
            print('CLIENT DISCONNECTED:', client_address)
            break
        # Processa os dados recebidos
        received_message = data.decode().strip()
        print('RECEIVED MESSAGE: ', received_message)
        # Trata a mensagem recebida
        response_message = process_message(received_message, client_address)
        # Envia a resposta ao cliente
        client_socket.sendall(response_message.encode())
    # Encerra a conexão com o cliente
    client_socket.close()

def process_message(message, client_address):
    global tasks, logged_users, users

    message = message.upper()

    # Comando: ADD_TASK
    if message.startswith('SET'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'

        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]

        if task_name in tasks:
            return 'ERRO-801\n'

        tasks[task_name] = '200'
        return 'PASS-200\n'

    # Comando: START_TASK
    if message.startswith('START'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'

        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]

        if task_name not in tasks:
            return f'"{task_name}": ERRO-404\n'

        current_status = tasks[task_name]
        if current_status == '200':
            # Tarefa está no estado "INICIADA"
            return f'"{task_name}": PASS-201\n'
        elif current_status == '201':
            # Tarefa está no estado "PAUSADA"
            tasks[task_name] = '200'
            return f'"{task_name}": PASS-201\n'
        else:
            # Tarefa não está em estado "INICIADA" ou "PAUSADA"
            return 'ERRO-804\n'

    # Comando: PAUSE_TASK
    if message.startswith('PAUSE'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'

        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]

        if task_name not in tasks:
            return f'"{task_name}": ERRO-404\n'

        current_status = tasks[task_name]
        if current_status == '200':
            # Tarefa está no estado "INICIADA"
            tasks[task_name] = '201'
            return f'"{task_name}": PASS-202\n'
        else:
            # Tarefa não está em estado "INICIADA"
            return 'ERRO-804\n'

    # Comando: FINISH_TASK
    if message.startswith('FINISH'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'

        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]

        if task_name not in tasks:
            return f'"{task_name}": ERRO-404\n'

        current_status = tasks[task_name]
        if current_status == '200':
            # Tarefa está no estado "INICIADA"
            tasks[task_name] = '203'
            return f'"{task_name}": PASS-203\n'
        else:
            # Tarefa não está em estado "INICIADA"
            return 'ERRO-804\n'

    # Comando: LIST_TASKS
    if message == 'LIST':
        if client_address not in logged_users:
            return 'ERRO-700\n'

        task_list = ''
        if tasks:
            for task, status in tasks.items():
                task_list += f'{task}: {status}\n'
        else:
            task_list = 'ERRO-501\n'
        return task_list

    # Comando: REGISTER_USER
    if message.startswith('REG'):
        split_message = message.split(' ')
        if len(split_message) < 3:
            return 'ERRO-702\n'

        username = split_message[1]
        password = split_message[2]

        if username in users:
            return 'ERRO-703\n'

        users[username] = password
        return 'PASS-213\n'

    # Comando: LOGIN
    if message.startswith('LOG'):
        split_message = message.split(' ')
        if len(split_message) < 3:
            return 'ERRO-702\n'

        username = split_message[1]
        password = split_message[2]

        if username in users and users[username] == password:
            logged_users[client_address] = username
            return 'PASS-214\n'

        return 'ERRO-704\n'

    # Comando: LOGOUT
    if message == 'OUT':
        if client_address in logged_users:
            del logged_users[client_address]
            return 'PASS-215\n'
        else:
            return 'ERRO-700\n'

    # Comando desconhecido
    return 'ERRO-999\n'

def main():
    # Cria o socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Define a opção de reutilização do endereço
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Vincula o socket à porta e ao endereço definidos
    server_socket.bind((HOST, PORT))

    # Define o limite máximo de conexões pendentes
    server_socket.listen(5)
    print('SERVER STARTED')

    try:
        while True:
            # Aguarda a conexão de um cliente
            client_socket, client_address = server_socket.accept()
            print('CLIENT CONNECTED:', client_address)

            # Cria uma thread para tratar as mensagens do cliente
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    finally:
        # Encerra o socket do servidor
        server_socket.close()

if __name__ == '__main__':
    main()
