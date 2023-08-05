import json
import datetime
from mysql.connector import connect, Error


class DatabaseQueryBuilder():
    def __init__(self, *, db_server='localhost', db_user, db_password, db_database, db_port=3306) -> None:
        """
        The function connects to a database and returns a cursor object

        :param db_server: 'localhost'
        :param db_user: 'root'
        :param db_password: 'password'
        :param db_database: 'my_database'
        """
        super().__init__()

        self.table = ''
        self.queryResult = ''
        self.db_database = db_database

        try:
            self.db = connect(host=db_server, user=db_user,
                              password=db_password, database=db_database, port=db_port)

            self.db.autocommit = False
            self.cursor = self.db.cursor()
        except Error as e:
            print(e)

    def reset(self):
        self.table = ''
        self.queryResult = ''
        return self

    def setTable(self, name: str):
        self.table = name
        return self

    def query(self):
        """
        It returns the query result of the table that was passed in
        :return: The queryResult attribute of the class.
        """
        self.queryResult = f'select * from {self.table}'
        return self

    def select(self, fields: list = []):
        """
        It takes a list of fields and builds a query string

        :param fields: list = []
        :type fields: list
        :return: The object itself.
        """
        if fields:
            self.queryResult = 'select '
            for index, field in enumerate(fields):
                if not index == len(fields) - 1:
                    self.queryResult += '{}, '.format(field)
                else:
                    self.queryResult += '{} '.format(field)

            self.queryResult += 'from '
        else:
            self.queryResult = 'select * from'
        return self

    def from_(self, table: str):
        """
        It takes a string as an argument and appends it to the queryResult property of the class

        :param table: str
        :type table: str
        :return: The object itself.
        """
        self.queryResult += f'{table}'
        return self

    def where(self, clausule: str, parameter: str, parameters_dict: dict = {}):
        """
        It takes a string, a string, and a dictionary as parameters, and returns an object

        :param clausule: the column name
        :type clausule: str
        :param parameter: str = 'id'
        :type parameter: str
        :param parameters_dict: {'condition': 'value'}
        :type parameters_dict: dict
        :return: The queryResult string
        """
        try:
            if clausule and parameter:
                if self.queryResult.find('where') == -1:
                    if type(parameter) == str:
                        parameter = f'\'{parameter}\''
                    self.queryResult += f' where {clausule} = {parameter}'
                else:
                    if type(parameter) == str:
                        parameter = f'\'{parameter}\''
                    self.queryResult += f' and {clausule} = {parameter}'
            else:
                self.queryResult += ' where '
                if (len(parameters_dict) == 1):
                    params = list(parameters_dict.items())
                    condition = params[0][0]
                    value = params[0][1]
                    if type(value) == str:
                        value = f'\'{value}\''
                    self.queryResult += f' {condition} {value}'
                else:
                    for index,(condition, value) in enumerate(parameters_dict.items()):
                        if not index == len(parameters_dict) - 1:
                            if type(value) == str:
                                value = f'\'{value}\''
                                self.queryResult += f' {condition} {value} and '
                        else:
                            if type(value) == str:
                                value = f'\'{value}\''
                                self.queryResult += f' {condition} {value} '
            return self
        except Exception as e:
            print(e)

    def results(self, query: str = '') -> list[tuple]:
        """
        It takes a query as an argument, and if the query is empty, it executes the queryResult
        variable, which is a string, and if the query is not empty, it executes the query

        :param query: str = ''
        :type query: str
        :return: A list of tuples.
        """
        try:
            if not query:
                self.cursor.execute(self.queryResult)
            else:
                self.cursor.execute(query)
                self.db.commit()
            return self.cursor.fetchall()
        except Error as e:
            self.db.rollback()
            print(e)

    def toJson(self) -> str:
        """
        It takes the results of a query and returns a json string
        :return: A list of dictionaries.
        """
        try:
            query_fields = f'SELECT COLUMN_NAME \'field\' FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = \'{self.db_database}\' AND TABLE_NAME = \'{self.table}\';'

            self.cursor.execute(query_fields)
            fields : list[tuple] = self.cursor.fetchall() 
            self.db.commit()
            query = self.results()

            listFields = []
            toJson = []
            dictionary = {}

            for field in fields:
                # Get the first position of tuple => 'id','name',
                newField : str = field[0]
                listFields.append(newField)

            for index, qResult in enumerate(query):
                dictionary = {}
                for index, qry in enumerate(qResult):
                    dictionary[listFields[index]] = str(
                        qry) if isinstance(qry, datetime.datetime) else qry
                toJson.append(dictionary)

            # It is used to encode the json strings to utf8
            toJson = json.dumps(toJson, ensure_ascii=False)

            return toJson
        except Error as e:
            self.db.rollback()
            print(e)

    def insert(self, *, table: str = '', fields: list = [], values: list = [], object: object = object):
        """
        It takes a table name, a list of fields, a list of values, and an object as parameters, and
        inserts the values into the table
        
        :param table: The table name
        :type table: str
        :param fields: list = [], values: list = [], object: object = object
        :type fields: list
        :param values: list = [], object: object = object
        :type values: list
        :param object: object = object
        :type object: object
        :return: The last row id
        """
        try:
            if table and fields and values:
                query = self.__generateInsert(table, fields, values)
            elif fields and values:
                query = self.__generateInsert(self.table, fields, values)
            elif object and table:
                for o in [attr for attr in dir(object) if not attr.startswith('__') and not callable(getattr(object, attr))]:
                    if o != 'id':
                        fields.append(o)
                        values.append(getattr(object, o))
                query = self.__generateInsert(table, fields, values)

            self.cursor.execute(query)
            self.db.commit()

            return self.cursor.lastrowid

        except Exception as e:
            self.db.rollback()
            print(e)

    def insertMany(self, *, table: str = '', fields: list = [], values: list = []):
        """
        It takes a table name, a list of fields, and a list of values, and inserts them into the
        database

        :param table: str = ''
        :type table: str
        :param fields: list = ('id', 'name', 'age')
        :type fields: list
        :param values: list = ()
        :type values: list
        :return: The last row id
        """
        try:
            if table and fields and values:
                query = self.__generateInsertMany(table, fields, values)
            else:
                query = self.__generateInsertMany(self.table, fields, values)
            self.cursor.execute(query)
            self.db.commit()

            return self.cursor.lastrowid

        except Exception as e:
            self.db.rollback()
            print(e)
    
    def update(self, *, table: str = '', fields: list = [], values: list = [], object: object = object, clausule: str, parameter: str, parameters_dict: dict = {}) -> int:
        """
        It generates an update query based on the parameters passed to it

        :param table: str = ''
        :type table: str
        :param fields: list = [], values: list = [], object: object = object, clausule: str, parameter:
        str, parameters_dict: dict = {}
        :type fields: list
        :param values: list = []
        :type values: list
        :param object: object = object
        :type object: object
        :param clausule: The condition to be met for the update to be executed
        :type clausule: str
        :param parameter: str = 'id'
        :type parameter: str
        :param parameters_dict: {'id': 1}
        :type parameters_dict: dict
        :return: The number of rows affected by the update.
        """
        try:
            if table and fields and values:
                query = self.__generateUpdate(table, fields, values)
            elif fields and values:
                query = self.__generateUpdate(self.table, fields, values)
            elif object and table:
                for o in [attr for attr in dir(object) if not attr.startswith('__') and not callable(getattr(object, attr))]:
                    if o != 'id':
                        fields.append(o)
                        values.append(getattr(object, o))
                query = self.__generateUpdate(table, fields, values)
            
            # Add where for update data in the db.
            self.reset().setTable(table if table else self.table).where(clausule, parameter, parameters_dict)
            
            query += self.queryResult

            self.cursor.execute(query)
            self.db.commit()

            return self.cursor.rowcount
        except Error as e:
            self.db.rollback()
            print(e)

    def delete(self, table : str = '',*,clausule: str = '', parameter: str = ''):
        try:
            if table:
                self.queryResult = f'delete from {table}'
            else:
                self.queryResult = f'delete from {self.table}'

            self.where(clausule,parameter,{})
            
            self.cursor.execute(self.queryResult)
            self.db.commit()

            return self.cursor.rowcount
        except Error as e:
            self.db.rollback()
            print(e)
        
    
    def __generateInsert(self, table : str, fields: list, values: list) -> str:
        """
        It takes a table name, a list of fields, and a list of values and returns a string that is a
        valid SQL insert statement

        :param table: the table name
        :param fields: list of fields to insert into
        :type fields: list
        :param values: list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13',
        '14', '15', '16', '17', '18', '19', '
        :type values: list
        :return: A string
        """
        try:
            insert = f'insert into {table} ('

            for index, field in enumerate(fields):
                if not index == len(fields) - 1:
                    insert += '{},'.format(field)
                else:
                    insert += '{}'.format(field)

            insert += ') values ('

            for index, value in enumerate(values):
                if not index == len(values) - 1:
                    if type(value) == str:
                        value = f'\'{value}\''
                        insert += '{},'.format(value)
                    else:
                        insert += '{},'.format(value)
                else:
                    if type(value) == str:
                        value = f'\'{value}\''
                        insert += '{}'.format(value)
                    else:
                        insert += '{}'.format(value)
            insert += ');'

            return insert
        except Exception as e:
            print(e)

    def __generateInsertMany(self, table : str, fields: list, values: list) -> str:
        """
        It takes a table name, a list of fields, and a list of values and returns a string that is a
        valid SQL insert statement

        :param table: the table name
        :param fields: list of fields to insert into
        :type fields: list
        :param values: list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13',
        '14', '15', '16', '17', '18', '19', '
        :type values: list
        :return: A string
        """
        try:
            insert = f' insert into {table} ('

            for index, field in enumerate(fields):
                if not index == len(fields) - 1:
                    insert += '{},'.format(field)
                else:
                    insert += '{}'.format(field)
                    insert += ') values '

            for index, value in enumerate(values):
                if not index == len(values) - 1:
                    if type(value) == str:
                        value = f'\'{value}\''
                        insert += '({}),'.format(value)
                    else:
                        insert += '({}),'.format(value)
                else:
                    if type(value) == str:
                        value = f'\'{value}\''
                        insert += '({})'.format(value)
                    else:
                        insert += '({})'.format(value)

            return insert
        except Exception as e:
            print(e)

    def __generateUpdate(self, table : str, fields: list, values: list) -> str:
        """
        It takes a table name, a list of fields, and a list of values, and returns an update statement

        :param table: The table name
        :param fields: ['id', 'name', 'age']
        :param values: a list of tuples, each tuple is a row of data
        :return: The update statement
        """
        try:
            update = f'update {table} set '

            if len(fields) == 1 and len(values) == 1:
                if type(values[0]) == str:
                    values[0] = f'\'{values[0]}\''
                    update += '{} = {}'.format(fields[0],values[0])
                else:
                    update += '{} = {}'.format(fields[0],values[0])
            else:
                for value in values:
                    for index,valueData in enumerate(value):
                        if not index == len(fields) - 1:
                            if type(valueData) == str:
                                valueData = f'\'{valueData}\''
                                update += '{} = {}, '.format(fields[index],valueData)
                            else:
                                update += '{} = {}, '.format(fields[index],valueData)
                        else:
                            if type(valueData) == str:
                                valueData = f'\'{valueData}\''
                                update += '{} = {}'.format(fields[index],valueData)
                            else:
                                update += '{} = {}'.format(fields[index],valueData)
            return update
        except Exception as e:
            print(e)