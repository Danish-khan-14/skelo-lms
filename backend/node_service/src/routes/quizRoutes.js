const express = require("express");
const axios = require("axios");
const db = require("../db/database");
const { authenticateToken } = require("../middleware/auth");

const router = express.Router();

router.get("/question", authenticateToken, (req, res) => {
    const { subject_id, difficulty } = req.query;

    if (!subject_id || !difficulty) {
        return res.status(400).json({ error: "subject_id and difficulty are required" });
    }

    const question = db.prepare(`
        SELECT qq.id, qq.question, qq.options, qq.difficulty, qq.topic_id
        FROM quiz_questions qq
        JOIN topics t ON qq.topic_id = t.id
        JOIN chapters c ON t.chapter_id = c.id
        WHERE c.subject_id = ? AND qq.difficulty = ?
        ORDER BY RANDOM()
        LIMIT 1
    `).get(subject_id, difficulty);

    if (!question) {
        return res.status(404).json({ error: "No question found for given criteria" });
    }

    res.status(200).json({
        id: question.id,
        question: question.question,
        options: JSON.parse(question.options),
        difficulty: question.difficulty,
        topic_id: question.topic_id
    });
});

router.post("/submit", authenticateToken, async (req, res) => {
    const { question_id, selected_answer, time_taken_sec } = req.body;
    const student_id = req.user.id;

    if (!question_id || !selected_answer || !time_taken_sec) {
        return res.status(400).json({ error: "question_id, selected_answer and time_taken_sec are required" });
    }

    if (time_taken_sec <= 0 || time_taken_sec > 3600) {
        return res.status(400).json({ error: "time_taken_sec must be between 1 and 3600" });
    }

    const question = db.prepare("SELECT * FROM quiz_questions WHERE id = ?").get(question_id);
    if (!question) {
        return res.status(404).json({ error: "Question not found" });
    }

    const is_correct = question.answer === selected_answer ? 1 : 0;

    db.prepare(`
        INSERT INTO quiz_attempts (student_id, question_id, selected_answer, is_correct, time_taken_sec)
        VALUES (?, ?, ?, ?, ?)
    `).run(student_id, question_id, selected_answer, is_correct, time_taken_sec);

    const topic = db.prepare("SELECT * FROM topics WHERE id = ?").get(question.topic_id);
    const chapter = db.prepare("SELECT * FROM chapters WHERE id = ?").get(topic.chapter_id);
    const subject_id = chapter.subject_id;

    const abilityRow = db.prepare(
        "SELECT ability_score FROM student_ability WHERE student_id = ? AND subject_id = ?"
    ).get(student_id, subject_id);

    const current_score = abilityRow ? abilityRow.ability_score : 50.0;

    let ability_score = current_score;
    let next_difficulty = "Easy";
    let is_mastery = false;
    let is_struggle = false;

    try {
        const pythonResponse = await axios.post(
            `${process.env.PYTHON_SERVICE_URL}/evaluate`,
            {
                student_id,
                subject_id,
                current_ability_score: current_score,
                is_correct: is_correct === 1,
                difficulty: question.difficulty,
                time_taken_sec
            }
        );
        ability_score = pythonResponse.data.ability_score;
        next_difficulty = pythonResponse.data.next_difficulty;
        is_mastery = pythonResponse.data.is_mastery;
        is_struggle = pythonResponse.data.is_struggle;
    } catch (err) {
        console.error("Python service error:", err.message);
    }

    if (abilityRow) {
        db.prepare(`
            UPDATE student_ability SET ability_score = ?, last_updated = CURRENT_TIMESTAMP
            WHERE student_id = ? AND subject_id = ?
        `).run(ability_score, student_id, subject_id);
    } else {
        db.prepare(`
            INSERT INTO student_ability (student_id, subject_id, ability_score)
            VALUES (?, ?, ?)
        `).run(student_id, subject_id, ability_score);
    }

    res.status(200).json({
        is_correct: is_correct === 1,
        correct_answer: question.answer,
        ability_score,
        next_difficulty,
        is_mastery,
        is_struggle
    });
});

router.get("/dashboard", authenticateToken, (req, res) => {
    const student_id = req.user.id;

    const attempts = db.prepare(`
        SELECT COUNT(*) as total_attempts,
        COALESCE(SUM(is_correct), 0) as correct_attempts
        FROM quiz_attempts WHERE student_id = ?
    `).get(student_id);

    const ability_scores = db.prepare(`
        SELECT sa.ability_score, s.title as subject
        FROM student_ability sa
        JOIN subjects s ON sa.subject_id = s.id
        WHERE sa.student_id = ?
    `).all(student_id);

    const recent_attempts = db.prepare(`
        SELECT qa.is_correct, qq.difficulty, qa.created_at
        FROM quiz_attempts qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        WHERE qa.student_id = ?
        ORDER BY qa.created_at DESC
        LIMIT 10
    `).all(student_id);

    const total = attempts.total_attempts || 0;
    const correct = attempts.correct_attempts || 0;

    res.status(200).json({
        total_attempts: total,
        correct_attempts: correct,
        accuracy: total > 0 ? Math.round((correct / total) * 100) : 0,
        ability_scores,
        recent_attempts
    });
});

router.get("/recommendations", authenticateToken, async (req, res) => {
    const student_id = req.user.id;

    try {
        const pythonResponse = await axios.get(
            `${process.env.PYTHON_SERVICE_URL}/recommend/${student_id}`
        );
        res.status(200).json(pythonResponse.data);
    } catch (err) {
        console.error("Python service error:", err.message);
        res.status(503).json({ error: "Recommendation service unavailable" });
    }
});

router.get("/report", authenticateToken, async (req, res) => {
    const student_id = req.user.id;

    try {
        const pythonResponse = await axios.get(
            `${process.env.PYTHON_SERVICE_URL}/report/${student_id}`
        );
        res.status(200).json(pythonResponse.data);
    } catch (err) {
        console.error("Python service error:", err.message);
        res.status(503).json({ error: "Report service unavailable" });
    }
});

module.exports = router;