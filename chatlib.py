# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def check_for_errors(cmd, data, leng):
    """בודקת אם ההודעה רשומה בחוקי הפרוטוקול"""
    if len(cmd) > 16 or len(data) > 9999 or len(data) < 0 or int(leng) != len(data):
        return False
    return True


def build_message(cmd, data):
    """רושם הודעת פרוטוקל מדוייקת"""
    try:
        if not check_for_errors(cmd, data, len(data)):
            return None
        full_msg = f'{cmd.ljust(16)}|{str(len(data)).rjust(4,"0")}|{data}'
        return full_msg
    except:
        return None


def parse_message(msg):
    """מחזיר פקודה והודעה מתוך הפרוטוקול"""
    try:
        splitted_msg = msg.split('|',2)
        if not check_for_errors(splitted_msg[0],splitted_msg[-1],splitted_msg[1]):
            return None,None
        cmd = splitted_msg[0].split()[0]
        data = splitted_msg[2]
        return cmd, data
    except:
        return None,None


def split_msg(msg):
    """עוזר בבדיקת תקינות מחזירה את המחרוזת התקינה עם מםרידים"""
    try:
        if len(msg.split('|')) < 3:
            return None
        if not check_for_errors(msg.split('|',2)[0],msg.split('|',2)[2],msg.split('|',2)[1]):
            return None
        return msg.split('|',2)
    except:
        return None


def join_msg(msg_fields):
    """מקבלת ערכגים הופכת אותם  להודעה תקינה"""
    for value in msg_fields:
        value = str(value)
    msg_fields.join('|')