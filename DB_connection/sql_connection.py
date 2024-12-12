import pymysql
from dotenv import load_dotenv
import os

class sqlConnection():

    companies = []

    new_companies = [
        {
            "name": "Tigo",
            "user": "Tigo_Colombia"
        },
        {
            "name": "WOM",
            "user": "womcolombia"
        }
    ]

    def __init__(self):
        load_dotenv()

        self.connection = pymysql.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            db=os.environ.get('DB_SCHEMA')
        )

        self.cursor = self.connection.cursor()


    def createTables(self):
        sql_companies = 'CREATE TABLE companies(id int NOT NULL AUTO_INCREMENT, name varchar(50) NOT NULL, twitter_user varchar(50), PRIMARY KEY(id))'
        sql_tweets = 'CREATE TABLE tweets(id int NOT NULL AUTO_INCREMENT, content varchar(1000) NOT NULL, post_date date, sentiment_score float, company_id int, PRIMARY KEY(id), FOREIGN KEY (company_id) REFERENCES companies(id))'

        try:
            self.cursor.execute(sql_companies)
            self.cursor.execute(sql_tweets)
            print("Tablas creadas correctamente")
        except Exception as e:
            raise

    def get_companies(self):
        query = "SELECT name, twitter_user FROM companies"

        companies = []

        try:
            self.cursor.execute(query)
            result = list(self.cursor.fetchall())
            for item in result:
                companies.append({
                    "name": item[0],
                    "user": item[1]
                })
        except Exception as e:
            print("Algo salió mal :( \n", e)

        return companies

    def insert_companies(self):
        for company in self.new_companies:
            c_name = company["name"]
            c_user = company["user"]
            query = f"INSERT INTO companies (name, twitter_user) VALUES ('{c_name}', '{c_user}')"
            try:
                self.cursor.execute(query)
                self.connection.commit()
                print("Registros insertados")
            except Exception as e:
                raise
        
        

sqlConnection()
