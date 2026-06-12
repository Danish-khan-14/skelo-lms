import numpy as np

DIFFICULTY_WEIGHTS = {
    "Easy": 0.3,
    "Medium": 0.6,
    "Hard": 1.0
}

MASTERY_THRESHOLD = 75.0
STRUGGLE_THRESHOLD = 50.0
MASTERY_CONSECUTIVE_REQUIRED = 3
MAX_ABILITY_SCORE = 100.0
DEFAULT_ABILITY_SCORE = 50.0

def calculate_new_ability_score(
    current_score: float,
    is_correct: bool,
    difficulty: str,
    time_taken_sec: int
) -> float:
    if current_score is None:
        current_score = DEFAULT_ABILITY_SCORE
    difficulty_weight = DIFFICULTY_WEIGHTS.get(difficulty, 0.5)
    time_penalty = max(0, 1 - (time_taken_sec / 120))
    performance_value = (1.0 if is_correct else 0.0) * difficulty_weight * time_penalty * MAX_ABILITY_SCORE
    new_score = (current_score * 0.7) + (performance_value * 0.3)
    return round(float(np.clip(new_score, 0, MAX_ABILITY_SCORE)), 2)

def determine_next_difficulty(ability_score: float) -> str:
    if ability_score is None:
        return "Easy"
    if ability_score >= 75:
        return "Hard"
    elif ability_score >= 45:
        return "Medium"
    else:
        return "Easy"

def detect_mastery(recent_attempts: list) -> bool:
    if not recent_attempts or len(recent_attempts) < MASTERY_CONSECUTIVE_REQUIRED:
        return False
    last_three = recent_attempts[-3:]
    return all(
        attempt.get("is_correct") and
        attempt.get("difficulty") == "Hard" and
        attempt.get("score", 0) > MASTERY_THRESHOLD
        for attempt in last_three
    )

def detect_struggle(recent_attempts: list) -> bool:
    if not recent_attempts or len(recent_attempts) < 3:
        return False
    easy_attempts = [a for a in recent_attempts if a.get("difficulty") == "Easy"]
    if len(easy_attempts) == 0:
        return False
    accuracy = sum(1 for a in easy_attempts if a.get("is_correct")) / len(easy_attempts) * 100
    return accuracy < STRUGGLE_THRESHOLD

def calculate_accuracy_trend(recent_scores: list) -> float:
    if not recent_scores or len(recent_scores) < 2:
        return 0.0
    scores_array = np.array(recent_scores)
    trend = float(np.mean(np.diff(scores_array)))
    return round(trend, 2)