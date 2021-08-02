import logging, os, pathlib, sys

import bs4
from bs4 import BeautifulSoup


## settings from env/activate
LOG_PATH = os.environ['ANX_ALMA__LOG_PATH']
LOG_LEVEL = os.environ['ANX_ALMA__LOG_LEVEL']  # 'DEBUG' or 'INFO'


## logging
log_level = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=log_level[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S'
    )
log = logging.getLogger(__name__)
log.debug( 'log setup' )


class Parser():

    def __init__(self):
        self.all_text = ''
        self.items = []  # bs4.element.ResultSet
        # self.current_item = None  # bs4.element.Tag
        self.item_text = ''
        self.xml_obj = None
        self.title = ''
        self.patron_name = ''

    def load_file( self, filepath ):
        ( self.all_text, err ) = ( '', None )
        try:
            assert type( filepath ) == str
            with open( filepath, encoding='utf-8' ) as f:
                self.all_text = f.read()
        except Exception as e:
            err = repr(e)
            log.exception( f'problem loading source-file, ``{err}``' )
        log.debug( f'self.all_text, ``{self.all_text[0:100]}``' )
        return ( self.all_text, err )

    def make_item_list( self, all_text ):
        try:
            log.debug( f'all_text, ``{all_text}``' )
            assert type( all_text ) == str
            ( self.items_text, err ) = ( [], None )
            soup = BeautifulSoup( all_text, 'xml' )  # encoding not specified because I'm giving it unicode
            self.items = soup.select( 'rsExport' )
            log.debug( f'self.items, ``{self.items}``' )
            assert type(self.items) == bs4.element.ResultSet
            return ( self.items, err )
        except:
            err = 'problem preparing items'
            log.exception( err )
        log.debug( f'self.items, ``{self.items}``' )
        return ( self.items, err )

    def parse_title( self, item ):
        ( self.title, err ) = ( '', None )
        try:
            assert type(item) == bs4.element.Tag
            title_elements = item.select( 'title' )
            assert type( title_elements ) == bs4.element.ResultSet
            title = title_elements[0].get_text()  # only one title in item-xml
            assert type( title ) == str
            self.title = title
        except:
            err = 'problem parsing title'
            log.exception( err )
        log.debug( f'self.title, ``{self.title}``' )
        return ( self.title, err )




