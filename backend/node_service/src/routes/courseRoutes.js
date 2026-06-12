const express = require("express");
const db = require("../db/database");
const { authenticateToken } = require("../middleware/auth");

const router = express.Router();

router.get("/", authenticateToken, (req, res) => {
    const subjects = db.prepare(`
        SELECT s.id, s.title, s.description,
        c.title as curriculum_title,
        COUNT(DISTINCT ch.id) as total_chapters,
        COUNT(DISTINCT t.id) as total_topics
        FROM subjects s
        JOIN curriculums c ON s.curriculum_id = c.id
        LEFT JOIN chapters ch ON ch.subject_id = s.id
        LEFT JOIN topics t ON t.chapter_id = ch.id
        GROUP BY s.id
    `).all();

    res.status(200).json({ subjects });
});

router.get("/:id", authenticateToken, (req, res) => {
    const subject_id = req.params.id;

    const subject = db.prepare(`
        SELECT s.id, s.title, s.description,
        c.title as curriculum_title
        FROM subjects s
        JOIN curriculums c ON s.curriculum_id = c.id
        WHERE s.id = ?
    `).get(subject_id);

    if (!subject) {
        return res.status(404).json({ error: "Subject not found" });
    }

    const chapters = db.prepare(`
        SELECT ch.id, ch.title, ch.description, ch.order_index,
        COUNT(t.id) as total_topics
        FROM chapters ch
        LEFT JOIN topics t ON t.chapter_id = ch.id
        WHERE ch.subject_id = ?
        GROUP BY ch.id
        ORDER BY ch.order_index
    `).all(subject_id);

    const chaptersWithTopics = chapters.map(chapter => {
        const topics = db.prepare(`
            SELECT t.id, t.title, t.difficulty, t.order_index,
            COUNT(qq.id) as total_questions
            FROM topics t
            LEFT JOIN quiz_questions qq ON qq.topic_id = t.id
            WHERE t.chapter_id = ?
            GROUP BY t.id
            ORDER BY t.order_index
        `).all(chapter.id);
        return { ...chapter, topics };
    });

    res.status(200).json({
        subject,
        chapters: chaptersWithTopics
    });
});

module.exports = router;