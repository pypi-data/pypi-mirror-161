import logging
from os import pardir
from os.path import abspath, dirname, join

# Debug file formatter
DEBUGFILE = 'debug.log'
DEBUGFORMATTER = '%(filename)s:%(name)s:%(funcName)s:%(lineno)d: %(message)s'

# Log file and stream output formatter
INFOFILE = 'info.log'
INFOFORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

ROOT_DIR = dirname(abspath(__file__))
DEBUG_DIR = abspath(join(ROOT_DIR, pardir))
DEBUG_DIR += '/'

# define global logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# define debug stream handler
db = logging.FileHandler(DEBUG_DIR + DEBUGFILE, mode='w')
db.setLevel(logging.DEBUG)
db.setFormatter(logging.Formatter(DEBUGFORMATTER))

# define info stream handler
info = logging.FileHandler(DEBUG_DIR + INFOFILE, mode='w')
info.setLevel(logging.INFO)
info.setFormatter(logging.Formatter(INFOFORMATTER))

# adds the handlers to the global variable: log
log.addHandler(db)
log.addHandler(info)
