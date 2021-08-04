import datetime, logging, os, pathlib, sys

import bs4
from bs4 import BeautifulSoup
from parse_alma_annex_requests_code.lib import mapper


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

    ## -- non-parsing methods -------------------

    def load_file( self, filepath ):
        ( self.all_text, err ) = ( '', None )
        try:
            log.debug( f'filepath, ``{filepath}``' )
            assert type( filepath ) == str
            with open( filepath, encoding='utf-8' ) as f:
                self.all_text = f.read()
        except Exception as e:
            err = repr(e)
            log.exception( f'problem loading source-file, ``{err}``' )
        log.debug( f'self.all_text, ``{self.all_text[0:100]}``' )
        return ( self.all_text, err )

    def make_item_list( self, all_text ):
        ( self.items, err ) = ( [], None )
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

    def prepare_gfa_entry( self, item_id, item_title, item_barcode, patron_name, patron_barcode, patron_note, parsed_pickup_library, parsed_library_code ):
        """ Prepares all GFA data elements. """
        ( gfa_entry, err ) = ( [], None )
        try:
            for element in [ item_id, item_title, item_barcode, patron_name, patron_barcode, patron_note, parsed_pickup_library, parsed_library_code ]:
                assert type( element ) == str
            ( gfa_delivery, err ) = self.transform_parsed_pickup_library( parsed_pickup_library )
            if err == None:
                ( gfa_location, err ) = self.transform_parsed_library_code( parsed_library_code, gfa_delivery )
                if err == None:
                    gfa_entry = [
                        item_id, item_barcode, gfa_delivery, gfa_location, patron_name, patron_barcode, item_title, self.prepare_gfa_datetime(), patron_note
                    ]
            log.debug( f'gfa_entry, ``{gfa_entry}``' )
        except Exception as e:
            err = repr( e )
            log.exception( f'problem preparing gfa entry, ``{err}``' )
        log.debug( f'gfa_entry, ``{gfa_entry}``' )
        return ( gfa_entry, err )

    def transform_parsed_pickup_library( self, parsed_pickup_library ):
        ( gfa_delivery, err ) = ( '', None )
        try:
            assert type( parsed_pickup_library) == str
            if parsed_pickup_library == 'DIGITAL_REQUEST':
                gfa_delivery = 'ED'
            else:
                source_dct = mapper.ALMA_PICKUP_TO_GFA_DELIVERY
                gfa_delivery = source_dct[parsed_pickup_library]
        except Exception as e:
            err = repr( e )
            log.exception( f'problem preparing gfa_delivery, ``{err}``' )
        log.debug( f'gfa_delivery, ``{gfa_delivery}``' )
        return ( gfa_delivery, err )

    def transform_parsed_library_code( self, parsed_library_code, gfa_delivery ):
        ( gfa_location, err ) = ( '', None )
        try:
            assert type( parsed_library_code) == str
            assert type( gfa_delivery ) == str
            if gfa_delivery == 'ED':
                gfa_location = 'ED'
            else:
                source_dct = mapper.ALMA_LIBRARY_CODE_TO_GFA_LOCATION
                gfa_location = source_dct[parsed_library_code]
        except Exception as e:
            err = repr( e )
            log.exception( f'problem preparing gfa_location, ``{err}``' )
        log.debug( f'gfa_location, ``{gfa_location}``' )
        return ( gfa_location, err )

    def prepare_gfa_datetime( self, datetime_obj=None ):
        """ In practice, no datetime-object will be passed in, but the 'datetime_obj=None' allows for easy testing. """
        if datetime_obj == None:
            datetime_obj = datetime.datetime.now()
        datetime_str = datetime_obj.strftime( '%a %b %d %Y' )
        log.debug( f'datetime_str, ``{datetime_str}``' )
        return datetime_str

    ## -- just parsers ---------------------------

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

    def parse_patron_name( self, item ):
        ( patron_name, err ) = self.parse_element( item, 'patronName' )
        log.debug( f', ``{patron_name}``' )
        return ( patron_name, err )

    def parse_patron_barcode( self, item ):
        ( patron_barcode, err ) = self.parse_element( item, 'patronIdentifier' )
        log.debug( f', ``{patron_barcode}``' )
        return ( patron_barcode, err )

    def parse_patron_note( self, item ):
        ( patron_note, err ) = self.parse_element( item, 'requestNote' )
        log.debug( f', ``{patron_note}``' )
        return ( patron_note, err )

    def parse_pickup_library( self, item ):
        interpreted_pickup_library = 'init'
        ( request_type, err ) = self.parse_element( item, 'requestType' )
        log.debug( f'request_type, ``{request_type}``' )
        if request_type == 'PHYSICAL_TO_DIGITIZATION':
            interpreted_pickup_library = 'DIGITAL_REQUEST'
        else:
            ( pickup_library, err ) = self.parse_element( item, 'library' )
            log.debug( f'pickup_library, ``{pickup_library}``' )
            interpreted_pickup_library = pickup_library
        log.debug( f'interpreted_pickup_library, ``{interpreted_pickup_library}``' )
        return ( interpreted_pickup_library, err )

    def parse_library_code( self, item ):
        ( library_code, err ) = self.parse_element( item, 'libraryCode' )
        log.debug( f', ``{library_code}``' )
        return ( library_code, err )

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


