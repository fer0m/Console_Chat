import socket

SERVER_ADDRESS = ('localhost', 8125)
CLIENTS = {}
NICKS = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)


class Session:
    def __init__(self, ip_address, ser_socket):
        self.server_socket = ser_socket
        self.state = 'init'
        self.address = ip_address

    def on_message(self, message_from_member):
        if self.state == 'init':
            message_for_member = 'Необходимо пройти регистрацию, введите свой ник: '
            self.state = 'waitname'
            return message_for_member

        elif self.state == 'waitname':
            if message_from_member in NICKS:
                message_from_member = 'К сожалению, данный ник занят, нажмите ENTER и повторите ввод'
                self.state = 'init'
                return message_from_member
            else:
                message_for_member = f'Ваш ник {message_from_member}? Введите "Да" или "Нет",в случае ошибки.'
                self.nick = message_from_member
                self.state = 'append_name'
                return message_for_member

        elif self.state == 'append_name':
            if message_from_member == "Да":
                self.state = 'register_st_1'
                text = 'Отлично, принято. Введи пароль для своего ника:'
                return text
            elif message_from_member == "Нет":
                self.state = 'init'
                text = 'Вызов повторного меню. Press Enter'
                return text
            else:
                self.state = 'waitname'
                text = 'Повторите ввод. Press Enter'
                return text

        elif self.state == 'register_st_1':
            print(self.state, message_from_member)
            answer_for_member = 'Введите пароль для своего ника повторно:'
            NICKS[self.nick] = message_from_member
            self.password = message_from_member
            self.state = 'register_st_2'
            return answer_for_member

        elif self.state == 'register_st_2':
            if message_from_member == self.password:
                self.state = 'hello'
                return f"Добро пожаловать в чат, {self.nick}! Напиши 'Привет', для начала общения!"
            else:
                text_error = 'Пароль не совпал, введите пароль снова:'
                self.state = 'register_st_1'
                return text_error

        elif self.state == 'hello':
            if message_from_member == "Привет":
                self.state = 'chat'
            else:
                text = f"{self.nick}! Напиши 'Привет', для начала общения!"
                return text

        elif self.state == 'chat':
            return message_from_member


while True:
    data, address = server_socket.recvfrom(1024)
    session = CLIENTS.get(address, None)
    if not session:
        session = Session(address, server_socket)
        CLIENTS[address] = session

    if session.state != 'chat':
        answer = session.on_message(data.decode('utf-8'))
        try:
            session.server_socket.sendto(answer.encode('utf-8'), address)
        except AttributeError:
            pass

    if session.state == 'chat':
        print(CLIENTS, NICKS)
        for other_session in CLIENTS.values():
            if other_session.state == 'chat' and other_session.address != session.address:
                try:
                    print(other_session.address, session.address)
                    answer_nick = session.nick
                    answer_data = data.decode('utf-8')
                    message = f"{answer_nick}: {answer_data}"
                    session.server_socket.sendto(message.encode('utf-8'), other_session.address)
                except AttributeError:
                    pass
