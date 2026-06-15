const express = require("express");
const axios = require("axios");
const db = require("../db/database");
const { authenticateToken, authenticateAdmin } = require("../middleware/auth");

const router = express.Router();

router.get("/analytics/:courseId", authenticateToken, async (req, res) => {
    const course_id = req.params.courseId;

    try {
        const pythonResponse = await axios.get(
            `${process.env.PYTHON_SERVICE_URL}/analytics/course/${course_id}`
        );
        res.status(200).json(pythonResponse.data);
    } catch (err) {
        console.error("Python service error:", err.message);
        res.status(503).json({ error: "Analytics service unavailable" });
    }
});

router.post("/question", authenticateToken, (req, res) => {
    const { topic_id, question, options, answer, difficulty } = req.body;

    if (!topic_id || !question || !options || !answer || !difficulty) {
        return res.status(400).json({ error: "All fields are required" });
    }

    if (!Array.isArray(options) || options.length !== 4) {
        return res.status(400).json({ error: "Options must be an array of 4 items" });
    }

    const validDifficulties = ["Easy", "Medium", "Hard"];
    if (!validDifficulties.includes(difficulty)) {
        return res.status(400).json({ error: "Difficulty must be Easy, Medium or Hard" });
    }

    const topic = db.prepare("SELECT id FROM topics WHERE id = ?").get(topic_id);
    if (!topic) {
        return res.status(404).json({ error: "Topic not found" });
    }

    const result = db.prepare(`
        INSERT INTO quiz_questions (topic_id, question, options, answer, difficulty)
        VALUES (?, ?, ?, ?, ?)
    `).run(topic_id, question, JSON.stringify(options), answer, difficulty);

    res.status(201).json({
        message: "Question added successfully",
        question_id: result.lastInsertRowid
    });
});

router.get("/students", authenticateToken, (req, res) => {
    const students = db.prepare(`
        SELECT s.id, s.name, s.email, s.created_at,
        COUNT(DISTINCT qa.id) as total_attempts,
        COALESCE(sa.ability_score, 0) as ability_score
        FROM students s
        LEFT JOIN quiz_attempts qa ON qa.student_id = s.id
        LEFT JOIN student_ability sa ON sa.student_id = s.id
        GROUP BY s.id
    `).all();

    res.status(200).json({ students });
});

module.exports = router;