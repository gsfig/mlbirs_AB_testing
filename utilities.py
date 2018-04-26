from os.path import isfile, getsize


def check_file(path):
    """
    checks that file exists and is bigger than 100
    :param path:
    :return: true or false
    """

    if isfile(path):
        if getsize(path) > 100:
            return True
        else:
            print(path + " file smaller than 100")
            return False
    else:
        print(path + " file does not exist")
        return False
