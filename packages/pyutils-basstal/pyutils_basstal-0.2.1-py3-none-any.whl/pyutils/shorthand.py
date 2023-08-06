import sys

######################
######################
#       简写      #
######################
######################


def is_win():
    return sys.platform.lower().startswith('win')


def is_macOS():
    return sys.platform.lower().startswith('darwin')
