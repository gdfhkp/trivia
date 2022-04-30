import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Parameters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """
    masg = chatlib.build_message(code, msg)
    conn.send(masg.encode())
    return

# Implement Code


def recv_message_and_parse(conn):
    """
    Receives a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Parameters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occurred, will return None, None
    """
    data = conn.recv().decode()
    print(data)
    cmd, msg = chatlib.parse_message(data)
    print(cmd + "\n" + msg)
    return cmd, msg


def connect():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("Listening for connections on port %d" % SERVER_PORT)
    return client_socket


def error_and_exit(msg):
    print(msg)
    exit()


def login(conn):
    x = 1
    while x != 0:
        username = input("Please enter username: \n")
        password = input("please enter your password: \n")
        data = username + "#" + password
        msg = chatlib.build_message('LOGIN', data)
        conn.send(msg.encode())
        if chatlib.parse_message(conn.recv(4096).decode())[0] == 'LOGIN_OK':
            x = 0
            print('logged in')
        else:
            print('didnt login')
    return


def build_send_recv_parse(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    msg_code, msg = chatlib.parse_message(conn.recv(4096).decode())
    return msg, msg_code


def get_score(conn):
    score, msg_code = build_send_recv_parse(conn, 'MY_SCORE', '')
    if msg_code == 'YOUR_SCORE':
        print(score)
    else:
        print('error')


def play_question(conn):
    question, msg_code = build_send_recv_parse(conn, 'GET_QUESTION', '')
    if msg_code == 'YOUR_QUESTION':
        answer = input(question + "\n enter your answer:")
        question_id = question.split('#')[0]
        correct, second_msg_code = build_send_recv_parse(conn, 'SEND_ANSWER', question_id + '#' + answer)
        if second_msg_code == 'CORRECT_ANSWER':
            print('you were right the correct answer is:' + answer)
        elif second_msg_code == 'WRONG_ANSWER':
            print('you were wrong the correct answer is:' + correct)
        else:
            print("error")
            return
    elif msg_code == 'NO_QUESTIONS':
        print('no more questions are left')
    else:
        print('error')
        return


def get_high_score(conn):
    scores, msg_code = build_send_recv_parse(conn, 'HIGHSCORE', '')
    if msg_code == 'ALL_SCORE':
        print(scores)
    else:
        print('error')


def get_logged_users(conn):
    logged, msg_code = build_send_recv_parse(conn, 'LOGGED', '')
    if msg_code == 'LOGGED_ANSWER':
        print(logged)
    else:
        print('error')


def logout(conn):
    build_and_send_message(conn, 'LOGOUT', '')


def main():
    skt = connect()
    command = 'c'
    while command != 'logout' and command != '' and command != 'exit':
        command = input('choose a command - score/exit/login/logout/question/logged/highscores:')
        if command == 'score':
            get_score(skt)
        if command == 'exit':
            skt.close()
        if command == 'login':
            login(skt)
        if command == 'question':
            play_question(skt)
        if command == 'logged':
            get_logged_users(skt)
        if command == 'highscores':
            get_high_score(skt)
        if command == 'logout':
            logout(skt)


if __name__ == '__main__':
    main()
