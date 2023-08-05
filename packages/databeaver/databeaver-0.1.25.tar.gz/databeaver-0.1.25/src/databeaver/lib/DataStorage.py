from .Object import Object
from .Schema import Schema
from .Table import Table


class DataStorage(Object):
    # Standard Data Types that all DataStorage classes must be able to handle
    DATA_TYPE_BOOLEAN = "BOOLEAN"
    DATA_TYPE_FLOAT = "FLOAT"
    DATA_TYPE_INTEGER = "INTEGER"
    DATA_TYPE_STRING = "STRING"
    DATA_TYPE_TEXT = "TEXT"
    DATA_TYPE_TIMESTAMP = "TIMESTAMP"

    STORAGE_TYPE_MYSQL = "MySQL"
    STORAGE_TYPE_POSTGRESQL = "PostgreSQL"
    STORAGE_TYPE_UNKNOWN = "UNKNOWN"

    def __init__(self):
        """
        Instantiate the base abstraction for all DataStorage classes
        """

        # Call Object.__init__()
        super().__init__()

        # Initial instantiation of class variables
        self.logger = self.get_logger()
        self.type = self.STORAGE_TYPE_UNKNOWN
        self.host = None
        self.database = None
        self.user = None
        self.password = None

    def create(self, schema=None, object_to_create=None):
        """
        Create a given Object in the database (withing the given schema
        :param schema:
        :param object_to_create: something we wish to create (Table, Tables, etc)
        :return:
        """
        if object_to_create is None:
            self.logger.warning(f"object_to_create is None. No work performed.")
            return

        # The caller requested a table be created
        if isinstance(object_to_create, Table):
            self.logger.info(f'Creating {schema}.{object_to_create.name}')
            self.create_table(schema, object_to_create.name, object_to_create.columns)

    def drop(self, schema=None, object_to_drop=None):
        """

        :param schema:
        :param object_to_drop:
        :return boolean: True if the table was dropped. False otherwise
        """
        if object_to_drop is None:
            self.logger.warning("No object to drop provided. No work done.")
            return False

        # The user requested a table be dropped
        if isinstance(object_to_drop, Table):
            self.logger.info(f"Dropping the table '{schema}.{object_to_drop.name}'")
            self.drop_table(table_name=object_to_drop.name, schema=schema)
            return True

        return False

    def get_schema(self, schema_name):
        """
        Get an instance of a Schema class

        :param schema_name:
        :return schema: Instantiated Schema object
        """
        schema = Schema(schema_name, data_storage=self)
        return schema

    def list_tables(self, schema=None):
        """
        List all tables in a given schema

        :param schema:
        :return:
        """
        self.list_tables(schema)

    def exists(self, schema=None, object_to_check = None):
        """
        Does a table exist in a given schema
        :return:
        """

        if isinstance(object_to_check, Table):
            return self.table_exists(schema=schema, table_name=object_to_check.name)

        return False