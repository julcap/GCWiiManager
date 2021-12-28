import unittest

import GCWiiManager
from mock import patch


class GCWiiManagerTests(unittest.TestCase):

    def test_get_output_file_absolute_path_WBFS(self):
        inputFile = '/home/jca/games/game name.iso'
        destination = '/home/jca/destination'
        folderName = 'Game name [ABCDEF]'
        fileExtension = 'WBFS'
        gameCode = 'ABCDEF'
        multidisc = False

        result = GCWiiManager.get_output_file_absolute_path(inputFile, destination, folderName, fileExtension,
                                                            gameCode,
                                                            multidisc)
        self.assertEqual('/home/jca/destination/Game name [ABCDEF]/ABCDEF.wbfs', result)

    def test_get_output_file_absolute_path_ISO(self):
        inputFile = '/home/jca/games/game name.iso'
        destination = '/home/jca/destination'
        folderName = 'Game name [ABCDEF]'
        fileExtension = 'ISO'
        gameCode = 'ABCDEF'
        multidisc = False

        result = GCWiiManager.get_output_file_absolute_path(inputFile, destination, folderName, fileExtension, gameCode,
                                                            multidisc)
        self.assertEqual('/home/jca/destination/Game name [ABCDEF]/game.iso', result)

    @patch('GCWiiManager.get_disc_number')
    def test_get_output_file_absolute_path_ISO_Multidisk_Disc_1(self, mock_method):
        mock_method.return_value = 1
        inputFile = '/home/jca/games/game name.iso'
        destination = '/home/jca/destination'
        folderName = 'Game name [ABCDEF]'
        fileExtension = 'ISO'
        gameCode = 'ABCDEF'
        multidisc = True

        result = GCWiiManager.get_output_file_absolute_path(inputFile, destination, folderName, fileExtension, gameCode,
                                                            multidisc)
        self.assertEqual('/home/jca/destination/Game name [ABCDEF]/game.iso', result)

    @patch('GCWiiManager.get_disc_number')
    def test_get_output_file_absolute_path_ISO_Multidisk_Disc_2(self, mock_method):
        mock_method.return_value = 2
        inputFile = '/home/jca/games/game name.iso'
        destination = '/home/jca/destination'
        folderName = 'Game name [ABCDEF]'
        fileExtension = 'ISO'
        gameCode = 'ABCDEF'
        multidisc = True

        result = GCWiiManager.get_output_file_absolute_path(inputFile, destination, folderName, fileExtension, gameCode,
                                                            multidisc)
        self.assertEqual('/home/jca/destination/Game name [ABCDEF]/disc2.iso', result)

    def test_get_destination_normalized_folder_name(self):
        result = GCWiiManager.get_destination_normalized_folder_name("Foo 2: The legend's - really?!", 'ABCDEF')
        self.assertEqual('Foo 2 The legend\'s - really?! [ABCDEF]', result)
        result = GCWiiManager.get_destination_normalized_folder_name("#%&{}\<>*?/ $!'\":@+`|=", 'ABCDEF')
        self.assertEqual('? !\' [ABCDEF]', result)


if __name__ == '__main__':
    unittest.main()
