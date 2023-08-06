"""
\033[显示方式; 前景色; 背景色m******\033[0m

显示方式	显示效果
0	    默认值
1	    高亮
3	    斜体
4	    下划线
5	    闪烁
7	    反显
8	    不可见

前景色	背景色	颜色说明
30	    40	    黑色
31	    41	    红色
32	    42	    绿色
33	    43	    黄色
34	    44	    蓝色
35	    45	    紫红色
36	    46	    青蓝色
37	    47	    白色

黑色 black
红色 red
绿色 green
黄色 yellow
蓝色 blue
紫红色 purple
青蓝色 cyan
白色 white
"""


# from colorama import init
#
# init(autoreset=True)


def show():
    print("\033[30m这是 30 黑色字体\033[0m", end='\t')
    print("\033[31m这是 31 红色字体\033[0m", end='\t')
    print("\033[32m这是 32 绿色字体\033[0m", end='\t')
    print("\033[33m这是 33 黄色字体\033[0m", end='\t')
    print("\033[34m这是 34 蓝色字体\033[0m", end='\t')
    print("\033[35m这是 35 紫红色字体\033[0m", end='\t')
    print("\033[36m这是 36 青蓝色字体\033[0m", end='\t')
    print("\033[37m这是 37 白色字体\033[0m")

    print("\033[0;37;40m这是 40 黑色 背景 \033[0m", end='\t')
    print("\033[0;30;41m这是 41 红色 背景 \033[0m", end='\t')
    print("\033[0;30;42m这是 42 绿色 背景 \033[0m", end='\t')
    print("\033[0;30;43m这是 43 黄色 背景 \033[0m", end='\t')
    print("\033[0;30;44m这是 44 蓝色 背景 \033[0m", end='\t')
    print("\033[0;30;45m这是 45 紫红色 背景 \033[0m", end='\t')
    print("\033[0;30;46m这是 46 青蓝色 背景 \033[0m", end='\t')
    print("\033[0;30;47m这是 47 白色 背景 \033[0m")

    print("\033[0;30;42m这是 0 默认值 效果 \033[0m", end='\t')
    print("\033[1;30;42m这是 1 高亮 效果 \033[0m", end='\t')
    print("\033[3;30;42m这是 3 斜体 效果 \033[0m", end='\t')
    print("\033[4;30;42m这是 4 下划线 效果 \033[0m", end='\t')
    print("\033[5;30;42m这是 5 闪烁 效果 \033[0m", end='\t')
    print("\033[7;30;42m这是 7 反显 效果 \033[0m", end='\t')
    print("\033[8;30;42m这是 8 不可见 效果 \033[0m")


class LM_PRINT():
    @staticmethod
    def print_black(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[30m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')

    @staticmethod
    def print_red(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[31m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')

    @staticmethod
    def print_green(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[32m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')

    @staticmethod
    def print_yellow(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[33m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')

    @staticmethod
    def print_blue(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[34m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')

    @staticmethod
    def print_purple(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[35m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')

    @staticmethod
    def print_cyan(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[36m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')

    @staticmethod
    def print_white(*values, sep=' ', end='\n', file=None, flush=False):
        print('\033[37m', end='')
        print(*values, sep=sep, end=end, file=file, flush=flush)
        print('\033[0m', end='')


def log_print(*values, sep=' ', end='\n', file=None, flush=False, log=True):
    if log:
        print('\033[37m', end='')
        print(*values, sep=sep, end='', file=file, flush=flush)
        print('\033[0m', end=end)


def printer(str, sep=' ', end='\n', file=None, flush=False, color='black', log=True):
    if log:
        colorIndex = {'black': 30, 'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'purple': 35, 'cyan': 36, 'white': 37}
        colorValue = colorIndex[color] if color in colorIndex.keys() else False
        print(f'\033[{colorValue}m{str}\033[0m', sep=sep, end=end, file=file, flush=flush)


if __name__ == '__main__':
    # printer('aaa', color='red', log=True)
    # printer(22222)
    # show()
    # LM_PRINT.print_purple('ppppppppppp')
    pass
