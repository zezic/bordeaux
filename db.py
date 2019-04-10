import databases
import sqlalchemy

database = databases.Database('sqlite:///db.sqlite')
metadata = sqlalchemy.MetaData()
