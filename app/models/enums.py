import enum


class ForceEnum(str, enum.Enum):
    pull = "pull"
    push = "push"
    static = "static"


class LevelEnum(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    expert = "expert"


class MuscleGroupEnum(str, enum.Enum):
    abs       = "abs"
    legs      = "legs"
    arms      = "arms"
    shoulders = "shoulders"
    chest     = "chest"
    back      = "back"


class EquipmentEnum(str, enum.Enum):
    body_only = "body_only"
    machine = "machine"
    other = "other"
    foam_roll = "foam_roll"
    kettlebells = "kettlebells"
    dumbbell = "dumbbell"
    cable = "cable"
    barbell = "barbell"
    bands = "bands"
    medicine_ball = "medicine_ball"
    exercise_ball = "exercise_ball"
    ez_curl_bar = "ez_curl_bar"


class SessionStatusEnum(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class SetTypeEnum(str, enum.Enum):
    warmup = "warmup"
    working = "working"
    dropset = "dropset"