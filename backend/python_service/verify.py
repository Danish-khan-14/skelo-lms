#This script is used to verify that the quiz_questions table has the expected distribution of difficulties -- (this is and temporary file)

from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) as count FROM curriculums")
print("Curriculums:", dict(cursor.fetchone()))

cursor.execute("SELECT COUNT(*) as count FROM subjects")
print("Subjects:", dict(cursor.fetchone()))

cursor.execute("SELECT COUNT(*) as count FROM chapters")
print("Chapters:", dict(cursor.fetchone()))

cursor.execute("SELECT COUNT(*) as count FROM topics")
print("Topics:", dict(cursor.fetchone()))

cursor.execute("SELECT difficulty, COUNT(*) as count FROM quiz_questions GROUP BY difficulty")
rows = cursor.fetchall()
for row in rows:
    print("Questions:", dict(row))

conn.close()