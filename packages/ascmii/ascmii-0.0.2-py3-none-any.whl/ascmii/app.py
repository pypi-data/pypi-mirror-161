from . import __version__ as v

from appscii import *
import lank


class ASCMII(Application):
    def init(self):
        self.about = About(self)


class About(Window):
    def __init__(self, app):
        super().__init__(app, 18, 9, 27, 9)

        self.text.center()
        self.text.word_wrap()

        self.text.print(f'ASCMII v{v}')
        self.text.print('"Ask Me"')
        self.text.print(f'The ASCII Messenger')
        self.text.print()
        self.text.print('-with-')
        self.text.print(f'LANK v{lank.__version__}')
        self.text.print(f'appscii v{__version__}')

