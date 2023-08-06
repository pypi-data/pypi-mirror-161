from os import getenv
import pymysql

class DataBase:
    def __init__(self) -> None: 
        self.connection = pymysql.connect(
            host = getenv('DB_HOST'), 
            user = getenv('DB_USER'),
            password = getenv('DB_PASSWORD'),
            port= int(getenv('DB_PORT')),
            db = getenv('DB')
        )
        self.cursor = self.connection.cursor()

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()