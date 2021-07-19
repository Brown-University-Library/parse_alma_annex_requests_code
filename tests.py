import os, sys, unittest

sys.path.append( os.environ['ANX_ALMA__ENCLOSING_PROJECT_PATH'] )
from parse_alma_annex_requests_code.lib.archiver import Archiver


TEST_DIRS_PATH = os.environ['ANX_ALMA__TEST_DIRS_PATH']


class ArchiverTest( unittest.TestCase ):

    def test_detect_new_file_does_not_exist( self ):
        arcvr = Archiver()
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_does_not_exist'
        exist_check_result = arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( False, exist_check_result )

    def test_detect_new_file_does_exist( self ):
        arcvr = Archiver()
        target_dir_path = f'{TEST_DIRS_PATH}/new_file_exists'
        exist_check_result = arcvr.check_for_new_file( target_dir_path )
        self.assertEqual( True, exist_check_result )

if __name__ == '__main__':
  unittest.main()
