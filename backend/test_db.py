import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bhageeratha@1",
    database="ai_doc_platform"
)

print("Connected!", db)
