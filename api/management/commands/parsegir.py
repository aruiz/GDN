import logging
import sys

from django.core.management.base import BaseCommand
from giscanner.girparser import GIRParser
from api.storage import GIR_PATH, store_parser

log = logging.getLogger(__name__)

class Command(BaseCommand):

    help = '''\
Parse installed GIR files
'''

    def handle(self, *args, **kwargs):
        parser = GIRParser()
        if len(sys.argv) == 3:
            library = sys.argv[2]
        else:
            library = "Gtk-3.0"
        print "Parsing %s" % library
        parser.parse(GIR_PATH % library)
        store_parser(parser)
