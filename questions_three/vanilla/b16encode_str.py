from base64 import b16encode


def b16encode_str(s):
    return b16encode(bytes(s, 'utf-8')).decode('utf-8')
