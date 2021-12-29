# A Gamecube/Wii backup manager
#
# Julian Capilla
# lyhan_jr@hotmail.com
import os
import re
import ast
import shutil
import filecmp

import GameTDBclient
from GWdb import GWdb

game_tdb_file = 'wiitdb.txt'
manually_maintained_file = 'AdditionalIdentifiers.txt'


def get_game_region(code):
    """
    A 	41 	All regions. System channels like the Mii channel use it.
    B 	42 	Used by some WiiWare / Virtual Console titles.
    D 	44 	German-speaking regions. Only if separate versions exist, e.g. Zelda: A Link to the Past
    E 	45 	USA and other NTSC regions except Japan
    F 	46 	French-speaking regions. Only if separate versions exist, e.g. Zelda: A Link to the Past.
    I 	49 	Italian-speaking regions. Only if separate versions exist, e.g. Pokemon Snap. Unofficially used by The Homebrew Channel 1.0.5 and newer.
    J 	4A 	Japan
    K 	4B 	Korea. Unofficially used by DVDX 2.0.
    L 	4C 	Japanese Import to Europe, Australia and other PAL regions
    M 	4D 	American Import to Europe, Australia and other PAL regions
    N 	4E 	Japanese Import to USA and other NTSC regions
    P 	50 	Europe, Australia and other PAL regions
    Q 	51 	Korea with Japanese language.
    S 	53 	Spanish-speaking regions. Only if separate versions exist, e.g. Pokemon Snap
    T 	54 	Korea with English language.
    U 	55 	Used by some WiiWare / Virtual Console titles.
    X 	58 	Used by some WiiWare / Virtual Console titles. Also used by DVDX 1.0 and The Homebrew Channel versions 1.0.4 and earlier.
    """
    region = {'A': '',
              'B': '',
              'D': 'DE',
              'E': 'US',
              'F': 'FR',
              'I': 'IT',
              'J': 'JA',
              'K': 'KO',
              'L': '',
              'M': '',
              'N': '',
              'P': '',
              'Q': '',
              'S': 'ES',
              'T': '',
              'U': '',
              'X': ''
              }
    if region.get(list(code)[3]):
        return region.get(list(code)[3])
    else:
        return 'EN'


def get_game_identifiers():
    try:
        with open(game_tdb_file, 'r') as file:
            game_tdb_data = ast.literal_eval(file.read())
    except FileNotFoundError:
        game_tdb_data = refresh_game_tdb_identifiers()
    with open(manually_maintained_file, 'r') as file:
        manually_maintained_data = ast.literal_eval(file.read())
    game_tdb_data.update(manually_maintained_data)
    return game_tdb_data


def get_sorted_game_titles(game_collection):
    """
    Data to pass to the QlistView table
    :param game_collection:
    :return:
    """
    result = []
    for identifier in game_collection:
        result.append(game_collection[identifier]["title"])
    result.sort()
    return result


def refresh_game_tdb_identifiers():
    game_tdb_data = GameTDBclient.fetch_game_identifiers()
    with open(game_tdb_file, 'w') as file:
        file.write(str(game_tdb_data))
    return game_tdb_data


# Check supported file extensions
def is_file_extension_supported(filename):
    """ @filename: absolute path to file """
    for extension in ('ISO', 'WBFS'):
        if filename.lower().endswith(extension.lower()):
            return True
    return False


def get_bite_chunk(file, size):
    f = open(file, 'rb')
    data = f.read(size)
    f.close()
    return data


# Wii games store the identifier at position (512, 518)
def is_valid_wii_identifier_location(location):
    return location == (512, 518)


# GameCube games store the identifier at position (0, 6).
def is_valid_gc_identifier_location(location):
    return location == (0, 6)


def get_game_identifier(file):
    code = re.search(b'[A-Z0-9]{6}', get_bite_chunk(file, 1024))
    if code:
        # The string is always in same location for Wii and GameCube identifiers
        if is_valid_wii_identifier_location(code.span()) or is_valid_gc_identifier_location(code.span()):
            return code.group(0).decode('ascii')
        else:
            return False
    else:
        return False


def get_disc_number(file):
    data = get_bite_chunk(file, 1024)
    match = re.search(b'[A-Z0-9]{6}', data)
    return int(data[match.span()[1]]) + 1


def find_supported_files(path):
    """@path: directory where to search"""
    files = []
    directories = []
    for item in os.listdir(path):
        file = os.path.join(path, item)
        if os.path.isdir(file):
            directories.append(item)
        if os.path.isfile(file) and is_file_extension_supported(file):
            if get_game_identifier(file):
                files.append(file)
    for directory in directories:
        directory = os.path.join(path, directory)
        for file in os.listdir(directory):
            file = os.path.join(directory, file)
            if os.path.isfile(file) and is_file_extension_supported(file):
                if get_game_identifier(file):
                    files.append(file)
    if files:
        return files
    else:
        return 0


def copy_file(source_file, destination_file):
    if os.path.exists(destination_file) and filecmp.cmp(source_file, destination_file, shallow=True):
        return
    shutil.copy2(source_file, destination_file)


def generate_game_collection(full_path_file_list=[]):
    """
    Return a game collection
    {"AGCDEF": { "title": "Game title", "files": ["/abs/olute/path.iso"], "extension": "ISO" },"GHIJK":{ ... } }
    """
    if not full_path_file_list:
        return {'0000': {'title': 'No Wii or GameCube game was found'}}
    game_collection = {}
    for file in full_path_file_list:
        identifier = get_game_identifier(file)
        if identifier not in game_collection.keys():
            game_collection[identifier] = {}
        if "files" not in game_collection[identifier].keys():
            game_collection[identifier]["files"] = file
            db = GWdb()
            game_collection[identifier]["title"] = db.select('gameTitles', '*', {'code': identifier})[0][2]
            game_collection[identifier]["extension"] = os.path.splitext(file)[1].upper()
        elif game_collection[identifier]["files"] != file:
            # Assuming there will not be more than 2 discs
            game_collection[identifier]["files"] = [game_collection[identifier]["files"], file]
    return game_collection


def refresh_db_source_table(full_path_file_list, list_name):
    """
    Clear table for old items and update with new items
    :param full_path_file_list:
    :param list_name:
    :return:
    """
    # flushTable('gamesFound',list_name)
    db = GWdb()
    db.delete(tableName='gamesFound', listName=list_name)
    if full_path_file_list:
        for file in full_path_file_list:
            code = get_game_identifier(file)
            extension = (os.path.splitext(file))[1].lstrip('.').upper()
            # gamesFoundInsert(code,file,extension,listName)
            db.insert('gamesFound', ('code', 'path', 'fileType', 'listName'),
                      (code, file, extension, 'source'))


def get_output_file_absolute_path(input_file, destination, folder_name, file_extension, game_identifier, is_multi_disc):
    file_name = ''
    if file_extension == 'ISO':
        if is_multi_disc:
            disc = get_disc_number(input_file)
            if disc == 1:
                file_name = 'game'
            elif disc == 2:
                file_name = 'disc2'
        else:
            file_name = 'game'
    elif file_extension == 'WBFS':
        file_name = game_identifier
    absolute_path = os.path.join(destination, folder_name, file_name + '.' + file_extension.lower())
    print("Input:\t\t'{}'\nDestination:\t'{}'\nMulti disc:\t'{}'\n".format(input_file, absolute_path, is_multi_disc))
    return absolute_path


def create_destination_folder(absolute_path):
    path = os.path.dirname(absolute_path)
    if not os.path.exists(path):
        os.mkdir(path)


def get_destination_normalized_folder_name(game_title, identifier):
    name = re.findall('[A-Za-z0-9 \'\-!?\(\)\.é]', game_title)
    name = ''.join(name)
    return name + " [" + identifier + "]"


def quit():
    db = GWdb()
    db.close()
