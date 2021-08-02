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
        self.item_text = ''
        self.xml_obj = None

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
        except Exception as e:
            err = repr(e)
            log.exception( f'problem making item-list, ``{err}``' )
        log.debug( f'self.items, ``{self.items}``' )
        return ( self.items, err )

    def parse_item_id( self, item ):
        ( item_id, err ) = self.parse_element( item, 'itemId' )
        log.debug( f'item_id, ``{item_id}``' )
        return ( item_id, err )

    def parse_item_title( self, item ):
        ( item_title, err ) = self.parse_element( item, 'title' )
        log.debug( f'item_title, ``{item_title}``' )
        return ( item_title, err )

    def parse_item_barcode( self, item ):
        ( item_barcode, err ) = self.parse_element( item, 'barcode' )
        log.debug( f', ``{item_barcode}``' )
        return ( item_barcode, err )

    def parse_element ( self, item, tag_name ):
        """ Returns text for given tag-name.
            Called by individual parsers, above. """
        log.debug( f'tag_name, ``{tag_name}``' )
        ( element_text, err ) = ( '', None )
        try:
            assert type(item) == bs4.element.Tag
            assert type(tag_name) == str
            elements = item.select( tag_name )
            assert type( elements ) == bs4.element.ResultSet
            log.debug( f'len(elements), ``{len(elements)}``' )
            if len( elements ) > 0:
                element_text = elements[0].get_text()
                assert type( element_text ) == str
        except Exception as e:
            err = repr(e)
            log.exception( f'problem parsing tag, ``{tag_name}``, ``{err}``' )
        log.debug( f'element_text, ``{element_text}``' )
        return ( element_text, err )


    ## end class Parser()


