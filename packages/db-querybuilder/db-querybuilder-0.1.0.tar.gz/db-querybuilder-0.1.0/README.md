# Database Query Builder 

- A library that serves as a means of connecting to a database and executing sql statements.

### Installation 😀📚
> pip install db_querybuilder

## Get started 
How to use  <mark><b>Database Query Builder<b><mark>

````python
from db_querybuilder import DatabaseQueryBuilder

class TestUser():
    def __init__(self) -> None:
        self.id = -1
        self.first_name = 'Jhon'
        self.last_name = 'Doe'


if __name__ == '__main__':
    db = DatabaseQueryBuilder(db_user='root',db_password='',db_database='test',db_port=3306)

    # Query to json
    query = db.setTable('test_data').query().where(clausule='id',parameter=1).toJson()
    print(query)

    # Query select
    query = db.select(['id','first_name']).from_('test_data').where('email','emaffini0@mlb.com').results()
    print(query)

    # Insert data with attributes object
    user = TestUser()
    query = db.insert(table='test_data',object=user)
    print(query)

````



