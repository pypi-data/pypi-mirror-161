from .wordtile import *
from .console import *
from .mocio import *
from .border import *
from .ui import *
import threading
import pygame

window = Console()
moprint = Printer()
moinput = Reader()


def init(width, height, font_height, title) -> None:
    """
    生成控制台界面

    :param width: 窗口宽（字符）
    :param height: 窗口高（字符）
    :param font_height: 字符大小
    :param title: 窗口标题
    """
    ok = False

    def create_console():
        global window
        window.init(width, height, font_height, title)
        nonlocal ok
        ok = True
        window.start()

    thread = threading.Thread(target=create_console)
    thread.start()
    while not ok:
        pygame.time.wait(10)
    global window
    moprint.bind(window)
    moinput.bind(window, moprint)


def close() -> None:
    pygame.event.post(pygame.event.Event(pygame.QUIT))
