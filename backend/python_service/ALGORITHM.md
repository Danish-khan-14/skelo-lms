# Skelo LMS — Adaptive Algorithm Design Note

## Overview
The adaptive engine personalizes learning by tracking each student's ability score and adjusting quiz difficulty in real time.

## 1. Ability Score
- Each student has an ability score per subject on a scale of 0–100
- Default starting score is 50
- Score updates after every quiz attempt using weighted rolling average:

  new_score = (current_score × 0.7) + (performance_value × 0.3)

- performance_value depends on:
  - Whether answer was correct (1.0) or wrong (0.0)
  - Difficulty weight: Easy = 0.3, Medium = 0.6, Hard = 1.0
  - Time penalty: faster answers score higher

## 2. Difficulty Routing
Based on ability score:
- Score 0–44 → Easy questions
- Score 45–74 → Medium questions
- Score 75–100 → Hard questions

## 3. Mastery Detection
- Triggered when student scores >75% on Hard questions 3 times in a row
- System escalates student to advanced topics automatically

## 4. Struggle Detection
- Triggered when accuracy drops below 50% on Easy questions
- System routes student to simplified content path

## 5. Recommendation Engine
Three types of recommendations:
1. Ability-based — topics matching current difficulty level
2. Gap analysis — topics student has never attempted
3. Default — Easy topics for new students

## 6. Analytics
- Class-level analytics track total students, attempts, accuracy by difficulty
- Weak topics identified by lowest correct answer ratio