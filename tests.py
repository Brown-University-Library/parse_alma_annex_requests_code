import datetime, os, sys, unittest

sys.path.append( os.environ['ANX_ALMA__ENCLOSING_PROJECT_PATH'] )
from parse_alma_annex_requests_code.lib.archiver import Archiver


TEST_DIRS_PATH = os.environ['ANX_ALMA__TEST_DIRS_PATH']


class ArchiverTest( unittest.TestCase ):

    def setUp( self ):
        self.arcvr = Archiver()

    def test_detect_new_file_does_not_exist( self ):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_does_not_exist'
        exist_check_result = self.arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( False, exist_check_result )

    def test_detect_new_file_does_exist( self ):
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_exists'
        exist_check_result = self.arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( True, exist_check_result )

    def test_make_datetime_stamp( self ):
        datetime_obj = datetime.datetime(2021, 7, 13, 14, 40, 49 )
        dt_result = self.arcvr.make_datetime_stamp( datetime_obj )
        self.assertEqual( '2021-07-13T14-40-49', dt_result )


if __name__ == '__main__':
  unittest.main()
