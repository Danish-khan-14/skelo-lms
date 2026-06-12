const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const db = require("../db/database");

const router = express.Router();

router.post("/register", async (req, res) => {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
        return res.status(400).json({ error: "Name, email and password are required" });
    }

    const existingUser = db.prepare("SELECT id FROM students WHERE email = ?").get(email);
    if (existingUser) {
        return res.status(409).json({ error: "Email already registered" });
    }

    const password_hash = await bcrypt.hash(password, 10);

    const result = db.prepare(
        "INSERT INTO students (name, email, password_hash) VALUES (?, ?, ?)"
    ).run(name, email, password_hash);

    const token = jwt.sign(
        { id: result.lastInsertRowid, email, role: "student" },
        process.env.JWT_SECRET,
        { expiresIn: "7d" }
    );

    res.status(201).json({
        message: "Registration successful",
        token,
        student: { id: result.lastInsertRowid, name, email }
    });
});

router.post("/login", async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ error: "Email and password are required" });
    }

    const student = db.prepare("SELECT * FROM students WHERE email = ?").get(email);
    if (!student) {
        return res.status(401).json({ error: "Invalid email or password" });
    }

    const validPassword = await bcrypt.compare(password, student.password_hash);
    if (!validPassword) {
        return res.status(401).json({ error: "Invalid email or password" });
    }

    const token = jwt.sign(
        { id: student.id, email: student.email, role: "student" },
        process.env.JWT_SECRET,
        { expiresIn: "7d" }
    );

    res.status(200).json({
        message: "Login successful",
        token,
        student: { id: student.id, name: student.name, email: student.email }
    });
});

module.exports = router;