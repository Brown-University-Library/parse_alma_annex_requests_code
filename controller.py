import datetime, json, logging, os, pprint, shutil, smtplib, sys
# from email.Header import Header
from email.mime.text import MIMEText

sys.path.append( os.environ['ANX_ALMA__ENCLOSING_PROJECT_PATH'] )
from parse_alma_annex_requests_code.lib.archiver import Archiver
from parse_alma_annex_requests_code.lib.parser import Parser
# from process_email_pageslips.lib.utility_code import Mailer


lvl_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
lvl = os.environ['ANX_ALMA__LOG_LEVEL']
logging.basicConfig(
    filename=os.environ['ANX_ALMA__LOG_PATH'],
    level=lvl,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)
log.info( '\n\nstarting log\n============' )


class Controller(object):
    """ Manages steps. """

    def __init__( self ):
        self.PATH_TO_SOURCE_DIRECTORY = os.environ['ANX_ALMA__PATH_TO_SOURCE_DIRECTORY']  # to check for new files
        self.PATH_TO_ARCHIVED_ORIGINALS_DIRECTORY = os.environ['ANX_ALMA__PATH_TO_ARCHIVED_ORIGINALS_DIRECTORY']
        self.PATH_TO_ARCHIVES_PARSED_DIRECTORY = os.environ['ANX_ALMA__PATH_TO_ARCHIVED_PARSED_DIRECTORY']
        self.PATH_TO_GFA_COUNT_DIRECTORY = os.environ['ANX_ALMA__PATH_TO_GFA_COUNT_DIR']
        self.PATH_TO_GFA_DATA_DIRECTORY = os.environ['ANX_ALMA__PATH_TO_GFA_DATA_DIR']
        self.DEV_MODE = json.loads( os.environ['ANX_ALMA__DEV_MODE'] )  # in dev-mode, new-original will not be deleted

    def process_requests( self ):
        """ Steps caller.
            Called by ```if __name__ == '__main__':``` """
        log.debug( 'starting process_requests()' )
        arcvr = Archiver()
        prsr = Parser()

        ## -- check for new file ----------------
        (new_file_name, err) = arcvr.check_for_new_file( self.PATH_TO_SOURCE_DIRECTORY )
        if err:
            raise Exception( f'Problem checking for new file, ``{err}``' )
        if new_file_name == '':
            message = 'no annex requests found; quitting\n\n'
            log.info( message )
            sys.exit( message )

        ## -- archive original ------------------
        source_file_path = f'{self.PATH_TO_SOURCE_DIRECTORY}/{new_file_name}'
        datetime_stamp = arcvr.make_datetime_stamp( datetime.datetime.now() ); assert type(datetime_stamp) == str
        destination_dir_path = self.PATH_TO_ARCHIVED_ORIGINALS_DIRECTORY
        ( archived_original_filepath, err ) = arcvr.copy_original_to_archives( source_file_path, datetime_stamp, destination_dir_path )
        if err:
            raise Exception( f'Problem archiving original, ``{err}``' )

        ## -- load file -------------------------
        ( source_file_contents, err ) = prsr.load_file( archived_original_filepath )
        if err:
            raise Exception( f'Problem loading source-file, ``{err}``' )

        ## -- get list of requests from file ----
        ( items, err ) = prsr.make_item_list( source_file_contents )
        if err:
            raise Exception( f'Problem creating items_list, ``{err}``' )

        ## -- process items ---------------------
        gfa_items = []
        for item in items:
            ( item_id, err01 ) = prsr.parse_item_id( item )
            ( item_title, err02 ) = prsr.parse_item_title( item )
            ( item_barcode, err03 ) = prsr.parse_item_barcode( item )
            ( patron_name, err04 ) = prsr.parse_patron_name( item )
            ( patron_barcode, err05 ) = prsr.parse_patron_barcode( item )
            ( patron_note, err06 ) = prsr.parse_patron_note( item )
            ( parsed_pickup_library, err07 ) = prsr.parse_pickup_library( item )
            ( parsed_library_code, err08 ) = prsr.parse_library_code( item )
            ( gfa_entry, err09 ) = prsr.prepare_gfa_entry(
                item_id, item_title, item_barcode, patron_name, patron_barcode, patron_note, parsed_pickup_library, parsed_library_code )
            # if err:
            for err in [ err01, err02, err03, err04, err05, err06, err07, err08, err09 ]:
                if err:
                    message = f'Problem preparing data; see logs for more info; quitting'
                    log.error( message )
                    ## TODO: email admin, or set cron to do this.
                    raise Exception( message )
            gfa_items.append( gfa_entry )

        ## -- stringify gfa data ----------------
        ( stringified_data, err ) = arcvr.stringify_gfa_data( gfa_items )

        ## -- archive parsed-data ---------------
        destination_dir_path = self.PATH_TO_ARCHIVES_PARSED_DIRECTORY
        ( success, err ) = arcvr.save_parsed_to_archives( stringified_data, datetime_stamp, destination_dir_path )
        if err:
            raise Exception( f'Problem archiving parsed-data, ``{err}``' )
        if success == False:
            raise Exception( f'Problem archiving parsed_data; see logs' )

        ## -- determine count -------------------
        count = len( gfa_items )

        ## -- send gfa count & data files -------
        err = arcvr.send_gfa_count_file( count, datetime_stamp, self.PATH_TO_GFA_COUNT_DIRECTORY )
        if err:
            raise Exception( f'Problem sending gfa count-file, ``{err}``' )
        err = arcvr.send_gfa_data_file( stringified_data, datetime_stamp, self.PATH_TO_GFA_DATA_DIRECTORY )
        if err:
            raise Exception( f'Problem sending gfa data-file, ``{err}``' )

        ## -- delete original -------------------
        log.debug( f'self.DEV_MODE, ``{self.DEV_MODE}``' )
        if self.DEV_MODE == True:
            pass
        else:
            err = arcvr.delete_original( source_file_path )
            if err:
                raise Exception( f'Problem deleting original file, ``{err}``' )
        log.debug( '-- processing complete --' )

    ## end class Controller()


    # def check_paths( self ):
    #     """ Ensures all paths are correct.
    #         Called by process_requests() """
    #     check_a = utility_code.checkDirectoryExistence( self.PATH_TO_SOURCE_FILE_DIRECTORY )
    #     check_b = utility_code.checkDirectoryExistence( self.PATH_TO_ARCHIVES_ORIGINALS_DIRECTORY )
    #     check_c = utility_code.checkDirectoryExistence( self.PATH_TO_ARCHIVES_PARSED_DIRECTORY )
    #     check_d = utility_code.checkDirectoryExistence( self.PATH_TO_PARSED_ANNEX_DATA_DIRECTORY )
    #     check_e = utility_code.checkDirectoryExistence( self.PATH_TO_PARSED_ANNEX_COUNT_DIRECTORY )
    #     if check_a == 'exists' and check_b == 'exists' and check_c == 'exists' and check_d == 'exists' and check_e == 'exists':
    #       log.debug( 'path check passed' )
    #     else:
    #       message='path check failed; quitting'
    #       log.error( message )
    #       sys.exit( message )
    #     return

    # def file_check( self ):
    #     """ Sees if there is a file waiting; returns unicode-text if so.
    #         Called by process_requests() """
    #     try:
    #       file_handler = open( self.PATH_TO_SOURCE_FILE )
    #       log.info( 'annex requests found' )
    #     except Exception as e:
    #       message = 'no annex requests found; quitting\n\n'
    #       log.info( message )
    #       sys.exit( message )
    #     utf8_data = file_handler.read()
    #     assert type(utf8_data) == str, type(utf8_data)
    #     data = utf8_data.decode( 'utf-8' )
    #     return data

    # def copy_original_to_archives( self, date_stamp ):
    #     """ Copies original file to archives.
    #         Called by process_requests() """
    #     original_archive_file_path = '%s/REQ-ORIG_%s.dat' % ( self.PATH_TO_ARCHIVES_ORIGINALS_DIRECTORY, date_stamp )   # i.e. '/path/REQ-ORIG_2005-05-19T15/08/09.dat'
    #     try:
    #       shutil.copyfile( self.PATH_TO_SOURCE_FILE, original_archive_file_path )
    #       os.chmod( original_archive_file_path, 0o640 )  # owner, RW-; group, R--; other, ---
    #       log.debug( 'source file copied to original archives' )
    #     except Exception as e:
    #       message = 'copy of original file from "%s" to "%s" unsuccessful; exception is: %s' % ( self.PATH_TO_SOURCE_FILE, original_archive_file_path, e )
    #       log.error( message )
    #       sys.exit( message )
    #     copy_check = utility_code.checkFileExistence( original_archive_file_path )
    #     if copy_check == 'exists':
    #       log.info( 'original file copied to: %s' % original_archive_file_path )
    #     else:
    #       message = 'copy of original file from "%s" to "%s" unsuccessful; exception is: %s' % ( self.PATH_TO_SOURCE_FILE, original_archive_file_path, copy_check )
    #       log.error( message )
    #       sys.exit( message )
    #     return

    # def post_original_to_db( self, data, date_stamp ):
    #     """ Posts original file to annex-processor-viewer.
    #         Called by process_requests() """
    #     post_result = 'init'
    #     try:
    #         post_result = utility_code.postFileData( identifier=date_stamp, file_data=data, update_type='original_file' )
    #         log.info( 'original_file post_result, `%s`' % post_result )
    #     except Exception as e:
    #         log.error( 'original_file post_result exception is: %s' % e )
    #     if not post_result == 'success':
    #         log.debug( 'post_result not "success"; but continuing' )
    #     return

    # def make_pageslips_list( self, data ):
    #     """ Returns list of pageslips, where each pageslip is a list of lines.
    #         Called by process_requests() """
    #     item_list_maker = utility_code.ItemListMaker()
    #     item_list = item_list_maker.make_item_list( data )
    #     log.info( 'item_list prepared' )
    #     return item_list

    # def make_gaf_list( self, pageslips_list ):
    #     """ Converts list of pageslips into list of items for gfa software.
    #         TODO: call parser.process_all() here instead of individual elements.
    #         Called by process_requests() """
    #     new_item_list = []
    #     pageslip_count = 0
    #     for item in pageslips_list:
    #         try:
    #             parser = utility_code.Parser()
    #             record_number = utility_code.parseRecordNumber(item)
    #             book_barcode = parser.parse_bookbarcode( item )
    #             las_delivery_stop = utility_code.parseJosiahPickupAtCode(item)
    #             las_customer_code = parser.parse_josiah_location_code( item )
    #             patron_name = utility_code.parsePatronName(item)
    #             patron_barcode = utility_code.parsePatronBarcode(item)
    #             title = parser.parse_title( item )
    #             las_date = utility_code.prepareLasDate()
    #             note = parser.parse_note( item )
    #             full_line = '''"%s","%s","%s","%s","%s","%s","%s","%s","%s"''' % ( record_number, book_barcode, las_delivery_stop, las_customer_code, patron_name, patron_barcode, title, las_date, note )
    #             new_item_list.append( full_line )
    #             pageslip_count = pageslip_count + 1
    #             if pageslip_count % 10 == 0:
    #                 log.debug( '`%s` pageslips processed so far...' % pageslip_count )
    #         except Exception as e:
    #             subject = 'annex process pageslips problem'
    #             message = 'iterating through item_list; problem with item "%s"; exception is: %s' % ( item, unicode(repr(e)) )
    #             logger.error( message )
    #             m = Mailer( subject, message )
    #             m.send_email()
    #     log.info( '`%s` items parsed' % pageslip_count )
    #     log.debug( 'new_item_list, ```%s```' % pprint.pformat(new_item_list) )
    #     return new_item_list

    # def post_parsed_to_db( self, gaf_list, date_stamp ):
    #     """ Posts parsed data to annex-processor-viewer.
    #         Called by process_requests() """
    #     unicode_string_data = ''
    #     count = 0
    #     for line in gaf_list:
    #         if count == 0:
    #             unicode_string_data = line
    #         else:
    #             unicode_string_data = unicode_string_data + '\n' + line
    #         count = count + 1
    #     unicode_string_data = unicode_string_data + '\n'   # the final newline is likely not necessary but unixy, and exists in old system
    #     post_result = 'init'
    #     try:
    #         post_result = utility_code.postFileData( identifier=date_stamp, file_data=unicode_string_data, update_type='parsed_file' )
    #         log.info( 'parsed_file post_result is: %s' % post_result )
    #     except Exception as e:
    #         log.error( 'parsed_file post_result exception is: %s' % unicode(repr(e)) )
    #     if not post_result == 'success':
    #         log.debug( 'post_result of parsed file not "success"; but continuing' )
    #     return unicode_string_data

    # def save_parsed_to_archives( self, date_stamp, unicode_parsed_data ):
    #     """ Copies parsed file to archives.
    #         Called by process_requests() """
    #     try:
    #       self.parsed_file_name = 'REQ-PARSED_%s.dat' % date_stamp
    #       self.parsed_file_archive_path = '%s/%s' % ( self.PATH_TO_ARCHIVES_PARSED_DIRECTORY, self.parsed_file_name )
    #       f = open( self.parsed_file_archive_path, 'w' )
    #       f.write( unicode_parsed_data.encode('utf-8') )
    #       f.close()
    #       copy_check = utility_code.checkFileExistence( self.parsed_file_archive_path )
    #       os.chmod( self.parsed_file_archive_path, 0o640 )   # rw-/r--/---
    #       if copy_check == 'exists':
    #         log.info( 'parsed file archived to: %s' % self.parsed_file_archive_path )
    #       else:
    #         message = 'write of parsed file to "%s" unsuccessful' % self.parsed_file_archive_path
    #         log.error( message )
    #         sys.exit( message )
    #     except Exception as e:
    #       message = 'problem on save of parsed file; quitting; exception is: %s' % unicode(repr(e))
    #       log.error( message )
    #       sys.exit( message )
    #     return

    # def determine_count( self, unicode_string, item_list ):
    #     """ Confirms count
    #         Called by process_requests() """
    #     item_list_maker = utility_code.ItemListMaker()
    #     lines = item_list_maker.make_lines( unicode_string )
    #     confirmed_count = utility_code.determineCount( len(item_list), lines )
    #     if confirmed_count == 0:   # if two methods of determining count don't match, zero is returned
    #         message = 'problem on determining count; quitting'
    #         log.error( message )
    #         sys.exit( message )
    #     log.info( 'count confirmed to be: %s' % confirmed_count )
    #     return confirmed_count

    # def save_count_and_data_to_gfa_dirs( self, date_stamp, count, unicode_parsed_data ):
    #     """ Saves count file and data file to destination directories.
    #         Called by process_requests() """
    #     try:
    #         count_file_name = 'REQ-PARSED_%s.cnt' % date_stamp
    #         count_file_las_destination_path = '%s/%s' % ( self.PATH_TO_PARSED_ANNEX_COUNT_DIRECTORY, count_file_name )
    #         f = open( count_file_las_destination_path, 'w' )
    #         count_str = '%s' % count + '\n'
    #         f.write( count_str.encode('utf-8') )
    #         f.close()
    #         try:
    #             os.chmod( count_file_las_destination_path, 0o666 )   # rw-/rw-/rw-
    #         except Exception as e:
    #             log.info( 'could not set file-permissions on count-destination-path; exception, `%s` -- continuing' % unicode(repr(e)) )
    #         log.info( 'count file written to: ```%s```' % count_file_las_destination_path )
    #     except Exception as e:
    #         message = 'problem on save of count file to ```%s```; quitting; exception is: `%s`' % (count_file_las_destination_path, unicode(repr(e)) )
    #         log.error( message )
    #         sys.exit( message )
    #     try:
    #         parsed_file_las_destination_path = '%s/%s' % ( self.PATH_TO_PARSED_ANNEX_DATA_DIRECTORY, self.parsed_file_name )
    #         shutil.copyfile( self.parsed_file_archive_path, parsed_file_las_destination_path )
    #         try:
    #             os.chmod( parsed_file_las_destination_path, 0o666 )   # rw-/rw-/rw-
    #         except Exception as e:
    #             log.info( 'could not set file-permissions on data-destination-path; exception, `%s` -- continuing' % unicode(repr(e)) )
    #         log.info( 'data file written to: ```%s```' % parsed_file_las_destination_path )
    #     except Exception as e:
    #         message = 'problem on save of data file to ```%s```; quitting; exception is: `%s`' % ( parsed_file_las_destination_path, unicode(repr(e)) )
    #         log.error( message )
    #         sys.exit( message )
    #     return

    # def delete_original( self ):
    #     """ Deletes original file.
    #         Called by process_requests() """
    #     try:
    #         os.remove( self.PATH_TO_SOURCE_FILE )
    #         copy_check = utility_code.checkFileExistence( self.PATH_TO_SOURCE_FILE )   # should not exist
    #         if copy_check == 'exists':
    #             message = 'deletion of original file at ```%s``` failed, as determined by copy_check' % self.PATH_TO_SOURCE_FILE
    #             log.error( message )
    #             sys.exit( message )
    #         else:
    #             log.info( 'deletion successful of original file at ```%s```' % self.PATH_TO_SOURCE_FILE )
    #     except Exception as e:
    #         message = 'deletion of original file at ```%s``` failed; exception, `%s`' % ( self.PATH_TO_SOURCE_FILE, unicode(repr(e)) )
    #         log.error( message )
    #         sys.exit( message )
    #     return


if __name__ == '__main__':
    c = Controller()
    c.process_requests()
    log.debug( '__main__ complete' )
