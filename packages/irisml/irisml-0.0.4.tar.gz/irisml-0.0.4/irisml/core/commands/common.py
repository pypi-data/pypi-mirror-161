import logging
import sys


class ColoredStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None, colorscheme=None):
        super().__init__(stream)
        self._stream = stream
        self._colorscheme = colorscheme

    def emit(self, record):
        try:
            msg = self.format(record)
            msg = self._add_color(msg, record.levelno)
            self.stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

    def _add_color(self, msg, levelno):
        color_code = self._colorscheme.get(levelno, '\x1b[0m')
        return color_code + msg + '\x1b[0m'

    def __getstate__(self):
        return {'stream': self._stream, 'colorscheme': self._colorscheme, 'formatter': self.formatter}

    def __setstate__(self, state):
        self.__init__(state['stream'], state['colorscheme'])
        self.setFormatter(state['formatter'])


class PicklableStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)
        self._stream = stream

    def __getstate__(self):
        return {'stream': self._stream, 'formatter': self.formatter}

    def __setstate__(self, state):
        self.__init__(state['stream'])
        self.setFormatter(state['formatter'])


LOG_COLORS = {
    logging.CRITICAL: '\x1b[91;101m',
    logging.ERROR: '\x1b[101m',
    logging.WARNING: '\x1b[33;20m',
    logging.INFO: '',
    logging.DEBUG: '\x1b[36m'
}


class Formatter(logging.Formatter):
    def __init__(self, fmt=None, task_fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self._task_formatter = logging.Formatter(task_fmt, datefmt)

    def format(self, record):
        if record.name.startswith('irisml.tasks.'):
            record.task = record.name[13:]
            return self._task_formatter.format(record)
        return super().format(record)


def configure_logger(verbose_level=0):
    """Configure logging handlers. Show logs in color if the stdout is connected to a terminal.

       Args:
           verbose_level (int): 0: No DEBUG logs. 1: DEBUG logs only from irisml. 2: DEBUG logs from all modules.
    """
    handler = ColoredStreamHandler(colorscheme=LOG_COLORS) if sys.stderr.isatty() else PicklableStreamHandler()
    formatter = Formatter('%(asctime)s %(levelname)-8s %(message)s (%(name)s)', '%(asctime)s %(levelname)-8s [%(task)s] %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose_level >= 2 else logging.INFO)
    logger.addHandler(handler)

    # Suppress noisy logs
    logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

    if verbose_level >= 1:
        logging.getLogger('irisml').setLevel(logging.DEBUG)
