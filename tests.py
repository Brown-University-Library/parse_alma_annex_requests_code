import datetime, logging, os, sys, unittest
import bs4

sys.path.append( os.environ['ANX_ALMA__ENCLOSING_PROJECT_PATH'] )
from parse_alma_annex_requests_code.lib.archiver import Archiver
from parse_alma_annex_requests_code.lib.parser import Parser


TEST_DIRS_PATH = os.environ['ANX_ALMA__TEST_DIRS_PATH']


lvl_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
lvl = os.environ['ANX_ALMA__LOG_LEVEL']
logging.basicConfig(
    filename=os.environ['ANX_ALMA__LOG_PATH'],
    level=lvl,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)
log.debug( 'test-logging ready' )


class ArchiverTest( unittest.TestCase ):

    def setUp( self ):
        self.arcvr = Archiver()

    ## -- tests ---------------------------------

    def test_detect_new_file_does_not_exist(self):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_does_not_exist'
        ( new_file_name, err ) = self.arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( '', new_file_name )
        self.assertTrue( err == None )

    def test_detect_new_file_does_exist(self):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_exists'
        ( new_file_name, err ) = self.arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( 'BUL_ANNEX-foo.xml', new_file_name )
        self.assertTrue( err == None )

    def test_make_datetime_stamp(self):
        datetime_obj = datetime.datetime(2021, 7, 13, 14, 40, 49 )
        dt_result = self.arcvr.make_datetime_stamp( datetime_obj )
        self.assertEqual( '2021-07-13T14-40-49', dt_result )

    def test_copy_original_to_archives_success(self):
        self.prep_copy_dirs()
        datetime_stamp = '2021-07-13T14-40-49'
        source_file_path = f'{TEST_DIRS_PATH}/new_file_exists/BUL_ANNEX-foo.xml'
        destination_dir_path = f'{TEST_DIRS_PATH}/copy_original_destination_dir'
        # ( success, err ) = self.arcvr.copy_original_to_archives( source_file_path, destination_dir_path, datetime_stamp )
        ( destination_filepath, err ) = self.arcvr.copy_original_to_archives( source_file_path, datetime_stamp, destination_dir_path,  )
        self.assertEqual( True, 'test_dirs/copy_original_destination_dir/REQ-ALMA-ORIG_2021-07-13T14-40-49.xml' in destination_filepath )
        self.assertTrue( err == None )

    def test_copy_original_to_archives_error(self):
        self.prep_copy_dirs()
        datetime_stamp = 2
        source_file_path = f'{TEST_DIRS_PATH}/new_file_exists/BUL_ANNEX-foo.xml'
        destination_dir_path = f'{TEST_DIRS_PATH}/copy_original_destination_dir'
        ( destination_filepath, err ) = self.arcvr.copy_original_to_archives( source_file_path, destination_dir_path, datetime_stamp )
        self.assertTrue( destination_filepath == '' )
        self.assertEqual( 'AssertionError()', err )

    def test_stringify_gfa_data(self):
        gfa_items = [
            ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1', 'i1' ],
            ['aa2', 'bb2', 'cc2', 'd2', 'e2', 'f2', 'g2', 'h2', 'i2' ],
        ]
        ( stringified_data, err ) = self.arcvr.stringify_gfa_data( gfa_items )
        log.debug( f'stringified_data in test, ``{stringified_data}``' )
        self.assertEqual(
            '''"a1","b1","c1","d1","e1","f1","g1","h1","i1"\n"aa2","bb2","cc2","d2","e2","f2","g2","h2","i2"\n''',
            stringified_data
            )
        self.assertTrue( err == None )

    def test_save_parsed_to_archives(self):
        text = 'foo'
        datetime_stamp = '1960-02-02T08-15-00'
        test_destination_dir = f'{TEST_DIRS_PATH}/save_parsed_destination_dir'
        self.clear_dir( test_destination_dir )
        ( success, err ) = self.arcvr.save_parsed_to_archives( text, datetime_stamp, test_destination_dir  )
        self.assertEqual( True, success )
        self.assertEqual( None, err )

    def test_send_gfa_count_file(self):
        """ Can't test for success cuz files disappear quickly. """
        count = 2
        datetime_stamp = '1960-02-02T08-15-00'
        test_destination_dir = f'{TEST_DIRS_PATH}/test_gfa_output_dir/count_dir'
        self.clear_dir( test_destination_dir )
        err = self.arcvr.send_gfa_count_file( count, datetime_stamp, test_destination_dir  )
        self.assertEqual( None, err )

    def test_send_gfa_data_file(self):
        """ Can't test for success cuz files disappear quickly. """
        text = 'hello world\nhello again\n'
        datetime_stamp = '1960-02-02T08-15-00'
        test_destination_dir = f'{TEST_DIRS_PATH}/test_gfa_output_dir/data_dir'
        self.clear_dir( test_destination_dir )
        err = self.arcvr.send_gfa_data_file( text, datetime_stamp, test_destination_dir  )
        self.assertEqual( None, err )


    ## -- helpers -------------------------------

    def prep_copy_dirs(self):
        ## -- ensure source-file exists ---------
        log.debug( 'starting prep_copy_dirs' )
        source_file = None
        source_contents = os.listdir( f'{TEST_DIRS_PATH}/new_file_exists/' )
        source_file_check = 'failed'
        for item_path in source_contents:
            if item_path.startswith( 'BUL_ANNEX' ):
                source_file_check = 'passed'
                break
        if source_file_check == 'failed':
            shutil.copy2( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml', f'{TEST_DIRS_PATH}/new_file_exists/' )
        ## -- ensure destination-dir is empty ---
        destination_dir_path = f'{TEST_DIRS_PATH}/copy_original_destination_dir'
        log.debug( f'destination_dir_path, ``{destination_dir_path}``' )
        destination_contents = os.listdir( destination_dir_path )
        log.debug( f'destination_contents, ``{destination_contents}``' )
        for item_name in destination_contents:
            full_item_path = f'{TEST_DIRS_PATH}/copy_original_destination_dir/{item_name}'
            log.debug( f'full_item_path found, ``{full_item_path}``' )
            try:
                os.remove( full_item_path )
                log.debug( f'full_item_path successfully deleted, ``{full_item_path}``' )
            except:
                log.exception( 'problem deleting found file' )
                pass
        return

    def clear_dir( self, destination_dir ):
        dir_contents = os.listdir( destination_dir )
        log.debug( f'dir_contents, ``{dir_contents}``' )
        for item in dir_contents:
            if 'keep.txt' in item:
                continue
            item_path = f'{destination_dir}/{item}'
            try:
                os.remove( item_path )
                log.debug( f'item, ``{item_path}`` successfully deleted' )
            except Exception as e:
                log.exception( f'problem deleting found file, ``{item_path}``' )
                pass
        return

    # def clear_dir( self, destination_dir ):
    #     dir_contents = os.listdir( destination_dir )
    #     log.debug( f'dir_contents, ``{dir_contents}``' )
    #     for item in dir_contents:
    #         item_path = f'{destination_dir}/{item}'
    #         try:
    #             os.remove( item_path )
    #             log.debug( f'item, ``{item_path}`` successfully deleted' )
    #         except Exception as e:
    #             log.exception( f'problem deleting found file, ``{item_path}``' )
    #             pass
    #     return

    ## end class ArchiverTest()


class ParserTest( unittest.TestCase ):

    def setUp( self ):
        self.prsr = Parser()

    ## -- tests ---------------------------------

    def test_open_file__success(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        self.assertTrue( len(all_text) > 100 )

    def test_make_item_list(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( items, err ) = self.prsr.make_item_list( all_text )
        self.assertEqual( bs4.element.ResultSet, type(items) )
        self.assertEqual( 5, len(items) )
        self.assertEqual( bs4.element.Tag, type(items[0]) )

    def test_parse_item_id(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( item_id, err ) = self.prsr.parse_item_id( item_list[0] )
        self.assertEqual( '2332679300006966', item_id )
        self.assertEqual( None, err )

    def test_parse_item_title(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( title, err ) = self.prsr.parse_item_title( item_list[0] )
        self.assertEqual( 'Education.', title )
        self.assertEqual( None, err )

    def test_parse_title_no_title(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX_no_title.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( title, err ) = self.prsr.parse_item_title( item_list[0] )
        self.assertEqual( '', title )
        self.assertEqual( None, err )

    def test_parse_item_barcode(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( item_barcode, err ) = self.prsr.parse_item_barcode( item_list[0] )
        self.assertEqual( '31236011508853', item_barcode )
        self.assertEqual( None, err )

    def test_parse_patron_name(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( patron_name, err ) = self.prsr.parse_patron_name( item_list[0] )
        self.assertEqual( 'Ddddd, Bbbbbb', patron_name )
        self.assertEqual( None, err )

    def test_parse_patron_barcode(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( patron_barcode, err ) = self.prsr.parse_patron_barcode( item_list[0] )
        self.assertEqual( '12345678901234', patron_barcode )
        self.assertEqual( None, err )

    def test_parse_patron_note(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( patron_note, err ) = self.prsr.parse_patron_note( item_list[0] )
        self.assertEqual( 'b-test, new-configuration, physical, 2:59pm', patron_note )
        self.assertEqual( None, err )

    def test_parse_pickup_library_physical(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( pickup_library, err ) = self.prsr.parse_pickup_library( item_list[0] )
        self.assertEqual( 'Rockefeller Library', pickup_library )
        self.assertEqual( None, err )

    def test_parse_pickup_library_digital(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( pickup_library, err ) = self.prsr.parse_pickup_library( item_list[1] )
        self.assertEqual( 'John Hay Library', pickup_library )
        self.assertEqual( None, err )

    def test_parse_pickup_library_personal(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( pickup_library, err ) = self.prsr.parse_pickup_library( item_list[2] )
        self.assertEqual( 'PERSONAL_DELIVERY', pickup_library )
        self.assertEqual( None, err )

    def test_parse_library_code(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( library_code, err ) = self.prsr.parse_library_code( item_list[0] )
        self.assertEqual( 'ROCK', library_code )
        self.assertEqual( None, err )

    def test_parse_library_code_personal(self):
        ( all_text, err ) = self.prsr.load_file( f'{TEST_DIRS_PATH}/static_source/BUL_ANNEX-sample.xml' )
        ( item_list, err ) = self.prsr.make_item_list( all_text )
        ( library_code, err ) = self.prsr.parse_library_code( item_list[2] )
        self.assertEqual( '', library_code )  # the 'personal' items have no library-code
        self.assertEqual( None, err )

    def test_prepare_gfa_date(self):
        datetime_obj = datetime.datetime( 1960, 2, 2, 1, 15, 30 )
        self.assertEqual( 'Tue Feb 02 1960', self.prsr.prepare_gfa_datetime(datetime_obj) )

    def test_prepare_gfa_entry__rock(self):
        ## ( item_id, item_title, item_barcode, patron_name, patron_barcode, patron_note, parsed_pickup_library, parsed_library_code )
        ( gfa_entry, err ) = self.prsr.prepare_gfa_entry(
                '2332679300006966', 'Education.', '31236011508853', 'Ddddd, Bbbbbb', '12345678901234', 'b-test, new-configuration, physical-rock, 2:59pm', 'Rockefeller Library', 'ROCK' )
        self.assertEqual( '2332679300006966', gfa_entry[0] )
        self.assertEqual( '31236011508853', gfa_entry[1] )
        self.assertEqual( 'RO', gfa_entry[2] )
        self.assertEqual( 'QS', gfa_entry[3] )
        self.assertEqual( 'Ddddd, Bbbbbb', gfa_entry[4] )
        self.assertEqual( '12345678901234', gfa_entry[5] )
        self.assertEqual( 'Education.', gfa_entry[6] )
        self.assertEqual( datetime.datetime.now().strftime( '%a %b %d %Y' ), gfa_entry[7] )
        self.assertEqual( None, err )

    def test_prepare_gfa_entry__hay(self):
        ## ( item_id, item_title, item_barcode, patron_name, patron_barcode, patron_note, parsed_pickup_library, parsed_library_code )
        ( gfa_entry, err ) = self.prsr.prepare_gfa_entry(
                '23334087800006966', 'Southern medical journal.', '31236070043131', 'Mmmmmmmm, Mmm', '12345678901234', 'b-test, new-configuration, physical-hay, 2:59pm', 'John Hay Library', 'HAY' )
        self.assertEqual( '23334087800006966', gfa_entry[0] )
        self.assertEqual( '31236070043131', gfa_entry[1] )
        self.assertEqual( 'HA', gfa_entry[2] )
        self.assertEqual( 'QH', gfa_entry[3] )
        self.assertEqual( 'Mmmmmmmm, Mmm', gfa_entry[4] )
        self.assertEqual( '12345678901234', gfa_entry[5] )
        self.assertEqual( 'Southern medical journal.', gfa_entry[6] )
        self.assertEqual( datetime.datetime.now().strftime( '%a %b %d %Y' ), gfa_entry[7] )
        self.assertEqual( None, err )

    def test_prepare_gfa_entry__rock_from_personal(self):
        ## ( item_id, item_title, item_barcode, patron_name, patron_barcode, patron_note, parsed_pickup_library, parsed_library_code )
        ( gfa_entry, err ) = self.prsr.prepare_gfa_entry(
                '23334087800006966', 'Southern medical journal.', '31236070043131', 'Mmmmmmmm, Mmm', '12345678901234', 'b-test, new-configuration, physical-hay, 2:59pm', 'John Hay Library', 'HAY' )
        self.assertEqual( 'foo', gfa_entry[0] )
        self.assertEqual( '31236070043131', gfa_entry[1] )
        self.assertEqual( 'HA', gfa_entry[2] )
        self.assertEqual( 'QH', gfa_entry[3] )
        self.assertEqual( 'Mmmmmmmm, Mmm', gfa_entry[4] )
        self.assertEqual( '12345678901234', gfa_entry[5] )
        self.assertEqual( 'Southern medical journal.', gfa_entry[6] )
        self.assertEqual( datetime.datetime.now().strftime( '%a %b %d %Y' ), gfa_entry[7] )
        self.assertEqual( None, err )


    ## end class ParserTest()


if __name__ == '__main__':
  unittest.main()
