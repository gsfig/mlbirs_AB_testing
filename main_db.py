import db_utilities
import rdflib
import json
import sqlite3


def configuration(config):
    """
    main dababase configuration
    :param config: config.ini
    :return: connection
    """

    db_name = config.get('MainDB', 'db_file')

    if not db_utilities.check_db_file(db_name):
        owl_file = config.get('Files', 'rdf_file')
        hierarchy_level = int(config.get('Parents', 'level'))
        prefix_to_remove = config.get('Predicates', 'subject_to_remove')
        predicates = json.loads(config.get("Predicates", "to_extract"))
        relation = config.get('DISHIN', 'relation2')

        setup_db(db_name, owl_file, hierarchy_level, predicates, prefix_to_remove,relation)

    return db_utilities.connect_db(db_name)


def setup_db(db_name, owl_file, hierarchy_level, predicates, prefix_to_remove, relation):
    """
    database configuration
    :param db_name: database name
    :param owl_file: owl file path
    :param hierarchy_level: number of levels to go up the owl tree
    :param predicates: list of owl predicates
    :param prefix_to_remove: owl prefix
    :param relation: owl relation
    """

    connection = db_utilities.make_connection(db_name)

    print("setting up database, could take a while ...")

    create_tables(predicates, connection, hierarchy_level)

    populate_db(connection, owl_file, prefix_to_remove, predicates, relation)

    insert_parents(connection, hierarchy_level)

    connection.commit()
    connection.close()


def populate_db(connection, owl_file, prefix_to_remove, predicates: list, relation):
    """
    Insert rows in database
    :param connection: database connection
    :param owl_file: owl file path
    :param prefix_to_remove: owl prefix
    :param predicates: prefered_name, synonym, ...
    :param relation: is_a OR subClass_of
    """
    print("reading owl file, could take a while")
    r = str(relation).replace(prefix_to_remove, '')
    relations = list(predicates)
    relations.append(r) # is_a + prefered name ...

    g = rdflib.Graph()
    g.load(owl_file)
    print("finish load rdflib")

    for subject, predicate, obj in g:
        p = str(predicate).replace(prefix_to_remove, '')
        if p in relations:
            s = str(subject).replace(prefix_to_remove, '')
            o = str(obj).replace(prefix_to_remove, '')

            # print("s: " + s + " p: " + p + " o: " + o)

            # insert entity
            rows = connection.execute('''  
                                INSERT OR IGNORE INTO entity (owl_id) VALUES (?)
                             ''', (s,))

            rows = connection.execute('SELECT id FROM entity WHERE owl_id = ?', (s,)).fetchall()

            # print(str(rows))
            entry1 = rows[0]

            if p in predicates: # prefered_name, synonym, obsolete ...

                count1 = connection.execute(''' SELECT COUNT(*) FROM '%s' ''' % p).fetchall()

                rows = connection.execute('''  
                                        INSERT OR IGNORE INTO '%s' (description, fkentity) VALUES (?,?)
                                     ''' % p, (o, entry1,)).fetchall()
                # print("p in predicates, " + "s: " + s + " p:" + p + " o:" + o + " entry1:" + str(entry1))
                # print(rows)

                count2 = connection.execute(''' SELECT COUNT(*) FROM '%s' ''' % p).fetchall()

                if int(count2[0]) <= int(count1[0]):
                    print("s: " + s + " p: " + p + " o: " + o + ", fkentity_subject: " + entry1)

            elif p == r:
                rows = connection.execute('''  
                                            INSERT OR IGNORE INTO entity (owl_id) VALUES (?)
                                         ''', (o,))

                rows = connection.execute('SELECT id FROM entity WHERE owl_id = ?', (o,)).fetchall()
                parent = rows[0]

                rows = connection.execute('''  
                                INSERT OR IGNORE INTO parent_1 (entity_child, entity_parent) VALUES (?,?)
                             ''', (entry1, parent,))

            else:
                print("else, " + "s: " + s + " p: " + p + " o: " + o + ", fkentity_subject: " + entry1)

            connection.commit()
    print("end populate DB")


def insert_parents(connection, hierarchy_level):
    """
    Insert owl parents into database
    :param connection: database sqlite3 connection
    :param hierarchy_level: number of levels to go up the owl tree
    """

    print('insert parents')

    connection.row_factory = sqlite3.Row

    cursor_child = connection.cursor()
    cursor_parent = connection.cursor()
    cursor_new = connection.cursor()

    level_child = 1  # level 1 already inserted

    parent_1_table = 'parent_' + str(level_child)

    # 1. for each child
    for row in cursor_child.execute(''' SELECT * FROM '%s' ''' % parent_1_table):
        level_parent = 2
        child = row[1]
        parent_1 = row[2]

        while level_parent <= hierarchy_level:
            parent_table = 'parent_' + str(level_parent)


            # 2. get parent2
            rows = cursor_parent.execute(''' SELECT * FROM '%s' WHERE entity_child =? ''' % parent_1_table,
                                         (parent_1,)).fetchall()
            # print(str(type(rows)) + ' ' + str(rows))
            alert = 0
            for r in rows:
                # print(r[0], r[1], r[2])
                alert = alert + 1
                if alert > 1:
                    raise RuntimeError('too many rows')

                parent_2 = r[2]

            if not parent_2:
                print("no parent_2, child: " + str(child) + " parent_1: " + str(parent_1))

            # 3. insert child + parent2
            cursor_new.execute(''' INSERT INTO '%s' (entity_child, entity_parent) VALUES (?,?)''' % parent_table, (child, parent_2,))

            parent_1 = parent_2

            level_parent = level_parent + 1

    cursor_child.close()
    cursor_parent.close()
    cursor_new.close()

    print('end insert parents')


def create_tables(predicate_list, connection, hierarchy_level):
    """
    Create database tables
    :param predicate_list: prefered_name, synonym, ...
    :param connection: database sqlite3 connection
    :param hierarchy_level: number of levels to go up the owl tree
    """

    print("create tables main_db")

    connection.execute('''
                          DROP TABLE IF EXISTS entity
                          ''')

    connection.execute('''
                              CREATE TABLE entity (
                              id     INTEGER PRIMARY KEY AUTOINCREMENT,
                              owl_id   VARCHAR(10) UNIQUE
                              )''')

    for tag in predicate_list:
        connection.execute('''
                      DROP TABLE IF EXISTS '%s'
                      ''' % tag)
        connection.execute('''
                      CREATE TABLE '%s' (
                      id     INTEGER PRIMARY KEY AUTOINCREMENT,
                      description   VARCHAR(100),
                      fkentity   INTEGER,
                      FOREIGN KEY(fkentity) REFERENCES entity(id)
                      )
                      ''' % tag)

    parent = hierarchy_level
    while parent > 0:
        table_name = 'parent_' + str(parent)
        connection.execute('''
                              DROP TABLE IF EXISTS '%s'
                              ''' % table_name)

        connection.execute('''
                              CREATE TABLE '%s' (
                              id     INTEGER PRIMARY KEY AUTOINCREMENT,
                              entity_child   VARCHAR(20),
                              entity_parent   VARCHAR(20),
                              FOREIGN KEY(entity_child) REFERENCES entity(id),
                              FOREIGN KEY(entity_parent) REFERENCES entity(id)
                              )
                              ''' % table_name)
        parent = parent - 1
    print('end main db creation')
    connection.commit()


def get_owl_id(config, entity_names: list) -> dict:
    """
    Retrieve corresponding owl ids for each name
    :param config: config.ini
    :param entity_names: owl names
    :return: dict { owl_name: [owl ids]}
    """

    tables_to_search = json.loads(config.get("Predicates", "to_extract"))

    db_name = config.get('MainDB', 'db_file')
    connection = db_utilities.connect_db(db_name)

    entity_ids = dict()

    for entity in entity_names:
        entity = entity.lower()
        owl_ids = list()

        for table in tables_to_search:
            rows = connection.execute(''' SELECT fkentity FROM '%s' WHERE description =? ''' % table,
                                         (entity,)).fetchall()

            for row in rows:

                owl = connection.execute(''' SELECT owl_id FROM '%s' WHERE id =? ''' % 'entity',
                                   (row,)).fetchall()

                # print("entity: " + str(entity) + " fk: " + str(row) + " owl_id: " + str(owl))
                for o in owl:
                    owl_ids.append(o)
        entity_ids[entity] = owl_ids

    connection.close()

    return entity_ids


def get_internal_ids(connection, tables_to_search, entity) -> list:
    """
    get db internal ids from description
    :param connection: database connection
    :param tables_to_search: which tables to include in retrieval
    :param entity: name to search for
    :return: list of database ids for this entity
    """

    internal_ids = list()
    for table in tables_to_search:
        rows = connection.execute(''' SELECT fkentity FROM '%s' WHERE description =? ''' % table,
                                  (entity,)).fetchall()

        for row in rows:
            internal_ids.append(row)

    return internal_ids


def get_parents(config, query_entities) -> dict:
    """

    :param config:
    :param query_entities:
    :return:
    """

    db_name = config.get('MainDB', 'db_file')
    connection = db_utilities.connect_db(db_name)
    table_name = config.get('Parents', 'table_name') + config.get('Parents', 'level')
    tables_to_search = json.loads(config.get("Predicates", "to_extract"))
    query_parents = dict()

    for entity in query_entities:
        entity_ids = get_internal_ids(connection, tables_to_search, entity)
        parent_list = list()

        for entity_id in entity_ids:
            parents = connection.execute(''' SELECT entity_parent FROM '%s' WHERE entity_child =? ''' % table_name,
                                        (entity_id,)).fetchall()

            for p in parents:
                owl_ids = connection.execute(''' SELECT owl_id FROM '%s' WHERE id =? ''' % 'entity',
                                            (p,)).fetchall()
                for owl_id in owl_ids:
                    parent_list.append(owl_id)

                    # print('entity: ' + str(entity) + '; entity_id: ' + str(entity_id) + '; parent: ' + str(p) + '; owl_parent: ' + str(owl_id))

        query_parents[entity] = parent_list
    connection.close()

    return query_parents


def get_parents_owl(config, connection_main, owl_list):
    """
    get parents from owl ids

    :param config: config.ini
    :param owl_list: owl ids
    :param connection_main: sqlite3 connection
    :return: dict {owl_id : [parents_owl_ids}}
    """

    table_name = config.get('Parents', 'table_name') + config.get('Parents', 'level')
    query_parents = dict()

    for entity in owl_list:
        entity_ids = get_internal_ids_owl(connection_main, entity)
        parent_list = list()

        for entity_id in entity_ids:
            parents = connection_main.execute(''' SELECT entity_parent FROM '%s' WHERE entity_child =? ''' % table_name,
                                         (entity_id,)).fetchall()

            for p in parents:
                owl_ids = connection_main.execute(''' SELECT owl_id FROM '%s' WHERE id =? ''' % 'entity',
                                             (p,)).fetchall()
                for owl_id in owl_ids:
                    parent_list.append(owl_id)

                    # print('entity: ' + str(entity) + '; entity_id: ' + str(entity_id) + '; parent: ' + str(p) + '; owl_parent: ' + str(owl_id))

        query_parents[entity] = parent_list

    return query_parents


def get_internal_ids_owl(connection, owl_id):
    """
    get internal ids from owl id
    :param connection: sqlite3 connection
    :param owl_id: owl id to get internal id
    :return: internal database id
    """

    return connection.execute(''' SELECT id FROM entity WHERE owl_id=? ''',(owl_id,)).fetchall()