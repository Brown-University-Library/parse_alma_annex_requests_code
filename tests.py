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


class ArchiverTest( unittest.TestCase ):

    def setUp( self ):
        self.arcvr = Archiver()

    ## -- tests ---------------------------------

    def test_detect_new_file_does_not_exist(self):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_does_not_exist'
        ( exists, err ) = self.arcvr.check_for_new_file( target_dir_path )
        self.assertTrue( exists == False )
        self.assertTrue( err == None )

    def test_detect_new_file_does_exist(self):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_exists'
        ( exists, err ) = self.arcvr.check_for_new_file( target_dir_path )
        self.assertTrue( exists == True )
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
        ( success, err ) = self.arcvr.copy_original_to_archives( source_file_path, destination_dir_path, datetime_stamp )
        self.assertTrue( success == True )
        self.assertTrue( err == None )
        self.assertTrue( 'BUL_ANNEX-foo.xml' in self.arcvr.destination_filepath )
        self.assertTrue( datetime_stamp in self.arcvr.destination_filepath )

    def test_copy_original_to_archives_error(self):
        self.prep_copy_dirs()
        datetime_stamp = 2
        source_file_path = f'{TEST_DIRS_PATH}/new_file_exists/BUL_ANNEX-foo.xml'
        destination_dir_path = f'{TEST_DIRS_PATH}/copy_original_destination_dir'
        ( success, err ) = self.arcvr.copy_original_to_archives( source_file_path, destination_dir_path, datetime_stamp )
        self.assertTrue( success == False )
        self.assertEqual( 'AssertionError()', err )

    # def test_copy_original_to_archives_success(self):
    #     self.prep_copy_dirs()
    #     datetime_stamp = '2021-07-13T14-40-49'
    #     source_file_path = f'{TEST_DIRS_PATH}/new_file_exists/BUL_ANNEX-foo.xml'
    #     destination_dir_path = f'{TEST_DIRS_PATH}/copy_original_destination_dir'
    #     err = self.arcvr.copy_original_to_archives( source_file_path, destination_dir_path, datetime_stamp )
    #     self.assertEqual( None, err )
    #     self.assertTrue( 'BUL_ANNEX-foo.xml' in self.arcvr.destination_filepath )
    #     self.assertTrue( datetime_stamp in self.arcvr.destination_filepath )

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

    ## -- helpers -------------------------------

    ## end class ParserTest()


if __name__ == '__main__':
  unittest.main()
