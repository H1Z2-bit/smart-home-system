class MySQLRepositoryNotReady(RuntimeError):
    pass


def mysql_not_ready():
    raise MySQLRepositoryNotReady("MySQLRepository is reserved. Use MockRepository before schema.sql is finalized.")