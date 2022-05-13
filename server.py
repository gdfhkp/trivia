##############################################################################
# server.py
##############################################################################

import socket
import chatlib
import random
import select

# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
messages_to_send = []

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, msg):
    global messages_to_send
    masg = chatlib.build_message(code, msg)
    messages_to_send.append((conn, masg))
    print("[SERVER] ", masg)  # Debug print
    return


def recv_message_and_parse(conn):
    try:
        data = conn.recv(4096).decode()
        if data == '':
            return '', ''
        cmd, msg = chatlib.parse_message(data)
        print("[CLIENT] ", chatlib.build_message(cmd, msg))  # Debug print
        return cmd, msg
    except:
        return '', ''


def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Receives: -
    Returns: questions dictionary
    """
    questions = {
        2313: {"question": "How much is  2+2?", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
               "correct": 3}
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Receives: -
    Returns: user dictionary
    """
    # users = {
    #     "test"	:	{"password": "test", "score": 0, "questions_asked": []},
    #     "yossi"		:	{"password": "123", "score": 50, "questions_asked": []},
    #     "master"	:	{"password": "master", "score": 200, "questions_asked": []}
    # }
    users = {}
    with open('users.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            things = line.split('|')
            users[things[0]] = {}
            users[things[0]]['password'] = things[1]
            users[things[0]]['score'] = int(things[2])
            if things[-1] != '':
                users[things[0]]['questions_asked'] = [int(x) for x in things[3].split(',')]
            else:
                users[things[0]]['questions_asked'] = []
    return users


def setup_socket():
    """
    Creates new listening socket and returns it
    Receives: -
    Returns: the socket object
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(10)
    return server_socket


def send_error(conn, error_msg):
    """
    Send error message with given message
    Receives: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, 'ERROR', error_msg.encode())


def handle_getscore_message(conn, username):
    global users
    score = users[username]['score']
    build_and_send_message(conn, 'YOUR_SCORE', str(score))


def handle_logout_message(conn):
    """
    Closes the given socket (in later chapters, also remove user from logged_users dictionary)
    Receives: socket
    Returns: None
    """
    global logged_users
    clientname = conn.getpeername()
    del logged_users[clientname]


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Receives: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users # To be used later
    username, password = data.split('#')[0], data.split('#')[1]
    if username in users:
        if password == users[username]['password']:
            logged_users[conn.getpeername()] = username
            build_and_send_message(conn, 'LOGIN_OK', '')
        else:
            send_error(conn, 'wrong password')
            return
    else:
        send_error(conn, 'username doesnt exist')
        return


def print_client_sockets():
    global logged_users
    print(logged_users)


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Receives: socket, message code and data
    Returns: None
    """
    global logged_users
    if conn.getpeername() in logged_users:
        username = logged_users[conn.getpeername()]
        if cmd == 'LOGOUT' or cmd == '':
            handle_logout_message(conn)
        elif cmd == 'MY_SCORE':
            handle_getscore_message(conn, username)
        elif cmd == 'SEND_ANSWER':
            handle_answer_message(conn, username, data)
        elif cmd == 'GET_QUESTION':
            handle_question_message(conn, username)
        elif cmd == 'LOGGED':
            handle_logged(conn)
        elif cmd == 'HIGHSCORE':
            handle_get_highscore(conn)
        else:
            send_error(conn, 'wrong command')
    elif cmd == 'LOGIN':
        handle_login_message(conn, data)
    else:
        send_error(conn, 'not connected')


def create_random_question(username):
    global questions
    global users
    temp_questions = questions
    while len(temp_questions.keys()) != 0:
        question_id = random.choice(list(temp_questions.keys()))
        if question_id not in users[username]['questions_asked']:
            answer = questions[question_id]['answers']
            answer = '#'.join(answer)
            question_data = str(question_id) + "#" + questions[question_id]['question'] + '#' + answer
            users[username]['questions_asked'].append(question_id)
            return chatlib.build_message('YOUR_QUESTION', question_data)
        del temp_questions[question_id]
    return chatlib.build_message('NO_QUESTIONS', '')


def handle_question_message(conn, username):
    question = create_random_question(username)
    conn.send(question.encode())


def handle_get_highscore(conn):
    global users
    scores = []
    for user in users:
        scores.append((user, users[user]['score']))
    scores = scores[:5]
    scores.sort(key=lambda x: x[1], reverse=True)
    protocol_scores = ''
    for tuplee in scores:
        protocol_scores += tuplee[0] + ":" + str(tuplee[1]) + '\n'
    build_and_send_message(conn, 'ALL_SCORE', protocol_scores)


def handle_logged(conn):
    global logged_users
    userim = ','.join(list(logged_users.values()))
    build_and_send_message(conn, 'LOGGED_ANSWER', userim)


def handle_answer_message(conn, username, answer):
    global users
    global questions
    question_id, ans = answer.split('#')[0], answer.split('#')[1]
    if questions[int(question_id)]['correct'] == int(ans):
        build_and_send_message(conn, 'CORRECT_ANSWER', '')
        users[username]['score'] += 1
    else:
        build_and_send_message(conn, 'WRONG_ANSWER', str(questions[int(question_id)]['correct']))


def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions
    global messages_to_send
    clients = []
    print("Welcome to Trivia Server!")
    users = load_user_database()
    questions = load_questions()
    server_socket = setup_socket()
    while True:
        rlist, wlist, xlist = select.select([server_socket] + clients, [], [])
        for skt in rlist:
            if skt is server_socket:
                client_socket, client_address = server_socket.accept()
                clients.append(client_socket)
                print('New connection received')
            else:
                cmd, msg = recv_message_and_parse(client_socket)
                handle_client_message(client_socket, cmd, msg)
                if cmd == 'LOGOUT' or cmd == '':
                    clients.remove(skt)
                    skt.close()
        for mesg in messages_to_send:
            mesg[0].send(mesg[1].encode())
            messages_to_send.remove(mesg)

if __name__ == '__main__':
    main()
