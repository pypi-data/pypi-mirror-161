import re
import shutil
import sqlite3
import pandas as pd

from pathlib import Path


MLOG_DIR = Path("./mlog")
MLOG_DB = MLOG_DIR / "mlog.db"
KEY_FORMAT = "[a-zA-Z][a-zA-Z0-9_]*"
GET_FORMAT = "[a-zA-Z_][a-zA-Z0-9_]*"

SQL_CREATE_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS runs (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    _name VARCHAR(255),
    _source VARCHAR(255)
)
"""

SQL_CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS logs (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    _run_id INT,
    FOREIGN KEY (_run_id) REFERENCES runs (_id)
)
"""

def start(run=None, config=None, save=None):
    return Run(run=run, config=config, save=save)


def get(*columns, filters=None):

    con = sqlite3.connect(MLOG_DB)

    for column in columns:
        if not re.fullmatch(GET_FORMAT, column):
            raise ValueError(
                f"Column '{column}' does not use format '{GET_FORMAT}'")

    columns = list(columns)
    columns.append('_id')
    columns = ",".join(columns)

    data = pd.read_sql_query(f"SELECT {columns} FROM logs", con)

    con.close()

    return data.set_index('_id')


class Run:

    def __init__(self, run=None, config=None, save=None):

        MLOG_DIR.mkdir(parents=True, exist_ok=True)

        if run is not None and not re.fullmatch(KEY_FORMAT, run):
            raise ValueError(
                f"Run name '{run}' does not use format '{KEY_FORMAT}'")

        con = sqlite3.connect(MLOG_DB)
        cur = con.cursor()

        if config:

            # Retrieve existing columns
            cols = [col[1] for col in cur.execute('PRAGMA table_info(runs)')]

            # Check columns format and add missing columns
            for key in config.keys():

                if not re.fullmatch(KEY_FORMAT, key):
                    raise ValueError(
                        f"Column '{key}' does not use format '{KEY_FORMAT}'")

                if key not in cols:
                    cur.execute(f"ALTER TABLE runs ADD {key}")

            # Add name
            config["_name"] = run

            # Add configs
            cols = ",".join(config.keys())
            vals = ":" + ",:".join(config.keys())
            cur.execute(f"INSERT INTO runs ({cols}) VALUES ({vals})", config)

            # Remove name
            config.pop("_name")

        else:
            cur.execute("INSERT INTO runs DEFAULT VALUES")

        self.run_id = cur.lastrowid

        con.commit()
        con.close()

        # Save files
        if save is not None:

            save_directory = MLOG_DIR / str(self.run_id)
            save_directory.mkdir()

            for file in Path('.').glob(save):
                shutil.copy(file, save_directory)

    def log(self, **logs):

        con = sqlite3.connect(MLOG_DB)

        with con:
            # Retrieve existing columns
            cols = [col[1] for col in con.execute("PRAGMA table_info(logs)")]

            # Check columns and values format and add missing columns
            for key, val in logs.items():

                if not re.fullmatch(KEY_FORMAT, key):
                    raise ValueError(
                        f"Column '{key}' does not use format '{KEY_FORMAT}'")

                if key not in cols:
                    con.execute(f"ALTER TABLE logs ADD {key} REAL")

                try:
                    float(val)
                except ValueError:
                    raise ValueError(
                        f"Value '{val}' for column '{key}' is not a number")

            # Add run id
            logs['_run_id'] = self.run_id

            # Add logs
            cols = ",".join(logs.keys())
            vals = ":" + ",:".join(logs.keys())
            con.execute(f"INSERT INTO logs ({cols}) VALUES ({vals})", logs)

        # Remove run id
        logs.pop('_run_id')

        con.commit()
        con.close()

    def get(self, *columns):
        # TODO: call get with appropriate filter

        con = sqlite3.connect(MLOG_DB)

        for column in columns:
            if not re.fullmatch(GET_FORMAT, column):
                raise ValueError(
                    f"Column '{column}' does not use format '{GET_FORMAT}'")

        columns = list(columns)
        columns.append('_id')
        columns = ",".join(columns)

        data = pd.read_sql_query(
            f"SELECT {columns} FROM logs WHERE _run_id = '{self.run_id}'", con)

        con.close()

        return data.set_index('_id')
