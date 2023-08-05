from .Object import Object
from .Table import Table


class Schema(Object):

    def __init__(self, name, data_storage):
        """
        :param system: System object
        :param name: Name of the schema

        Initialize a Schema object
        """
        # Call Object.__init__()
        super().__init__()

        # Set the name of the schema
        self.name = name

        # Set the system that this schema exists in
        self.data_storage = data_storage

    def list_tables(self):
        """

        :return:
        """
        return self.data_storage.list_tables(schema=self.name)

    def table_exists(self, table_object: Table = None):
        """
        Does this table exist in this schema

        :param table_object: Table we want to check for existence
        :return boolean: True if the table exists in this schema. False otherwise.
        """
        return self.data_storage.table_exists(schema=self.name, table_object=table_object)
