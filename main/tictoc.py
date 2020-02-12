import time


def tic():
    return time.time()


def toc(a, text='', dif=0):
    b = time.time()
    print(text)
    print('time:', b-a)
    if dif:
        print('dif', b-dif)
    return b
