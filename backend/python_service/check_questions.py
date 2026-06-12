from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT qq.id, qq.question, qq.answer, qq.difficulty, t.title as topic
    FROM quiz_questions qq
    JOIN topics t ON qq.topic_id = t.id
    ORDER BY qq.id
    LIMIT 20
""")
rows = cursor.fetchall()
for row in rows:
    print(f"ID:{row['id']} | {row['difficulty']} | Q: {row['question'][:40]} | A: {row['answer']}")

conn.close()