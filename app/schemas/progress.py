import uuid
from datetime import date
from typing import Optional
from pydantic import BaseModel

from app.models.enums import MuscleGroupEnum


# ---------------------------------------------------------------------------
# Summary
# High-level stats for the selected period
# ---------------------------------------------------------------------------
class SummaryResponse(BaseModel):
    total_sessions: int
    total_volume: float
    current_streak: int


# ---------------------------------------------------------------------------
# Calendar
# Dates the user completed a workout
# ---------------------------------------------------------------------------
class CalendarResponse(BaseModel):
    workout_dates: list[date]


# ---------------------------------------------------------------------------
# Exercise Progress
# One data point per period (week or month) for a specific exercise
# Used for: "how has my bench press improved over the last 8 weeks?"
# ---------------------------------------------------------------------------
class ExerciseProgressPoint(BaseModel):
    period_start: date          # start of the week or month
    max_weight: Optional[float] # heaviest weight lifted that period
    total_volume: float         # sum of (actual_reps * actual_weight) across all sets
    total_sets: int             # how many sets were logged


class ExerciseProgressResponse(BaseModel):
    exercise_id: uuid.UUID
    exercise_name: str
    data: list[ExerciseProgressPoint]


# ---------------------------------------------------------------------------
# Workout Frequency
# One data point per period showing how many sessions the user completed
# Used for: "how consistent have I been this month?"
# ---------------------------------------------------------------------------
class WorkoutFrequencyPoint(BaseModel):
    period_start: date
    session_count: int
    total_volume: float         # total volume across all sessions that period


class WorkoutFrequencyResponse(BaseModel):
    data: list[WorkoutFrequencyPoint]


# ---------------------------------------------------------------------------
# Muscle Group Volume
# Breakdown of volume per muscle group for a given time range
# Used for: "am I training chest more than back?"
# ---------------------------------------------------------------------------
class MuscleGroupVolumePoint(BaseModel):
    muscle_group: MuscleGroupEnum
    total_volume: float
    total_sets: int


class MuscleGroupVolumeResponse(BaseModel):
    start_date: date
    end_date: date
    data: list[MuscleGroupVolumePoint]


# ---------------------------------------------------------------------------
# Body Metric Trend
# Bodyweight and body fat % over time
# Used for: "am I losing weight while maintaining strength?"
# ---------------------------------------------------------------------------
class BodyMetricPoint(BaseModel):
    recorded_at: date
    weight_kg: Optional[float]
    body_fat_pct: Optional[float]


class BodyMetricTrendResponse(BaseModel):
    data: list[BodyMetricPoint]
