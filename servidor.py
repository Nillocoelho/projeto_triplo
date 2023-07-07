import socket
import threading

# Configurações do servidor
HOST = '0.0.0.0'  # Endereço IP do servidor
PORT = 12345  # Porta de escuta do servidor

# Dicionário de tarefas
tasks = {}

# Dicionário de usuários logados
logged_users = {}

# Dicionário de usuários registrados
users = {}

# Dicionário de semáforos para as tarefas
task_semaphores = {}

# Mutex para garantir exclusão mútua no acesso aos dicionários de tarefas, usuários logados e usuários registrados
mutex = threading.Lock()

#Função encarregada de lidar com a comunicação entre cliente e servidor
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
        print('RECEIVED MESSAGE:', received_message)
        # Trata a mensagem recebida
        response_message = process_message(received_message, client_address)
        # Envia a resposta ao cliente
        client_socket.sendall(response_message.encode())
    # Encerra a conexão com o cliente
    client_socket.close()


def process_message(message, client_address):
    global tasks, logged_users, users, task_semaphores, mutex

    message = message.upper()

    # Comando adicionar tarefa
    if message.startswith('SET'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'

        # Verifica o tamanho da mensagem, retornando erro caso a mensagem seja menor que 2
        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]
        # Garante o acesso unico a região crítica, deixando um acesso por vez
        with mutex:
            if task_name in tasks:
                return 'ERRO-801\n'

            # Cria um semáforo para a nova tarefa
            task_semaphore = threading.Semaphore(1)
            task_semaphores[task_name] = task_semaphore
            # Tarefa no statu de aguardo, esperando novas instruções
            tasks[task_name] = '200'
        return 'PASS-200\n'

    # Comando para iniciar uma task
    if message.startswith('START'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'
        # Verifica o tamanho da mensagem, retornando erro caso a mensagem seja menor que 2
        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]
        # Garante o acesso unico a região crítica, deixando um acesso por vez
        with mutex:
            if task_name not in tasks:
                return 'ERRO-404\n'
            # Passa o tarefa para o dicionário do semaforo
            task_semaphore = task_semaphores[task_name]

        # Adquire o semáforo (bloqueia outros usuários)
        task_semaphore.acquire()

        # Analiza o estado atual de uma mensagem
        try:
            current_status = tasks[task_name]
            if current_status == '200':  # Aguardando
                tasks[task_name] = '201'  # Iniciada
                return 'PASS-201\n'
            elif current_status == '202':  # Pausada
                tasks[task_name] = '201'  # Iniciada
                return 'PASS-201\n'
            else:
                # Tarefa esta num parametro que não pode prosseguir para atribuição desejada
                return 'ERRO-804\n'
        finally:
            # Libera o semáforo (permite que outros usuários acessem)
            task_semaphore.release()

    # Comando para pausar uma tarefa
    if message.startswith('PAUSE'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'
        # Verifica o tamanho da mensagem, retornando erro caso a mensagem seja menor que 2
        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]
        # Garante o acesso unico a região crítica, deixando um acesso por vez
        with mutex:
            if task_name not in tasks:
                return 'ERRO-404\n'

            task_semaphore = task_semaphores[task_name]

        # Adquire o semáforo (bloqueia outros usuários)
        task_semaphore.acquire()

        # Analiza o estado atual de uma mensagem
        try:
            current_status = tasks[task_name]
            if current_status == '200':  # Aguardando
                return 'ERRO-804\n'
            elif current_status == '201':  # Iniciada
                tasks[task_name] = '202'  # Pausada
                return 'PASS-202\n'
            else:
                return 'ERRO-804\n'
        finally:
            # Libera o semáforo (permite que outros usuários acessem)
            task_semaphore.release()

    # Comando para finalizar uma tarefa
    if message.startswith('FINISH'):
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'
        # Verifica o tamanho da mensagem, retornando erro caso a mensagem seja menor que 2
        split_message = message.split(' ')
        if len(split_message) < 2:
            return 'ERRO-701\n'

        task_name = split_message[1]
        # Garante o acesso unico a região crítica, deixando um acesso por vez
        with mutex:
            if task_name not in tasks:
                return 'ERRO-404\n'

            task_semaphore = task_semaphores[task_name]

        # Adquire o semáforo (bloqueia outros usuários)
        task_semaphore.acquire()

        # Analiza o estado atual de uma mensagem
        try:
            current_status = tasks[task_name]
            if current_status != '201':  # Se estiver em aguardo ou após pausada, não pode finalizar
                return 'ERRO-804\n'
            #Se iniciada, pode finalizar
            else:
                tasks[task_name] = '203'  # Finalizada
                return 'PASS-203\n'
        finally:
            # Libera o semáforo (permite que outros usuários acessem)
            task_semaphore.release()

    # Comando para listar tarefas
    if message == 'LIST':
        # Verifica se o cliente está logado
        if client_address not in logged_users:
            return 'ERRO-700\n'
        # Garante o acesso unico a região crítica, deixando um acesso por vez
        with mutex:
            task_list = ''
            if tasks:
                for task, status in tasks.items():
                    task_list += f'{task}: {status}\n'
            # Se a lista estiver vazia, retorne erro:
            else:
                task_list = 'ERRO-501\n'
        # Retorna a lista de tarefas
        return task_list

    # Comando que registra o usuário
    if message.startswith('REG'):
        split_message = message.split(' ')
        if len(split_message) < 3:
            return 'ERRO-702\n'
        # Define que Username é o segundo parametro passado e o password é o terceiro
        username = split_message[1]
        password = split_message[2]

        # Garante o acesso unico a região crítica, deixando um acesso por vez
        with mutex:
            if username in users:
                return 'ERRO-703\n'
            # Passa o correspondente de usuário e sua senha
            users[username] = password
        return 'PASS-213\n'

    # Comando que loga o usuário
    if message.startswith('LOG'):
        split_message = message.split(' ')
        if len(split_message) < 3:
            return 'ERRO-702\n'
        # Define que Username é o segundo parametro passado e o password é o terceiro
        username = split_message[1]
        password = split_message[2]
        # Garante o acesso unico a região crítica, deixando um acesso por vez
        with mutex:
            if username in users and users[username] == password:
                logged_users[client_address] = username
                return 'PASS-214\n'

        return 'ERRO-704\n'

    # Comando que desloga o usuário
    if message == 'OUT':
        if client_address in logged_users:
            del logged_users[client_address]
            return 'PASS-215\n'
        # Caso o usuário já esteja deslogado
        else:
            return 'ERRO-700\n'

    # Comando desconhecido
    return 'ERRO-500\n'


def main():
    # Cria o socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Associa o socket a um endereço e porta
    server_socket.bind((HOST, PORT))

    # Inicia o modo de escuta do servidor
    server_socket.listen(5)

    print('SERVER STARTED')

    try:
        while True:
            # Aguarda uma conexão
            client_socket, client_address = server_socket.accept()
            print('CLIENT CONNECTED: ', client_address)

            # Inicia uma nova thread para lidar com o cliente
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    finally:
        # Encerra o socket do servidor
        server_socket.close()

# Verifica se o script está sendo executado de maneira adequada
if __name__ == '__main__':
    main()
