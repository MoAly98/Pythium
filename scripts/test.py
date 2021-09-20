import logging
import utils
from utils.logger import ColoredLogger

if __name__ == '__main__':
    logger = ColoredLogger()
    logger.setLevel(logging.INFO)
    def add(a, b, debug=False):
        if debug:
            logger.error('a is type '+str(type(a)))
        return a+b

    x = add(5,3, debug=True)
