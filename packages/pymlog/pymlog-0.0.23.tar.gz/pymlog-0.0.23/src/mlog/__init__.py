import sqlite3

from .mlog import start, get
from .mlog import MLOG_DIR, MLOG_DB
from .mlog import SQL_CREATE_RUNS_TABLE, SQL_CREATE_LOGS_TABLE


MLOG_DIR.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(MLOG_DB)

with con:
    con.execute(SQL_CREATE_RUNS_TABLE)
    con.execute(SQL_CREATE_LOGS_TABLE)

con.close()
