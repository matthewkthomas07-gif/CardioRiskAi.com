"""Conversational assistant that collects patient data and runs the risk model."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

FIELD_FLOW: list[tuple[str, str, type]] = [
    ("Age", "How old are you? (years)", int),
    (
        "Sex",
        "What is your sex for this dataset? Reply **0** for female or **1** for male.",
        int,
    ),
    (
        "ChestPain",
        "Chest pain type: **0** = typical angina, **1** = atypical angina, **2** = non-anginal pain, **3** = no chest pain. Enter 0-3.",
        int,
    ),
    ("SystolicBP", "What is your **systolic** blood pressure? (top number, e.g. 120)", int),
    ("Cholesterol", "What is your **serum cholesterol** in mg/dL? (e.g. 200)", int),
    (
        "FastingBS",
        "Fasting blood sugar over 120 mg/dL? Reply **0** for no or **1** for yes.",
        int,
    ),
    (
        "RestingECG",
        "Resting ECG result: **0** = normal, **1** = ST-T abnormality, **2** = left ventricular hypertrophy. Enter 0–2.",
        int,
    ),
    ("MaxHR", "Maximum heart rate reached during exercise? (e.g. 150)", int),
    (
        "ExerciseAngina",
        "Exercise-induced angina? Reply **0** for no or **1** for yes.",
        int,
    ),
    ("Oldpeak", "ST depression (**Oldpeak**) from exercise test? (decimal, e.g. 0.0 or 1.5)", float),
    (
        "Slope",
        "ST segment slope during exercise: **0** = upsloping, **1** = flat, **2** = downsloping.",
        int,
    ),
    (
        "NumVessels",
        "Major vessels (0–3) colored by fluoroscopy. Enter **0**, **1**, **2**, or **3**.",
        int,
    ),
    (
        "Thal",
        "Thalassemia test: **1** = normal, **2** = fixed defect, **3** = reversible defect.",
        int,
    ),
]

FIELD_LIMITS: dict[str, tuple[int | float, int | float]] = {
    "Age": (1, 120),
    "Sex": (0, 1),
    "ChestPain": (0, 3),
    "SystolicBP": (80, 250),
    "Cholesterol": (100, 600),
    "FastingBS": (0, 1),
    "RestingECG": (0, 2),
    "MaxHR": (60, 220),
    "ExerciseAngina": (0, 1),
    "Oldpeak": (0.0, 10.0),
    "Slope": (0, 2),
    "NumVessels": (0, 3),
    "Thal": (1, 3),
}

GREETING = (
    "Hi! I'm **CardioRisk AI**, your guided heart-risk assistant. "
    "I'll ask a few health measurements, then run them through our trained model. "
    "This is for **education only** - not a real diagnosis.\n\n"
    "Type **start** when you're ready, or **help** anytime."
)

HELP_TEXT = (
    "**Commands:** `start` · `restart` · `skip` (not available) · `help`\n\n"
    "Answer each question with a number. I'll validate ranges for you.\n\n"
    "**Disclaimer:** Not medical advice. See a doctor for real concerns."
)


def _parse_value(field: str, text: str, cast: type) -> int | float | None:
    cleaned = text.strip().lower()
    if field == "Sex":
        if cleaned in ("f", "female", "woman", "girl", "0"):
            return 0
        if cleaned in ("m", "male", "man", "boy", "1"):
            return 1
    if field in ("FastingBS", "ExerciseAngina"):
        if cleaned in ("yes", "y", "true", "1"):
            return 1
        if cleaned in ("no", "n", "false", "0"):
            return 0
    match = re.search(r"-?\d+\.?\d*", text.replace(",", ""))
    if not match:
        return None
    try:
        value = cast(match.group())
    except ValueError:
        return None
    lo, hi = FIELD_LIMITS[field]
    if value < lo or value > hi:
        return None
    return value


def _risk_explanation(percent: float) -> str:
    if percent < 25:
        level = "relatively low"
        tone = "Still talk to a clinician for real decisions."
    elif percent < 50:
        level = "moderate"
        tone = "Consider discussing lifestyle and screening with a healthcare provider."
    else:
        level = "elevated"
        tone = "This model flags higher risk - only a doctor can interpret that for you."
    return (
        f"### Your model estimate: **{percent:.1f}%** cardiovascular risk ({level})\n\n"
        f"{tone}\n\n"
        "Type **restart** to run another assessment."
    )


@dataclass
class ChatSession:
    session_id: str
    stage: str = "idle"  # idle | collecting | done
    field_index: int = 0
    data: dict[str, int | float] = field(default_factory=dict)

    def current_field(self) -> tuple[str, str, type] | None:
        if self.field_index >= len(FIELD_FLOW):
            return None
        return FIELD_FLOW[self.field_index]


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}

    def get_or_create(self, session_id: str | None) -> ChatSession:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        new_id = session_id or str(uuid.uuid4())
        session = ChatSession(session_id=new_id)
        self._sessions[new_id] = session
        return session


sessions = SessionStore()


@dataclass
class ChatResult:
    reply: str
    session_id: str
    stage: str
    collected: dict[str, int | float]
    prediction: dict[str, Any] | None = None
    done: bool = False


def handle_message(
    message: str,
    session_id: str | None,
    predict_fn: Callable[[dict[str, int | float]], dict[str, Any]],
) -> ChatResult:
    text = message.strip()
    lower = text.lower()
    session = sessions.get_or_create(session_id)

    if lower in ("help", "?"):
        return ChatResult(
            reply=HELP_TEXT,
            session_id=session.session_id,
            stage=session.stage,
            collected=session.data,
        )

    if lower in ("restart", "reset", "start over"):
        session.stage = "idle"
        session.field_index = 0
        session.data = {}
        return ChatResult(
            reply="Session cleared. Type **start** to begin a new assessment.",
            session_id=session.session_id,
            stage=session.stage,
            collected=session.data,
        )

    if session.stage == "idle":
        if lower in ("start", "hi", "hello", "begin", "go"):
            session.stage = "collecting"
            session.field_index = 0
            session.data = {}
            name, prompt, _ = FIELD_FLOW[0]
            return ChatResult(
                reply=f"Great - let's begin.\n\n**{name}:** {prompt}",
                session_id=session.session_id,
                stage=session.stage,
                collected=session.data,
            )
        return ChatResult(
            reply=GREETING,
            session_id=session.session_id,
            stage=session.stage,
            collected=session.data,
        )

    if session.stage == "collecting":
        current = session.current_field()
        if current is None:
            session.stage = "done"
        else:
            field_name, prompt, cast = current
            value = _parse_value(field_name, text, cast)
            if value is None:
                lo, hi = FIELD_LIMITS[field_name]
                return ChatResult(
                    reply=(
                        f"I couldn't use that answer for **{field_name}**. "
                        f"Please enter a number between **{lo}** and **{hi}**.\n\n{prompt}"
                    ),
                    session_id=session.session_id,
                    stage=session.stage,
                    collected=session.data,
                )
            session.data[field_name] = value
            session.field_index += 1
            nxt = session.current_field()
            if nxt:
                next_name, next_prompt, _ = nxt
                return ChatResult(
                    reply=f"Got it. **{next_name}:** {next_prompt}",
                    session_id=session.session_id,
                    stage=session.stage,
                    collected=session.data,
                )

        try:
            prediction = predict_fn(session.data)
        except Exception as exc:
            session.stage = "collecting"
            return ChatResult(
                reply=f"Something went wrong running the model: {exc}. Type **restart** to try again.",
                session_id=session.session_id,
                stage=session.stage,
                collected=session.data,
            )

        session.stage = "done"
        percent = float(prediction.get("risk_percentage", 0))
        return ChatResult(
            reply=_risk_explanation(percent),
            session_id=session.session_id,
            stage=session.stage,
            collected=session.data,
            prediction=prediction,
            done=True,
        )

    if session.stage == "done" and lower in ("start", "again", "new"):
        session.stage = "collecting"
        session.field_index = 0
        session.data = {}
        name, prompt, _ = FIELD_FLOW[0]
        return ChatResult(
            reply=f"Starting fresh.\n\n**{name}:** {prompt}",
            session_id=session.session_id,
            stage=session.stage,
            collected=session.data,
        )

    return ChatResult(
        reply="Assessment complete. Type **restart** for a new run, or **help** for commands.",
        session_id=session.session_id,
        stage=session.stage,
        collected=session.data,
        done=True,
    )
