##    threadsnake. A tiny experimental server-side express-like library.
##    Copyright (C) 2022  Erick Fernando Mora Ramirez
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##
##    mailto:erickfernandomoraramirez@gmail.com

from functools import reduce
from typing import Any, Callable, Dict, List, Tuple, Type
from enum import IntEnum
import sqlite3

class FieldType(IntEnum):
    NONE = 0,
    READ = 1,
    WRITE = 2,
    READWRITE = 3,
    ID = 4,
    FILTER = 8

class Field:
    __slots__ = ['name', 'alias', 'type']
    def __init__(self, name:str, alias:str = None, type:FieldType = FieldType.READ) -> None:
        self.name:str = name
        self.alias:str = alias or name
        self.type:FieldType = type
        
    def is_type(self, type:FieldType):
        return self.type & type == type
    
    def apply_type(self, type:FieldType):
        self.type |= type

entities = {}


class BaseEntity:
    def __init__(self, name:str = None):
        self.name:str = name
        self.cls:Type = None
        self.fields:Dict[str, Field] = {}
        
    def with_fields_type(self, fields:List[Any], type:FieldType = FieldType.READWRITE):
        for f in fields:
            alias = f
            if not isinstance(f, str):
                f, alias = f
            else:
                pass
            if f not in self.fields:
                self.fields[f] = Field(f, alias, type)
            else:
                self.fields[f].alias = alias
                self.fields[f].apply_type(type)
        return self
        
    def id(self, fields:Dict[str, str]):
        return self.with_fields_type(fields, FieldType.ID)
    
    def read(self, fields:Dict[str, str]):
        return self.with_fields_type(fields, FieldType.READ)
    
    def write(self, fields:Dict[str, str]):
        return self.with_fields_type(fields, FieldType.WRITE)
    
    def readwrite(self, fields:Dict[str, str]):
        return self.with_fields_type(fields, FieldType.READWRITE)
    
    def filter(self, fields:Dict[str, str]):
        return self.with_fields_type(fields, FieldType.FILTER)
    
class Entity(BaseEntity):
    def __init__(self, name: str = None):
        BaseEntity.__init__(self, name)
        
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.cls = args[0]
        self.name = self.name or self.cls.__name__ 
        entities[self.cls] = self
        return args[0]
    
    def fields_with_type(self, type_filter:FieldType):
        return [i for i in self.fields.values() if (i.type & type_filter) == type_filter]

class DatabaseAccess:
    def __init__(self, databaseName:str) -> None:
        self.databaseName = databaseName
        
    def select(self, query:str):
        with sqlite3.connect(self.databaseName) as c:
            cur = c.cursor()
            for r in cur.execute(query):
                yield r
                
    def insert_many(self, tableName:str, columns:List[str], values:List[Tuple[Any]]):
        cols:str = ', '.join(columns)
        par:str = ', '.join(['?' for i in columns])
        query = f'INSERT INTO {tableName} ({cols}) VALUES ({par})'
        try:
            with sqlite3.connect(self.databaseName) as c:
                cur = c.cursor()
                cur.executemany(query, values)
                c.commit()
                return cur.rowcount
        except sqlite3.IntegrityError:
            return 0
        
    def insert(self, tableName:str, values:Dict[str, Any]):
        cols:str = ', '.join([i for i in values.keys()])
        par:str = ', '.join(['?' for i in values.keys()])
        params:Tuple = tuple([values[i] for i in values.keys()])
        query = f'INSERT INTO {tableName} ({cols}) VALUES ({par})'
        try:
            with sqlite3.connect(self.databaseName) as c:
                cur:sqlite3.Cursor = c.cursor()
                cur.execute(query, params)
                c.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return 0
    
    def select(self, tableName:str, columns:List[str] = None):
        columns = ', '.join(columns or ['*'])
        query:str = f"SELECT {columns} FROM {tableName};"
        with sqlite3.connect(self.databaseName) as c:
            cur = c.cursor()
            for r in cur.execute(query):
                yield r
                        
    def select_match(self, tableName:str, match:Dict[str, Any], columns:List[str] = None):
        columns = ', '.join(columns or ['*'])
        filtering = ' AND '.join([f'{i}=:{i}' for i in match.keys()])
        query:str = f"SELECT {columns} FROM {tableName} WHERE {filtering};"
        with sqlite3.connect(self.databaseName) as c:
            cur = c.cursor()
            for r in cur.execute(query, match):
                yield r

    def select_where(self, tableName:str, where:List[str], columns:List[str] = None):
        columns = ', '.join(columns or ['*'])
        filtering = ' AND '.join(where)
        query:str = f"SELECT {columns} FROM {tableName} WHERE {filtering};"
        with sqlite3.connect(self.databaseName) as c:
            cur = c.cursor()
            for r in cur.execute(query):
                yield r     

    def update(self, tableName, newValues:Dict[str, Any], where:Dict[str, Any]):
        updates = ', '.join([f'{i} = ?' for i in newValues.keys()])
        whereStr = ' AND '.join([f'{i} = ?' for i in where.keys()])
        params = [i for i in newValues.values()] + [i for i in where.values()]
        query:str = f'UPDATE {tableName} SET {updates} WHERE {whereStr};'
        try:
            with sqlite3.connect(self.databaseName) as c:
                cur:sqlite3.Cursor = c.cursor()
                cur.execute(query, params)
                c.commit()
                return cur.rowcount
        except sqlite3.IntegrityError as e:
            return 0
        
    def update_where(self, tableName, newValues:Dict[str, Any], where:List[str]):
        updates = ', '.join([f'{i} = ?' for i in newValues.keys()])
        whereStr = ' AND '.join(where)
        params = [i for i in newValues.values()]
        query:str = f'UPDATE {tableName} SET {updates} WHERE {whereStr};'
        try:
            with sqlite3.connect(self.databaseName) as c:
                cur:sqlite3.Cursor = c.cursor()
                cur.execute(query, params)
                c.commit()
                return cur.rowcount
        except sqlite3.IntegrityError as e:
            return 0
        
    def delete(self, tableName, where:Dict[str, Any]):
        whereStr = ' AND '.join([f'{i} = ?' for i in where.keys()])
        params = [i for i in where.values()]
        query:str = f'DELETE FROM {tableName} WHERE {whereStr};'
        with sqlite3.connect(self.databaseName) as c:
            cur:sqlite3.Cursor = c.cursor()
            cur.execute(query, params)
            c.commit()
            return cur.rowcount
        
    def delete_where(self, tableName, where:List[str]):
        whereStr = ' AND '.join(where)
        query:str = f'DELETE FROM {tableName} WHERE {whereStr};'
        with sqlite3.connect(self.databaseName) as c:
            cur:sqlite3.Cursor = c.cursor()
            cur.execute(query)
            c.commit()
            return cur.rowcount

class NanORM(DatabaseAccess):
    def __init__(self, databaseName:str) -> None:
        super().__init__(databaseName)
    
    def get_entity(self, entity:Any) -> Entity:
        return [i for i in entities.values() if isinstance(entity, i.cls)][0]
    
    def values_of_type(self, entity:Any, type:FieldType) -> Tuple[str, Dict[str, Any]]:
        table, fields = self.fields_of_type(entity, type)
        fields = [i for i in fields if getattr(entity, i.name) is not None]
        return  table, {f.alias:getattr(entity, f.name) for f in fields}
    
    def fields_of_type(self, entity:Any, type:FieldType) -> Tuple[str, Dict[str, Any]]:
        e = self.get_entity(entity)
        return e.name, e.fields_with_type(type)
    
    def entity_insert(self, entity:Any) -> int:
        table, values = self.values_of_type(entity, FieldType.WRITE)
        return self.insert(table, values)

    def entity_delete_by_id(self, entity:Any) -> int:
        table, values = self.values_of_type(entity, FieldType.ID)
        return self.delete(table, values)

    def entity_delete_when_matches(self, entity:Any) -> int:
        table, values = self.values_of_type(entity, FieldType.FILTER)
        return self.delete(table, values)

    def entity_update_by_id(self, entity:Any) -> int:
        table, newValues = self.values_of_type(entity, FieldType.WRITE)
        table, where = self.values_of_type(entity, FieldType.ID )
        return self.update(table, newValues, where)

    def entity_update_when_matches(self, entity:Any) -> int:
        table, newValues = self.values_of_type(entity, FieldType.WRITE)
        table, where = self.values_of_type(entity, FieldType.FILTER)
        return self.update(table, newValues, where)
    
    def entity_select_by_id(self, entity:Any, ctor:Callable[[], Any]) -> int:
        table, where = self.values_of_type(entity, FieldType.ID)
        table, read = self.fields_of_type(entity, FieldType.READ)
        columns = [i.alias for i in read]
        for r in self.select_match(table, where, columns):
            result = ctor()
            for i in range(len(read)):
                setattr(result, read[i].name, r[i])
            yield result
    
    def create_table(self, entity:Any):
        table, read = self.fields_of_type(entity, FieldType.NONE)
        columns = []
        for f in read:
            colName = f.alias
            value = getattr(entity, f.name)
            if isinstance(value, int):
                colName += ' INTEGER'
            elif isinstance(value, float):
                colName += ' FLOAT'
            else:
                colName += ' TEXT'
            if (f.type & FieldType.ID) == FieldType.ID:
                colName += ' PRIMARY KEY'
            columns.append(colName)
        cols = ', '.join(columns)
        query = f'CREATE TABLE IF NOT EXISTS {table}({cols});'
        with sqlite3.connect(self.databaseName) as c:
            cur:sqlite3.Cursor = c.cursor()
            cur.execute(query)
            c.commit()
            return cur.rowcount

@Entity('Person').id([('id', 'rowid')]).readwrite(['firstName', 'lastName', 'identification']).filter(['firstName'])
class PersonExample:
    def __init__(self, id:int = 0, firstName:str = None, lastName:str = None, identification:str = None) -> None:
        self.id = 0
        self.firstName:str = firstName
        self.lastName:str = lastName
        self.identification:str = identification