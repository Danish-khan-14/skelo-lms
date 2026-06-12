import requests

BASE_URL = "http://localhost:3000"

test_students = [
    {"name": "Alice (High Performer)",   "email": "alice10@test.com",   "password": "test1234"},
    {"name": "Bob (Average Student)",    "email": "bob10@test.com",     "password": "test1234"},
    {"name": "Charlie (Struggling)",     "email": "charlie10@test.com", "password": "test1234"},
    {"name": "Diana (Mastery Track)",    "email": "diana10@test.com",   "password": "test1234"},
    {"name": "Eve (New Student)",        "email": "eve10@test.com",     "password": "test1234"},
    {"name": "Frank (Fast Learner)",     "email": "frank10@test.com",   "password": "test1234"},
    {"name": "Grace (Slow Learner)",     "email": "grace10@test.com",   "password": "test1234"},
    {"name": "Henry (Mixed Results)",    "email": "henry10@test.com",   "password": "test1234"},
    {"name": "Iris (Hard Questions)",    "email": "iris10@test.com",    "password": "test1234"},
    {"name": "Jack (Zero Attempts)",     "email": "jack10@test.com",    "password": "test1234"},
]

quiz_scenarios = {
    "alice10@test.com":   [(22,"<class 'int'>",8),(23,"_name",7),(24,"5",6),(25,"9",5),(26,"False",6)],
    "bob10@test.com":     [(22,"<class 'int'>",15),(25,"6",20),(26,"False",18),(28,"[0,2,4]",22),(29,"Does nothing",16)],
    "charlie10@test.com": [(22,"Error",30),(25,"6",35),(26,"True",28),(23,"2name",32),(24,"6",25)],
    "diana10@test.com":   [(22,"<class 'int'>",5),(23,"_name",4),(24,"5",6),(25,"9",5),(26,"False",4)],
    "eve10@test.com":     [],
    "frank10@test.com":   [(22,"<class 'int'>",4),(23,"_name",3),(24,"5",4),(25,"9",3),(26,"False",3)],
    "grace10@test.com":   [(22,"Error",45),(23,"Error",50),(24,"Error",40),(25,"6",35),(26,"True",42)],
    "henry10@test.com":   [(22,"<class 'int'>",10),(25,"6",15),(26,"False",12),(28,"[0,2,4]",18),(29,"Error",20)],
    "iris10@test.com":    [(34,"Restricts instance attributes",10),(35,"@functools.lru_cache",8),(36,"function",9),(37,"True parallel thread execution",7),(38,"{'a':2}",6)],
    "jack10@test.com":    [],
}

def register_student(student):
    response = requests.post(f"{BASE_URL}/api/auth/register", json=student)
    data = response.json()
    if "token" in data:
        print(f"  Registered: {student['name']}")
        return data["token"]
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": student["email"], "password": student["password"]
    })
    data = response.json()
    print(f"  Logged in: {student['name']}")
    return data.get("token")

def submit_answer(token, question_id, selected_answer, time_taken):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question_id": question_id, "selected_answer": selected_answer, "time_taken_sec": time_taken}
    response = requests.post(f"{BASE_URL}/api/quiz/submit", json=payload, headers=headers)
    return response.json()

def get_report(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{BASE_URL}/api/quiz/report", headers=headers).json()

def get_recommendations(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{BASE_URL}/api/quiz/recommendations", headers=headers).json()

print("\n=== SKELO LMS — 10 STUDENT SIMULATION ===\n")

passed = 0
failed = 0

for student in test_students:
    print(f"\n--- {student['name']} ---")
    token = register_student(student)

    if not token:
        print(f"  FAILED to get token")
        failed += 1
        continue

    scenarios = quiz_scenarios.get(student["email"], [])
    for question_id, answer, time_taken in scenarios:
        result = submit_answer(token, question_id, answer, time_taken)
        correct = result.get("is_correct", False)
        score = result.get("ability_score", 0)
        difficulty = result.get("next_difficulty", "N/A")
        mastery = result.get("is_mastery", False)
        struggle = result.get("is_struggle", False)
        status = "MASTERY" if mastery else "STRUGGLE" if struggle else ""
        print(f"  Q{question_id}: {'✓' if correct else '✗'} | Score: {score} | Next: {difficulty} {status}")

    report = get_report(token)
    recs = get_recommendations(token)

    print(f"  Final: {report['total_attempts']} attempts | {report['accuracy']}% accuracy")
    print(f"  Recommendations:")
    for rec in recs.get("recommendations", []):
        print(f"    → {rec['title']} ({rec['difficulty']})")

    passed += 1

print(f"\n=== SIMULATION COMPLETE: {passed}/10 students passed ===\n")