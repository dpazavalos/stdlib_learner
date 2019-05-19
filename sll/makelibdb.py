"""
ModuleInfo to populate database with list of all standard modules (using stdlib_list)
"""

import stdlib_list
import sqlite3
from pathlib import Path


class TableModules:
    # Table name Kept as inherited. Keeps .TableModules accessible
    # accessible from child, without polluting child's __dict__
    table_name = 'modules'


class RowFunctions:
    @property
    def header(self) -> list:
        return [x for x in self.__dict__]
    #
    @property
    def row(self) -> list:
        return [x[0] for x in self.__dict__.values()]
    #
    @property
    def header_insert(self) -> str:
        return f"{','.join(self.header)}"
    #
    @property
    def header_valget(self) -> str:
        return f"({','.join(['?']*len(self.header))})"
    #
    @property
    def make_table(self) -> str:
        return ',\n'.join(f"{k} {v[1]}" for k, v in self.__dict__.items())


class SqlObj(TableModules, RowFunctions):
    pass


class ModuleRow(SqlObj):
    def __init__(self, module: str):
        self.mod_name = [module, 'text PRIMARY KEY']
        self.accessed = [0, 'NUMERIC NOT NULL']
        self.info = ['', 'text']


class CreateLibDB:
    def __init__(self):
        self.db_path = Path(__file__)
        self.db_path = self.db_path.parent/'lib.db'
        self.db_path.touch()
        self.db_conn: sqlite3.Connection

        self.sql_obj = SqlObj()

    def create_table(self):
        sql_cmd = f"""
        CREATE TABLE IF NOT EXISTS {self.sql_obj.table_name} (
            {self.sql_obj.make_table}
        );"""
        c = self.db_conn.cursor()
        c.execute(sql_cmd)

    def insert_row(self, return_newid: bool = False):
        sql_cmd = f"""
        INSERT INTO {self.sql_obj.table_name}({self.sql_obj.header_insert})
        VALUES{self.sql_obj.header_valget}"""
        try:
            c = self.db_conn.cursor()
            c.execute(sql_cmd, self.sql_obj.row)
            if return_newid:
                return c.lastrowid
        except sqlite3.IntegrityError:
            pass

    def create_db(self):
        table_made = False
        with sqlite3.connect(self.db_path) as self.db_conn:
            for mod in stdlib_list.stdlib_list():
                if '.' not in mod:
                    self.sql_obj = ModuleRow(mod)
                    if not table_made:
                        self.create_table()
                        table_made = True

                    self.insert_row()


if __name__ == '__main__':
    create = CreateLibDB()
    create.create_db()
