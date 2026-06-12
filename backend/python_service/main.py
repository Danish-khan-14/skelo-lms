from fastapi import FastAPI
from pydantic import BaseModel
import logging
from database import initialize_database, get_connection
from ability_engine import (
    calculate_new_ability_score,
    determine_next_difficulty,
    detect_mastery,
    detect_struggle,
    calculate_accuracy_trend
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Skelo LMS - AI Microservice")

class EvaluateRequest(BaseModel):
    student_id: int
    subject_id: int
    current_ability_score: float
    is_correct: bool
    difficulty: str
    time_taken_sec: int

@app.on_event("startup")
def on_startup():
    initialize_database()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Skelo AI Microservice"}

@app.post("/evaluate")
def evaluate_attempt(request: EvaluateRequest):
    logger.info(f"Evaluating attempt for student {request.student_id}")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT qa.is_correct, qq.difficulty, qa.created_at
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        WHERE qa.student_id = ?
        ORDER BY qa.created_at DESC
        LIMIT 10
    """, (request.student_id,))
    recent_rows = cursor.fetchall()

    recent_attempts = [
        {
            "is_correct": bool(row["is_correct"]),
            "difficulty": row["difficulty"],
            "score": request.current_ability_score
        }
        for row in recent_rows
    ]

    cursor.execute("""
        SELECT ability_score FROM student_ability
        WHERE student_id = ? AND subject_id = ?
        ORDER BY last_updated DESC
        LIMIT 5
    """, (request.student_id, request.subject_id))
    score_rows = cursor.fetchall()
    recent_scores = [row["ability_score"] for row in score_rows]

    conn.close()

    new_ability_score = calculate_new_ability_score(
        request.current_ability_score,
        request.is_correct,
        request.difficulty,
        request.time_taken_sec
    )

    next_difficulty = determine_next_difficulty(new_ability_score)
    is_mastery = detect_mastery(recent_attempts)
    is_struggle = detect_struggle(recent_attempts)
    trend = calculate_accuracy_trend(recent_scores)

    logger.info(f"Student {request.student_id} new ability score: {new_ability_score}")

    return {
        "ability_score": new_ability_score,
        "next_difficulty": next_difficulty,
        "is_mastery": is_mastery,
        "is_struggle": is_struggle,
        "trend": trend
    }

@app.get("/recommend/{student_id}")
def get_recommendations(student_id: int):
    logger.info(f"Getting recommendations for student {student_id}")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sa.subject_id, sa.ability_score, s.title as subject_title
        FROM student_ability sa
        JOIN subjects s ON sa.subject_id = s.id
        WHERE sa.student_id = ?
    """, (student_id,))
    ability_rows = cursor.fetchall()

    if not ability_rows:
        cursor.execute("""
            SELECT t.id as topic_id, t.title, t.difficulty, c.title as chapter_title
            FROM topics t
            JOIN chapters c ON t.chapter_id = c.id
            WHERE t.difficulty = 'Easy'
            LIMIT 3
        """)
        default_topics = cursor.fetchall()
        conn.close()
        return {
            "recommendations": [
                {
                    "topic_id": row["topic_id"],
                    "title": row["title"],
                    "difficulty": row["difficulty"],
                    "chapter": row["chapter_title"],
                    "reason": "Start here — great beginner topic"
                }
                for row in default_topics
            ]
        }

    recommendations = []

    for ability_row in ability_rows:
        subject_id = ability_row["subject_id"]
        ability_score = ability_row["ability_score"]
        subject_title = ability_row["subject_title"]
        target_difficulty = determine_next_difficulty(ability_score)

        cursor.execute("""
            SELECT t.id as topic_id, t.title, t.difficulty, c.title as chapter_title
            FROM topics t
            JOIN chapters c ON t.chapter_id = c.id
            WHERE c.subject_id = ? AND t.difficulty = ?
            LIMIT 2
        """, (subject_id, target_difficulty))
        matched_topics = cursor.fetchall()

        for topic in matched_topics:
            recommendations.append({
                "topic_id": topic["topic_id"],
                "title": topic["title"],
                "difficulty": topic["difficulty"],
                "chapter": topic["chapter_title"],
                "reason": f"Your {subject_title} score is {ability_score} — focus on {target_difficulty} topics"
            })

    cursor.execute("""
        SELECT t.id as topic_id, t.title, t.difficulty, c.title as chapter_title,
        COUNT(qa.id) as attempt_count
        FROM topics t
        JOIN chapters c ON t.chapter_id = c.id
        LEFT JOIN quiz_questions qq ON qq.topic_id = t.id
        LEFT JOIN quiz_attempts qa ON qa.question_id = qq.id AND qa.student_id = ?
        GROUP BY t.id
        HAVING attempt_count = 0
        LIMIT 2
    """, (student_id,))
    untried_topics = cursor.fetchall()

    for topic in untried_topics:
        if len(recommendations) < 3:
            recommendations.append({
                "topic_id": topic["topic_id"],
                "title": topic["title"],
                "difficulty": topic["difficulty"],
                "chapter": topic["chapter_title"],
                "reason": "You haven't tried this topic yet — explore it!"
            })

    conn.close()
    logger.info(f"Returning {len(recommendations[:3])} recommendations for student {student_id}")
    return {"recommendations": recommendations[:3]}

@app.get("/report/{student_id}")
def get_student_report(student_id: int):
    logger.info(f"Getting report for student {student_id}")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) as total, COALESCE(SUM(is_correct), 0) as correct
        FROM quiz_attempts WHERE student_id = ?
    """, (student_id,))
    stats = cursor.fetchone()

    cursor.execute("""
        SELECT sa.ability_score, s.title as subject,
        COALESCE(sa.ability_score, 50.0) as safe_score
        FROM student_ability sa
        JOIN subjects s ON sa.subject_id = s.id
        WHERE sa.student_id = ?
    """, (student_id,))
    ability_scores = cursor.fetchall()

    cursor.execute("""
        SELECT qq.difficulty, COUNT(*) as attempts,
        COALESCE(SUM(qa.is_correct), 0) as correct
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        WHERE qa.student_id = ?
        GROUP BY qq.difficulty
    """, (student_id,))
    by_difficulty = cursor.fetchall()

    cursor.execute("""
        SELECT qa.is_correct, qq.difficulty,
        qa.time_taken_sec, qa.created_at
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        WHERE qa.student_id = ?
        ORDER BY qa.created_at DESC
        LIMIT 5
    """, (student_id,))
    recent_attempts = cursor.fetchall()

    conn.close()

    total = stats["total"] or 0
    correct = stats["correct"] or 0

    return {
        "student_id": student_id,
        "total_attempts": total,
        "correct_attempts": correct,
        "accuracy": round((correct / total * 100), 2) if total > 0 else 0,
        "ability_scores": [dict(row) for row in ability_scores],
        "by_difficulty": [dict(row) for row in by_difficulty],
        "recent_attempts": [dict(row) for row in recent_attempts]
    }

@app.get("/analytics/course/{course_id}")
def get_course_analytics(course_id: int):
    logger.info(f"Getting analytics for course {course_id}")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT qa.student_id) as total_students,
        COUNT(qa.id) as total_attempts,
        SUM(qa.is_correct) as correct_attempts,
        AVG(qa.time_taken_sec) as avg_time_sec
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        JOIN topics t ON qq.topic_id = t.id
        JOIN chapters c ON t.chapter_id = c.id
        WHERE c.subject_id = ?
    """, (course_id,))
    overall = cursor.fetchone()

    cursor.execute("""
        SELECT qq.difficulty,
        COUNT(qa.id) as attempts,
        SUM(qa.is_correct) as correct,
        AVG(qa.time_taken_sec) as avg_time
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        JOIN topics t ON qq.topic_id = t.id
        JOIN chapters c ON t.chapter_id = c.id
        WHERE c.subject_id = ?
        GROUP BY qq.difficulty
    """, (course_id,))
    by_difficulty = cursor.fetchall()

    cursor.execute("""
        SELECT t.title as topic,
        COUNT(qa.id) as attempts,
        SUM(qa.is_correct) as correct
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        JOIN topics t ON qq.topic_id = t.id
        JOIN chapters c ON t.chapter_id = c.id
        WHERE c.subject_id = ?
        GROUP BY t.id
        ORDER BY correct ASC
        LIMIT 3
    """, (course_id,))
    weak_topics = cursor.fetchall()

    conn.close()

    total = overall["total_attempts"] or 0
    correct = overall["correct_attempts"] or 0

    return {
        "course_id": course_id,
        "total_students": overall["total_students"] or 0,
        "total_attempts": total,
        "overall_accuracy": round((correct / total * 100), 2) if total > 0 else 0,
        "avg_time_sec": round(overall["avg_time_sec"] or 0, 2),
        "by_difficulty": [dict(row) for row in by_difficulty],
        "weak_topics": [dict(row) for row in weak_topics]
    }