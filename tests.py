import datetime, os, sys, unittest

sys.path.append( os.environ['ANX_ALMA__ENCLOSING_PROJECT_PATH'] )
from parse_alma_annex_requests_code.lib.archiver import Archiver


TEST_DIRS_PATH = os.environ['ANX_ALMA__TEST_DIRS_PATH']


class ArchiverTest( unittest.TestCase ):

    def setUp( self ):
        self.arcvr = Archiver()

    ## -- tests ---------------------------------

    def test_detect_new_file_does_not_exist(self):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_does_not_exist'
        exist_check_result = self.arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( False, exist_check_result )

    def test_detect_new_file_does_exist(self):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_exists'
        exist_check_result = self.arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( True, exist_check_result )

    def test_make_datetime_stamp(self):
        datetime_obj = datetime.datetime(2021, 7, 13, 14, 40, 49 )
        dt_result = self.arcvr.make_datetime_stamp( datetime_obj )
        self.assertEqual( '2021-07-13T14-40-49', dt_result )

    def test_copy_original_to_archives_success(self):
        self.prep_copy_dirs()
        source_file_path = f'{TEST_DIRS_PATH}/new_file_exists/BUL_ANNEX-foo.xml'
        destination_dir_path = f'{TEST_DIRS_PATH}/copy_original_destination_dir/'
        copy_result = self.arcvr.copy_original_to_archives( '2021-07-13T14-40-49' )

    ## -- helpers -------------------------------

    def prep_copy_dirs(self):
        ## -- ensure source-file exists ---------
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
        destination_contents = os.listdir( f'{TEST_DIRS_PATH}/copy_original_destination_dir/' )
        for item_path in destination_contents:
            try:
                os.remove( item_path )
            except:
                pass
        return



if __name__ == '__main__':
  unittest.main()
