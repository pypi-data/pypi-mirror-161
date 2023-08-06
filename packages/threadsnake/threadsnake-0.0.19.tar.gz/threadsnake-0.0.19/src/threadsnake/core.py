import imp
from .myhttp.http_classes import *
from .myhtml.Html import *
from .pypress_classes import *
from .middlewares import *
from .markdown import *
from .data_access import *
from sys import argv

def get_port(default:int):
    return int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else default
