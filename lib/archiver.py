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
        self.new_file_name = ''
        self.destination_filepath = ''

    def check_for_new_file(self, dir_path):
        """ Checks if there is a file waiting. """
        ( exists, err ) = ( False, None )
        try:
            assert type(dir_path) == str
            contents = os.listdir( dir_path )
            assert type(contents) == list
            for item in contents:
                log.debug( f'item, ``{item}``' )
                if item.startswith( 'BUL_ANNEX' ):
                    exists = True
                    self.new_file_name = item
                    log.debug( f'self.new_file_name, ``{self.new_file_name}``' )
                    break
        except Exception as e:
            err = repr(e)
            log.exception( f'Problem checking for new file, ``{err}``' )
        log.debug( f'exists, ``{exists}``; err, ``{err}``' )
        return ( exists, err )

    def make_datetime_stamp( self, datetime_obj ):
        """ Creates a a time-stamp string for the files to be archived, like '2021-07-13T13-41-39' """
        iso_datestamp = datetime_obj.isoformat()
        custom_datestamp = iso_datestamp[0:19].replace( ':', '-' )  # colons to slashes to prevent filename issues
        return str( custom_datestamp )

    def copy_original_to_archives( self, source_file_path, destination_dir_path, datetime_stamp ):
        """ Archives original before doing anything else. """
        log.debug( f'source_file_path, ``{source_file_path}``' )
        log.debug( f'destination_dir_path, ``{destination_dir_path}``' )
        ( success, err ) = ( False, None )
        try:
            assert type(source_file_path) == str
            assert type(destination_dir_path) == str
            assert type(datetime_stamp) == str
            source_path_obj = pathlib.Path( source_file_path )
            source_filename = source_path_obj.name
            self.destination_filepath = f'{destination_dir_path}/{datetime_stamp}__{source_filename}'
            log.debug( f'self.destination_filepath, ``{self.destination_filepath}``' )
            shutil.copy2( source_file_path, self.destination_filepath )
            destination_path_obj = pathlib.Path( self.destination_filepath )
            log.debug( f'destination_path_obj, ``{destination_path_obj}``' )
            assert destination_path_obj.exists() == True
            success = True
        except Exception as e:
            err = repr(e)
            log.exception( f'Problem checking for new file, ``{err}``' )
        log.debug( f'success, ``{success}``; err, ``{err}``' )
        return ( success, err )

    # -- common ---------------------------------

    def log_and_quit( self, message ):
        """ Exits on various errors. """
        message = f'{message}\n\n'
        log.info( message )
        sys.exit( message )

## end class Archiver
