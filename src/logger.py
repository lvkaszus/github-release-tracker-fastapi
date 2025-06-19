import logging
import colorlog

PREFIX = "[FastAPI GitHub Release Tracker - by @lvkaszus]"

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    f"%(purple)s{PREFIX}%(reset)s - %(log_color)s%(levelname)-8s%(reset)s - "
    "%(white)s%(asctime)s%(reset)s - %(log_color)s%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    },
    secondary_log_colors={},
    style='%'
))

logger = colorlog.getLogger("main")
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
