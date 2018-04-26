from os.path import isfile, getsize
import sqlite3


def check_db_file(db_file: str):
    """
    checks existence of sqlite database file
    param: db_file sqlite db file path
    :return: True or False
    """

    if isfile(db_file):
        if getsize(db_file) > 100:
            with open(db_file, 'r', encoding="ISO-8859-1") as f:
                header = f.read(100)
                if header.startswith('SQLite format 3'):
                    # print(str(db_file) + " database detected")
                    return True
                else:
                    print(str(db_file) + " file is not SQLite format 3")
                    return False
        else:
            print(str(db_file) + " file is empty")
            return False
    else:
        print(str(db_file) + " file does not exist")
        return False


def connect_db(db_file) -> sqlite3.Connection:
    """
    file should exist
    :param db_file: name of sqlite3 databse file
    :return: Connection or error in case file doesnt exist
    """
    if check_db_file(db_file):
        db_connection = make_connection(db_file)
        return db_connection
    else:
        raise RuntimeError('check_db_file returned false, db file should exist')


def make_connection(db_name) -> sqlite3.Connection:
    """
    establish connection with non existing sqlite3 file / databse
    :param db_name: name of sqlite3 databse file
    :return: connection
    """
    connection = sqlite3.connect(db_name)
    connection.isolation_level = None  # auto_commit
    connection.row_factory = lambda cursor, row: row[0]
    return connection
