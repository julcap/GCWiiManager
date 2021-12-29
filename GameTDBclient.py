import os
from urllib import request, error, parse


class ErrorFetchingData(Exception):
    pass


class InvalidParameters(Exception):
    pass


def fetch_game_identifiers(language='EN') -> object:
    """
    @param language: EN, JA, FR, DE, ES, IT, NL, PT, ZHTW, ZHCN, KO
    @return:
    """
    url = 'http://www.gametdb.com/wiitdb.txt'
    games_id_dictionary = dict()
    params = {'LANG': language}
    try:
        data = parse.urlencode(params)
        data = data.encode('utf-8')
        result = request.urlopen(url, data)
    # Raise error if there is no connection to the internet.
    except error.URLError as e:
        raise ErrorFetchingData
    for i in result:
        line = i.decode('utf-8')
        id, title = line.rstrip('\r\n').split(' = ')
        games_id_dictionary[id] = title
    return games_id_dictionary


def get_art_work(language=None, identifier=None, cover3D=True, disc=True) -> object:
    """
    Sample url request http://art.gametdb.com/wii/cover/US/S72E01.png
    @param language: String (EN, JA, FR, DE, ES, IT, NL, PT, ZHTW, ZHCN, KO)
    @param identifier: String (e.g. S72E01)
    @param cover3D: Boolean
    @param disc: Boolean
    """
    disc_path = os.path.join(os.getcwd(), 'images', 'disc')
    cover3_d_path = os.path.join(os.getcwd(), 'images', 'cover3D')
    art_url = 'http://art.gametdb.com/wii'

    if language == None or identifier == None:
        raise InvalidParameters
    else:
        try:
            status = 0
            if disc:
                output_dir = os.path.join(disc_path, language)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, identifier + '.png')
                if not os.path.exists(output_file):
                    request.urlretrieve(art_url + '/disc/' + language + '/' + identifier + '.png', output_file)
                status = 1
            if cover3D:
                output_dir = os.path.join(cover3_d_path, language)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, identifier + '.png')
                if not os.path.exists(output_file):
                    request.urlretrieve(art_url + '/cover3D/' + language + '/' + identifier + '.png',
                                        output_file)
                status = 1
            return status
        # Raise error if there is no connection to the internet.
        except error.URLError as e:
            raise ErrorFetchingData
