import threading


def get_request_info():
    try:
        request_info = threading.current_thread().request_info
    except:
        request_info = {}

    return request_info
