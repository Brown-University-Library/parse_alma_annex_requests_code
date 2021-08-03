import logging, os, pathlib, shutil, sys


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


class Archiver():

    def __init__(self):
        pass

    def check_for_new_file(self, dir_path):
        """ Checks if there is a file waiting; if so, returns new_file_name. """
        ( new_file_name, err ) = ( '', None )
        try:
            assert type(dir_path) == str
            log.debug( f'new-file dir_path, ``{dir_path}``' )
            contents = os.listdir( dir_path )
            assert type(contents) == list
            for item in contents:
                log.debug( f'item, ``{item}``' )
                if item.startswith( 'BUL_ANNEX' ):
                    exists = True
                    new_file_name = item
                    log.debug( f'new_file_name, ``{new_file_name}``' )
                    break
        except Exception as e:
            err = repr(e)
            log.exception( f'Problem checking for new file, ``{err}``' )
        log.debug( f'new_file_name, ``{new_file_name}``; err, ``{err}``' )
        return ( new_file_name, err )

    def make_datetime_stamp( self, datetime_obj ):
        """ Creates a a time-stamp string for the files to be archived, like '2021-07-13T13-41-39' """
        iso_datestamp = datetime_obj.isoformat()
        custom_datestamp = iso_datestamp[0:19].replace( ':', '-' )  # colons to slashes to prevent filename issues
        return str( custom_datestamp )

    def copy_original_to_archives( self, source_file_path, datetime_stamp, destination_dir_path ):
        """ Archives original before doing anything else. """
        log.debug( f'source_file_path, ``{source_file_path}``' )
        log.debug( f'destination_dir_path, ``{destination_dir_path}``' )
        ( destination_filepath, err ) = ( '', None )
        try:
            assert type(source_file_path) == str
            assert type(destination_dir_path) == str
            assert type(datetime_stamp) == str
            source_path_obj = pathlib.Path( source_file_path )
            source_filename = source_path_obj.name
            destination_filepath = f'{destination_dir_path}/REQ-ALMA-ORIG_{datetime_stamp}.xml'
            log.debug( f'destination_filepath, ``{destination_filepath}``' )
            shutil.copy2( source_file_path, destination_filepath )
            ## check that it's there
            destination_path_obj = pathlib.Path( destination_filepath )
            log.debug( f'destination_path_obj, ``{destination_path_obj}``' )
            assert destination_path_obj.exists() == True
            success = True
        except Exception as e:
            destination_filepath = ''
            err = repr(e)
            log.exception( f'Problem checking for new file, ``{err}``' )
        log.debug( f'destination_filepath, ``{destination_filepath}``; err, ``{err}``' )
        return ( destination_filepath, err )

    def stringify_gfa_data( self, gfa_items ):
        """ line elements: [ item_id, item_barcode, gfa_delivery, gfa_location, patron_name, patron_barcode, item_title, gfa_date_str, patron_note ] """
        ( text, err ) = ( '', None )
        try:
            assert type(gfa_items) == list
            text = ''
            for item in gfa_items:
                ( item_id, item_barcode, gfa_delivery, gfa_location, patron_name, patron_barcode, item_title, gfa_date_str, patron_note ) = ( item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8] )
                line = '''"%s","%s","%s","%s","%s","%s","%s","%s","%s"''' % (
                    item_id, item_barcode, gfa_delivery, gfa_location, patron_name, patron_barcode, item_title, gfa_date_str, patron_note
                    )
                text = text + line + '\n'
        except Exception as e:
            err = repr(e)
            log.exception( f'Problem transforming list of lists into text, ``{err}``' )
        log.debug( f'text, ``{text}``; err, ``{err}``' )
        return ( text, err )

    def save_parsed_to_archives( self, text, datetime_stamp, destination_dir_path ):
        log.debug( f'text[0:100], ``{text[0:100]}``' )
        log.debug( f'destination_dir_path, ``{destination_dir_path}``' )
        log.debug( f'datetime_stamp, ``{datetime_stamp}``' )
        ( success, err ) = ( False, None )
        try:
            assert type(text) == str
            assert type(datetime_stamp) == str
            assert type(destination_dir_path) == str
            destination_filepath = f'{destination_dir_path}/REQ-ALMA-PARSED_{datetime_stamp}.dat'
            log.debug( f'destination_filepath, ``{destination_filepath}``' )
            with open( destination_filepath, 'w' ) as file_handler:
                file_handler.write( text )
            ## check that it's there
            destination_path_obj = pathlib.Path( destination_filepath )
            assert destination_path_obj.exists() == True
            success = True
        except Exception as e:
            err = repr(e)
            log.exception( f'Problem checking for new file, ``{err}``' )
        log.debug( f'success, ``{success}``; err, ``{err}``' )
        return ( success, err )

    def send_gfa_count_file( self, count, datetime_stamp, gfa_count_dir ):
        err = None
        count_file_name = f'REQ-PARSED_{datetime_stamp}.cnt'
        count_file_gfa_destination_path = f'{gfa_count_dir}/{count_file_name}'
        count_str = f'{count}\n'
        try:
            with open( count_file_gfa_destination_path, 'w' ) as file_handler:
                file_handler.write( count_str )
            log.info( f'count file saved to, ``{count_file_gfa_destination_path}``' )
        except Exception as e:
            err = repr(e)
            log.exception( f'problem on save of count file, ``{err}``' )
        try:
            os.chmod( count_file_gfa_destination_path, 0o666 )   # `rw-/rw-/rw-`
        except Exception as e:
            log.exception( 'could not set file-permissions on count destination-path' )
            ## not returning error that would quit processing
        return err

    def send_gfa_data_file( self, text, datetime_stamp, gfa_data_dir ):
        err = None
        data_file_name = f'REQ-PARSED_{datetime_stamp}.dat'
        data_file_gfa_destination_path = f'{gfa_data_dir}/{data_file_name}'
        try:
            with open( data_file_gfa_destination_path, 'w' ) as file_handler:
                file_handler.write( text )
            log.info( f'data file saved to, ``{data_file_gfa_destination_path}``' )
        except Exception as e:
            err = repr(e)
            log.exception( f'problem on save of data file, ``{err}``' )
        try:
            os.chmod( data_file_gfa_destination_path, 0o666 )   # `rw-/rw-/rw-`
        except Exception as e:
            log.exception( 'could not set file-permissions on data destination-path' )
            ## not returning error that would quit processing
        return err

        # try:
        #     count_file_name = 'REQ-PARSED_%s.cnt' % date_stamp
        #     count_file_las_destination_path = '%s/%s' % ( self.PATH_TO_PARSED_ANNEX_COUNT_DIRECTORY, count_file_name )
        #     f = open( count_file_las_destination_path, 'w' )
        #     count_str = '%s' % count + '\n'
        #     f.write( count_str.encode('utf-8') )
        #     f.close()
        #     try:
        #         os.chmod( count_file_las_destination_path, 0666 )   # rw-/rw-/rw-
        #     except Exception, e:
        #         log.info( 'could not set file-permissions on count-destination-path; exception, `%s` -- continuing' % unicode(repr(e)) )
        #     log.info( 'count file written to: ```%s```' % count_file_las_destination_path )
        # except Exception, e:
        #     message = 'problem on save of count file to ```%s```; quitting; exception is: `%s`' % (count_file_las_destination_path, unicode(repr(e)) )
        #     log.error( message )
        #     sys.exit( message )


## end class Archiver
