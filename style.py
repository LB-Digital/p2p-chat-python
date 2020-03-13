

# CLASS:Style
# stores ANSI escape sequences for console logging in
class Style:
    END = '\033[0m'

    @staticmethod
    def warning(txt):
        return '\033[33m' + txt + Style.END

    @staticmethod
    def success(txt):
        return '\033[32m' + txt + Style.END

    @staticmethod
    def info(txt):
        return '\033[36m' + txt + Style.END

    @staticmethod
    def error(txt):
        return '\033[31m' + txt + Style.END

    @staticmethod
    def bright_green(txt):
        return '\033[34m' + txt + Style.END

    @staticmethod
    def clear():
        print('\x1b[2K\r', end='')

    # COLORS = {
    #     'WARNING': '\033[33m'
    # }
    # END = '\033[0m'
    #
    # @staticmethod
    # def colorize(color, txt):
    #     if color in Color.COLORS:
    #         return Color.COLORS[color] + txt + Color.END
    #     raise Exception('Color "' + color + '" invalid!')
