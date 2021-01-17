import threading


def run_async(func, args):
    threading.Thread(target=func, args=args).start()