from . import db
class User(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    username:str = db.Column(db.String(80), unique=True, nullable=False)
    email:str = db.Column(db.String(120), unique=True, nullable=False)
    address:str = db.Column(db.String(120), unique=False, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
# 添加名为age的整数列到User表中
#add_column_to_table("user", "age", "INTEGER")
def add_column_to_table(table_name, column_name, column_type):
    sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    print(sql)
    #ALTER TABLE user ADD COLUMN address VARCHAR(120)
    db.session.execute(sql)
    db.session.commit()