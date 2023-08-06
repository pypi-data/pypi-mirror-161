from typing import List

from pydantic import BaseModel


class SqlScript(BaseModel):
    name: str
    catch_errors: bool = False


class DatabaseExecution(BaseModel):
    database: str = None
    scripts: List[SqlScript] = []


class SqlExecution(BaseModel):
    database_execution_objects: List[DatabaseExecution]
