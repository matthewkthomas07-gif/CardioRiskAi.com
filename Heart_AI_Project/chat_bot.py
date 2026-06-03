"""Conversational assistant that collects patient data in plain language."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

# Typical values when the user skips clinic-only tests (UCI cohort medians/modes).
CLINICAL_DEFAULTS: dict[str, int | float] = {
    "Cholesterol": 240,
    "RestingECG": 0,
    "Oldpeak": 0.0,
    "Slope": 1,
    "NumVessels": 0,
    "Thal": 2,
}

# (field_key, prompt, type, allow_skip)
FIELD_FLOW: list[tuple[str, str, type, bool]] = [
    (
        "Age",
        "How old are you? Enter your age in **years** (example: 55).",
        int,
        False,
    ),
    (
        "Sex",
        "Are you **female** or **male**? (You can also type woman/man.)",
        int,
        False,
    ),
    (
        "ChestPain",
        "Do you have chest discomfort? Pick the closest match:\n"
        "- **typical** — tight pain with exertion, eases with rest\n"
        "- **atypical** — chest pain that does not fit the classic pattern\n"
        "- **non-anginal** — discomfort that does not feel like angina\n"
        "- **none** — no chest pain\n\n"
        "Reply with one word (e.g. `none` or `typical`).",
        int,
        False,
    ),
    (
        "SystolicBP",
        "What is your **systolic** blood pressure — the **top** number? "
        "(Use a home cuff after resting 5 minutes, or your latest clinic reading. Example: 120)",
        int,
        False,
    ),
    (
        "FastingBS",
        "After fasting overnight, was your blood sugar **over 120 mg/dL**? Reply **yes** or **no**. "
        "(Home glucose meter or doctor lab.)",
        int,
        False,
    ),
    (
        "ExerciseAngina",
        "Do you get **chest pain when exercising** (stairs, brisk walking)? Reply **yes** or **no**.",
        int,
        False,
    ),
    (
        "MaxHR",
        "What is the **highest heart rate** you reach with effort?\n"
        "- From a stress test, use that number.\n"
        "- At home: after brisk stairs for 1 minute, count your pulse for 15 seconds and **multiply by 4**.\n"
        "- Rough estimate: **220 minus your age**.\n\n"
        "Enter a number (example: 150).",
        int,
        False,
    ),
    (
        "Cholesterol",
        "Cholesterol from a **blood lab** in mg/dL (example: 200). "
        "No recent lab? Type **skip** — we will use a typical value. For real care, ask your doctor for a lipid test.",
        int,
        True,
    ),
    (
        "RestingECG",
        "If you have a **resting ECG** report, which best matches?\n"
        "- **normal**\n"
        "- **abnormal** — ST-T changes\n"
        "- **thick** — left ventricular hypertrophy\n\n"
        "No ECG? Type **skip** (only book a doctor visit if you have symptoms that worry you).",
        int,
        True,
    ),
    (
        "Oldpeak",
        "From an **exercise stress test**, what is the **ST depression** number (often labeled Oldpeak)? "
        "Example: 0 or 1.5. No test? Type **skip**.",
        float,
        True,
    ),
    (
        "Slope",
        "On a stress test, was the ST segment **up**, **flat**, or **down** at peak exercise? "
        "Reply `up`, `flat`, or `down`. No test? Type **skip**.",
        int,
        True,
    ),
    (
        "NumVessels",
        "If imaging showed narrowed heart arteries, how many (**0–3**)? "
        "No imaging? Type **skip**.",
        int,
        True,
    ),
    (
        "Thal",
        "If you had a **blood-flow heart scan**, was it **normal**, **fixed defect**, or **reversible defect**? "
        "No scan? Type **skip**.",
        int,
        True,
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

TOTAL_FIELDS = len(FIELD_FLOW)

GREETING = (
    "Hi! I'm **CardioRisk AI**. I'll ask simple questions you can mostly answer at home, "
    "then estimate cardiovascular risk with our trained model.\n\n"
    "**Education only** — not a diagnosis. Type **start** when ready, or **help** anytime."
)

HELP_TEXT = (
    "**Commands:** `start` · `restart` · `help`\n\n"
    "Answer in plain words (yes/no, female/male, or a number). "
    "For hospital-only tests, type **skip** if you do not have results.\n\n"
    "See the **Medical terms** section on this page for how to count each measurement."
)


def _is_skip(text: str) -> bool:
    cleaned = text.strip().lower()
    return cleaned in (
        "skip",
        "don't know",
        "dont know",
        "unknown",
        "idk",
        "n/a",
        "na",
        "no test",
        "not sure",
    )


def _parse_chest_pain(text: str) -> int | None:
    cleaned = text.strip().lower()
    mapping = {
        "typical": 0,
        "0": 0,
        "atypical": 1,
        "1": 1,
        "non-anginal": 2,
        "nonanginal": 2,
        "non anginal": 2,
        "2": 2,
        "none": 3,
        "no": 3,
        "no pain": 3,
        "3": 3,
    }
    for key, val in mapping.items():
        if key in cleaned:
            return val
    return None


def _parse_resting_ecg(text: str) -> int | None:
    cleaned = text.strip().lower()
    if any(w in cleaned for w in ("normal", "ok", "fine", "0")):
        return 0
    if any(w in cleaned for w in ("abnormal", "st-t", "st t", "1")):
        return 1
    if any(w in cleaned for w in ("thick", "hypertrophy", "lvh", "2")):
        return 2
    return None


def _parse_slope(text: str) -> int | None:
    cleaned = text.strip().lower()
    if "up" in cleaned or cleaned == "0":
        return 0
    if "flat" in cleaned or cleaned == "1":
        return 1
    if "down" in cleaned or cleaned == "2":
        return 2
    return None


def _parse_thal(text: str) -> int | None:
    cleaned = text.strip().lower()
    if "normal" in cleaned or cleaned == "1":
        return 1
    if "fixed" in cleaned or cleaned == "2":
        return 2
    if "revers" in cleaned or cleaned == "3":
        return 3
    return None


def _parse_value(field: str, text: str, cast: type) -> int | float | None:
    if _is_skip(text):
        return None

    cleaned = text.strip().lower()

    if field == "Sex":
        if cleaned in ("f", "female", "woman", "girl", "0"):
            return 0
        if cleaned in ("m", "male", "man", "boy", "1"):
            return 1

    if field == "ChestPain":
        parsed = _parse_chest_pain(text)
        if parsed is not None:
            return parsed

    if field == "RestingECG":
        parsed = _parse_resting_ecg(text)
        if parsed is not None:
            return parsed

    if field == "Slope":
        parsed = _parse_slope(text)
        if parsed is not None:
            return parsed

    if field == "Thal":
        parsed = _parse_thal(text)
        if parsed is not None:
            return parsed

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


def _risk_explanation(percent: float, used_defaults: list[str]) -> str:
    if percent < 25:
        level = "relatively low"
        tone = "Still talk to a clinician for real decisions."
    elif percent < 50:
        level = "moderate"
        tone = "Consider discussing lifestyle and screening with a healthcare provider."
    else:
        level = "elevated"
        tone = "This model flags higher risk — only a doctor can interpret that for you."

    lines = [
        f"### Your model estimate: **{percent:.1f}%** cardiovascular risk ({level})\n",
        tone,
    ]
    if used_defaults:
        names = ", ".join(f"**{f}**" for f in used_defaults)
        lines.append(
            f"\n\n_Note: You skipped clinic tests for {names}. "
            "We used typical values — results are less precise. "
            "A doctor can run the missing tests for a clearer picture._"
        )
    lines.append("\n\nType **restart** to run another assessment.")
    return "\n".join(lines)


@dataclass
class ChatSession:
    session_id: str
    stage: str = "idle"  # idle | collecting | done
    field_index: int = 0
    data: dict[str, int | float] = field(default_factory=dict)
    used_defaults: list[str] = field(default_factory=list)

    def current_field(self) -> tuple[str, str, type, bool] | None:
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
    total_fields: int = TOTAL_FIELDS


def _reset_session(session: ChatSession) -> None:
    session.stage = "idle"
    session.field_index = 0
    session.data = {}
    session.used_defaults = []


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
        _reset_session(session)
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
            session.used_defaults = []
            name, prompt, _, _ = FIELD_FLOW[0]
            return ChatResult(
                reply=(
                    "Great — I'll keep the language simple. "
                    "Answer with words or numbers; type **skip** only when a question says you may.\n\n"
                    f"**{name}:** {prompt}"
                ),
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
            field_name, prompt, cast, allow_skip = current
            if allow_skip and _is_skip(text):
                default = CLINICAL_DEFAULTS[field_name]
                session.data[field_name] = default
                session.used_defaults.append(field_name)
                session.field_index += 1
                nxt = session.current_field()
                if nxt:
                    next_name, next_prompt, _, _ = nxt
                    return ChatResult(
                        reply=(
                            f"OK — using a typical value for **{field_name}**. "
                            f"You can update this later if you get test results.\n\n"
                            f"**{next_name}:** {next_prompt}"
                        ),
                        session_id=session.session_id,
                        stage=session.stage,
                        collected=session.data,
                    )
            else:
                value = _parse_value(field_name, text, cast)
                if value is None:
                    lo, hi = FIELD_LIMITS[field_name]
                    skip_hint = (
                        "\n\nOr type **skip** if you do not have this test."
                        if allow_skip
                        else ""
                    )
                    return ChatResult(
                        reply=(
                            f"I couldn't use that for **{field_name}**. "
                            f"Please enter a number between **{lo}** and **{hi}**, "
                            f"or use the wording in the question.{skip_hint}\n\n{prompt}"
                        ),
                        session_id=session.session_id,
                        stage=session.stage,
                        collected=session.data,
                    )
                session.data[field_name] = value
                session.field_index += 1
                nxt = session.current_field()
                if nxt:
                    next_name, next_prompt, _, _ = nxt
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
            reply=_risk_explanation(percent, session.used_defaults),
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
        session.used_defaults = []
        name, prompt, _, _ = FIELD_FLOW[0]
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
