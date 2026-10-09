import json
from datetime import date
from uuid import uuid4


CASEBOOK_FORMAT_VERSION = 1
CASE_TEXT_FIELDS = (
    "case_name",
    "citation",
    "course",
    "topic",
    "year",
    "facts",
    "procedure",
    "issue",
    "rule",
    "holding",
    "reasoning",
    "exam_note",
)
REQUIRED_FIELDS = ("case_name", "course", "facts", "issue", "rule", "holding", "reasoning")


def create_case_brief(
    case_name,
    course,
    facts,
    issue,
    rule,
    holding,
    reasoning,
    citation="",
    topic="",
    year="",
    procedure="",
    exam_note="",
):
    """Validate and normalize a student-authored case brief."""
    values = {
        "case_name": case_name,
        "citation": citation,
        "course": course,
        "topic": topic,
        "year": year,
        "facts": facts,
        "procedure": procedure,
        "issue": issue,
        "rule": rule,
        "holding": holding,
        "reasoning": reasoning,
        "exam_note": exam_note,
    }
    if any(not isinstance(value, str) for value in values.values()):
        raise ValueError("Case brief sections must contain text.")
    clean_values = {field: value.strip() for field, value in values.items()}
    missing = [field.replace("_", " ") for field in REQUIRED_FIELDS if not clean_values[field]]
    if missing:
        raise ValueError(f"Complete the required brief sections: {', '.join(missing)}.")

    return {
        "brief_id": uuid4().hex,
        "added_on": date.today().isoformat(),
        **clean_values,
    }


def filter_case_briefs(briefs, query="", course="All courses", topic="All topics"):
    """Filter briefs by course, topic, and text across their study notes."""
    normalized_query = query.strip().casefold()
    matches = []
    for brief in briefs:
        if course != "All courses" and brief["course"] != course:
            continue
        if topic != "All topics" and brief["topic"] != topic:
            continue
        searchable_text = " ".join(brief[field] for field in CASE_TEXT_FIELDS).casefold()
        if normalized_query and normalized_query not in searchable_text:
            continue
        matches.append(brief)
    return sorted(matches, key=lambda brief: brief["added_on"], reverse=True)


def casebook_to_json(briefs):
    """Serialize case briefs in a versioned, portable JSON backup."""
    payload = {"format_version": CASEBOOK_FORMAT_VERSION, "briefs": briefs}
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def casebook_from_json(content):
    """Parse and validate a casebook backup produced by this app."""
    try:
        payload = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("The backup must be a valid UTF-8 casebook JSON file.") from error

    if not isinstance(payload, dict) or payload.get("format_version") != CASEBOOK_FORMAT_VERSION:
        raise ValueError("This casebook backup has an unsupported format version.")
    raw_briefs = payload.get("briefs")
    if not isinstance(raw_briefs, list) or not raw_briefs:
        raise ValueError("The backup does not contain any case briefs.")

    briefs = []
    for row_number, raw_brief in enumerate(raw_briefs, start=1):
        if not isinstance(raw_brief, dict):
            raise ValueError(f"Invalid case brief at position {row_number}.")
        try:
            brief = create_case_brief(
                **{field: raw_brief.get(field, "") for field in CASE_TEXT_FIELDS}
            )
            brief_id = raw_brief["brief_id"]
            added_on = date.fromisoformat(raw_brief["added_on"])
            if not isinstance(brief_id, str) or not brief_id.strip():
                raise ValueError("The brief ID is missing.")
            brief["brief_id"] = brief_id
            brief["added_on"] = added_on.isoformat()
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid case brief at position {row_number}: {error}") from error
        briefs.append(brief)
    return briefs