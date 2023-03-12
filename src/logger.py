import logging

FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LEVEL = logging.INFO


def init_root_logger():
    root = logging.getLogger()
    root.setLevel(LEVEL)

    sh = logging.StreamHandler()
    sh.setLevel(LEVEL)

    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
    sh.setFormatter(formatter)

    if root.hasHandlers():
        root.handlers.clear()

    root.addHandler(sh)
