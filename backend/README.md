# Skelo LMS — Backend

Adaptive Learning Management System backend built with Python FastAPI and Node.js Express.

## Project Structure
backend/

├── python_service/          # AI/ML adaptive engine

│   ├── main.py              # FastAPI endpoints

│   ├── ability_engine.py    # Adaptive algorithm

│   ├── database.py          # SQLite connection

│   ├── seed_data.py         # Seed script

│   └── ALGORITHM.md         # Algorithm documentation

└── node_service/            # API gateway

└── src/

├── server.js

├── routes/

├── middleware/

└── db/

## Setup Instructions

### Step 1 — Clone Repository
```bash
git clone https://github.com/Danish-khan-14/skelo-lms.git
cd skelo-lms
```

### Step 2 — Python Service Setup
```bash
cd backend/python_service
python -m venv env
env\Scripts\activate
pip install fastapi uvicorn numpy requests
python seed_data.py
uvicorn main:app --reload --port 8000
```

### Step 3 — Node.js Service Setup
```bash
cd backend/node_service
npm install
npm run dev
```

### Step 4 — Verify Both Services
http://localhost:8000/health → Python service

http://localhost:3000/health → Node service

http://localhost:8000/docs  → API documentation

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register student |
| POST | /api/auth/login | Login student |

### Quiz
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/quiz/question | Get adaptive question |
| POST | /api/quiz/submit | Submit answer |
| GET | /api/quiz/recommendations | Get top 3 recommendations |
| GET | /api/quiz/report | Student performance report |

### Courses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/courses | List all subjects |
| GET | /api/courses/:id | Subject detail with chapters |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/admin/analytics/:courseId | Class analytics |
| GET | /api/admin/students | All students list |
| POST | /api/admin/question | Add quiz question |

## Adaptive Algorithm

- Ability Score: 0–100 per subject
- Difficulty routing: Easy (0–44), Medium (45–74), Hard (75–100)
- Mastery: >75% on Hard questions 3 times in a row
- Struggle: <50% accuracy on Easy questions
- Recommendations: based on ability score + gap analysis