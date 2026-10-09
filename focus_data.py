import csv
import io
from datetime import date, timedelta


CSV_FIELDS = ("date", "subject", "focus_minutes", "notes")


def create_session(session_date, subject, focus_minutes, notes=""):
    """Validate and normalize one completed focus session."""
    clean_subject = subject.strip()
    if not clean_subject:
        raise ValueError("Add a subject or project before saving a session.")
    if not 1 <= focus_minutes <= 600:
        raise ValueError("Focus time must be between 1 and 600 minutes.")

    return {
        "date": session_date.isoformat(),
        "subject": clean_subject,
        "focus_minutes": int(focus_minutes),
        "notes": notes.strip(),
    }


def weekly_summary(sessions, today, weekly_goal_minutes):
    """Summarize sessions from Monday through Sunday of the current week."""
    if weekly_goal_minutes < 1:
        raise ValueError("The weekly goal must be at least one minute.")

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    daily_minutes = {week_start + timedelta(days=offset): 0 for offset in range(7)}
    week_sessions = []

    for session in sessions:
        session_day = date.fromisoformat(session["date"])
        if week_start <= session_day <= week_end:
            week_sessions.append(session)
            daily_minutes[session_day] += int(session["focus_minutes"])

    total_minutes = sum(daily_minutes.values())
    return {
        "week_start": week_start,
        "week_end": week_end,
        "total_minutes": total_minutes,
        "session_count": len(week_sessions),
        "subject_count": len({session["subject"] for session in week_sessions}),
        "active_days": sum(minutes > 0 for minutes in daily_minutes.values()),
        "goal_progress": min(total_minutes / weekly_goal_minutes, 1.0),
        "daily_minutes": daily_minutes,
        "sessions": week_sessions,
    }


def sessions_to_csv(sessions):
    """Serialize sessions into a UTF-8 CSV suitable for downloading."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    writer.writerows(sessions)
    return output.getvalue().encode("utf-8")


def sessions_from_csv(content):
    """Parse and validate a CSV backup created by this app."""
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("The backup must be a UTF-8 CSV file.") from error

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or not set(CSV_FIELDS).issubset(reader.fieldnames):
        raise ValueError("The CSV must include date, subject, focus_minutes, and notes columns.")

    sessions = []
    for row_number, row in enumerate(reader, start=2):
        try:
            session_date = date.fromisoformat(row["date"].strip())
            focus_minutes = int(row["focus_minutes"])
            session = create_session(
                session_date,
                row["subject"],
                focus_minutes,
                row["notes"] or "",
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid session on CSV row {row_number}: {error}") from error
        sessions.append(session)

    if not sessions:
        raise ValueError("The CSV does not contain any sessions.")
    return sessions