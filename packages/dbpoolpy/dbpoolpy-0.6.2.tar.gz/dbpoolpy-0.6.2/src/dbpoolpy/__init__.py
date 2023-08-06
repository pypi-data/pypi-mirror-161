try:
    from pymysql import install_as_MySQLdb
    install_as_MySQLdb()
except Exception:
    pass

from .dbpool import init_pool
from .dbpool import connect_db
from .table import SelectTable as Select
from .table import UpdateTable as Update
from .table import DeleteTable as Delete
from .table import InsertTable as Insert
from .table import Table
from .config import settings

__version__ = "0.6.2"
