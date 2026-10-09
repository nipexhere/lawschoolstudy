from datetime import date

import pandas as pd
import streamlit as st

from casebook_data import (
    casebook_from_json,
    casebook_to_json,
    create_case_brief,
    filter_case_briefs,
)
from focus_data import create_session, sessions_from_csv, sessions_to_csv, weekly_summary


st.set_page_config(
    page_title="Casebook Studio",
    page_icon=":material/menu_book:",
    layout="wide",
)

st.session_state.setdefault("case_briefs", [])
st.session_state.setdefault("sessions", [])
st.session_state.setdefault("weekly_goal_hours", 8)
st.session_state.setdefault("revealed_brief_id", None)

with st.sidebar:
    st.title("Casebook Studio", anchor=False)
    st.caption("Brief cases. Keep the rule. Practice recalling it.")
    st.number_input(
        "Weekly study goal (hours)",
        min_value=1,
        max_value=80,
        step=1,
        key="weekly_goal_hours",
    )
    st.caption("Notes are kept for this browser session. Download backups before leaving.")
    st.download_button(
        "Export casebook",
        data=casebook_to_json(st.session_state.case_briefs),
        file_name=f"casebook-{date.today().isoformat()}.json",
        mime="application/json",
        icon=":material/download:",
        disabled=not st.session_state.case_briefs,
        width="stretch",
    )
    st.download_button(
        "Export study log",
        data=sessions_to_csv(st.session_state.sessions),
        file_name=f"study-log-{date.today().isoformat()}.csv",
        mime="text/csv",
        icon=":material/table_view:",
        disabled=not st.session_state.sessions,
        width="stretch",
    )
    backup_file = st.file_uploader("Import a casebook or study log", type=["json", "csv"])
    if st.button("Import backup", disabled=backup_file is None, width="stretch"):
        try:
            if backup_file.name.lower().endswith(".json"):
                imported_briefs = casebook_from_json(backup_file.getvalue())
                known_ids = {brief["brief_id"] for brief in st.session_state.case_briefs}
                new_briefs = [brief for brief in imported_briefs if brief["brief_id"] not in known_ids]
                st.session_state.case_briefs.extend(new_briefs)
                st.success(f"Added {len(new_briefs)} case brief(s).")
            else:
                imported_sessions = sessions_from_csv(backup_file.getvalue())
                st.session_state.sessions.extend(imported_sessions)
                st.success(f"Added {len(imported_sessions)} study session(s).")
        except ValueError as error:
            st.error(str(error))

summary = weekly_summary(
    st.session_state.sessions,
    date.today(),
    st.session_state.weekly_goal_hours * 60,
)
case_briefs = st.session_state.case_briefs
courses = sorted({brief["course"] for brief in case_briefs})


def case_picker_options(briefs):
    labels = {}
    counts = {}
    for brief in briefs:
        parts = [brief["case_name"], brief["course"]]
        if brief["citation"]:
            parts.append(brief["citation"])
        label = " · ".join(parts)
        counts[label] = counts.get(label, 0) + 1
        if counts[label] > 1:
            label = f"{label} ({counts[label]})"
        labels[label] = brief
    return labels


st.title("Law school, organized.", icon=":material/menu_book:")
st.caption(
    "Casebook Studio helps Nigerian Law School students turn assigned cases and class notes "
    "into organized briefs, then practice recalling the rules before exam day."
)

with st.container(horizontal=True):
    st.metric("Cases briefed", len(case_briefs), border=True)
    st.metric("Courses", len(courses), border=True)
    st.metric("Focused this week", f"{summary['total_minutes'] / 60:.1f} h", border=True)
    st.metric("Study days", f"{summary['active_days']} / 7", border=True)

st.progress(
    summary["goal_progress"],
    text=(
        f"Weekly study goal · {summary['total_minutes'] / 60:.1f} of "
        f"{st.session_state.weekly_goal_hours} hours"
    ),
)

library_tab, new_brief_tab, recall_tab, study_tab = st.tabs(
    ["Case library", "New brief", "Active recall", "Study log"]
)

with library_tab:
    st.subheader("Your case library", icon=":material/library_books:")
    if not case_briefs:
        st.info("Start with a case from your reading. Your briefs will be searchable by course and topic.")
    else:
        search_column, course_column, topic_column = st.columns([1.5, 1, 1])
        with search_column:
            case_query = st.text_input(
                "Search case briefs",
                placeholder="Search facts, rules, holdings, notes...",
                type="search",
                key="case_search",
            )
        with course_column:
            selected_course = st.selectbox("Course", ["All courses", *courses], key="library_course")
        topics = sorted({brief["topic"] for brief in case_briefs if brief["topic"]})
        with topic_column:
            selected_topic = st.selectbox("Topic", ["All topics", *topics], key="library_topic")

        visible_briefs = filter_case_briefs(
            case_briefs,
            query=case_query,
            course=selected_course,
            topic=selected_topic,
        )
        if not visible_briefs:
            st.info("No briefs match those filters.")
        else:
            case_options = case_picker_options(visible_briefs)
            selected_case_label = st.selectbox(
                "Select a case",
                options=list(case_options),
                key="selected_case_id",
            )
            selected_brief = case_options[selected_case_label]
            selected_case_id = selected_brief["brief_id"]
            selected_brief_id = selected_case_id
            citation_line = " · ".join(
                value
                for value in (
                    selected_brief["course"],
                    selected_brief["topic"],
                    selected_brief["citation"],
                    selected_brief["year"],
                )
                if value
            )
            st.caption(citation_line)

            with st.container(border=True):
                facts_column, procedure_column = st.columns(2)
                with facts_column:
                    st.markdown("**Facts**")
                    st.write(selected_brief["facts"])
                with procedure_column:
                    st.markdown("**Procedural posture**")
                    st.write(selected_brief["procedure"] or "Not recorded")
                st.markdown("**Issue**")
                st.write(selected_brief["issue"])
                rule_column, holding_column = st.columns(2)
                with rule_column:
                    st.markdown("**Rule**")
                    st.write(selected_brief["rule"])
                with holding_column:
                    st.markdown("**Holding**")
                    st.write(selected_brief["holding"])
                st.markdown("**Reasoning**")
                st.write(selected_brief["reasoning"])
                if selected_brief["exam_note"]:
                    st.markdown("**Exam connection**")
                    st.write(selected_brief["exam_note"])

            with st.expander("Edit this brief", icon=":material/edit:"):
                with st.form(f"edit_brief_{selected_brief_id}"):
                    edit_columns = st.columns(2)
                    with edit_columns[0]:
                        edit_name = st.text_input(
                            "Case name",
                            value=selected_brief["case_name"],
                            key=f"edit_name_{selected_brief_id}",
                        )
                        edit_course = st.text_input(
                            "Course",
                            value=selected_brief["course"],
                            key=f"edit_course_{selected_brief_id}",
                        )
                        edit_topic = st.text_input(
                            "Topic or doctrine",
                            value=selected_brief["topic"],
                            key=f"edit_topic_{selected_brief_id}",
                        )
                        edit_citation = st.text_input(
                            "Citation",
                            value=selected_brief["citation"],
                            key=f"edit_citation_{selected_brief_id}",
                        )
                        edit_year = st.text_input(
                            "Year",
                            value=selected_brief["year"],
                            key=f"edit_year_{selected_brief_id}",
                        )
                    with edit_columns[1]:
                        edit_facts = st.text_area(
                            "Facts",
                            value=selected_brief["facts"],
                            key=f"edit_facts_{selected_brief_id}",
                        )
                        edit_procedure = st.text_area(
                            "Procedural posture",
                            value=selected_brief["procedure"],
                            key=f"edit_procedure_{selected_brief_id}",
                        )
                    edit_issue = st.text_area(
                        "Issue",
                        value=selected_brief["issue"],
                        key=f"edit_issue_{selected_brief_id}",
                    )
                    edit_rule = st.text_area(
                        "Rule",
                        value=selected_brief["rule"],
                        key=f"edit_rule_{selected_brief_id}",
                    )
                    edit_holding = st.text_area(
                        "Holding",
                        value=selected_brief["holding"],
                        key=f"edit_holding_{selected_brief_id}",
                    )
                    edit_reasoning = st.text_area(
                        "Reasoning",
                        value=selected_brief["reasoning"],
                        key=f"edit_reasoning_{selected_brief_id}",
                    )
                    edit_exam_note = st.text_area(
                        "Exam connection",
                        value=selected_brief["exam_note"],
                        key=f"edit_exam_note_{selected_brief_id}",
                    )
                    save_edit = st.form_submit_button("Save changes", type="primary")

                if save_edit:
                    try:
                        edited_brief = create_case_brief(
                            case_name=edit_name,
                            course=edit_course,
                            topic=edit_topic,
                            citation=edit_citation,
                            year=edit_year,
                            facts=edit_facts,
                            procedure=edit_procedure,
                            issue=edit_issue,
                            rule=edit_rule,
                            holding=edit_holding,
                            reasoning=edit_reasoning,
                            exam_note=edit_exam_note,
                        )
                        edited_brief["brief_id"] = selected_brief_id
                        edited_brief["added_on"] = selected_brief["added_on"]
                        brief_index = next(
                            index
                            for index, brief in enumerate(case_briefs)
                            if brief["brief_id"] == selected_brief_id
                        )
                        case_briefs[brief_index] = edited_brief
                        st.session_state["case_notice"] = "Case brief updated."
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))

            with st.expander("Remove this brief", icon=":material/delete:"):
                confirm_delete = st.checkbox(
                    "I understand this removes the brief from this session.",
                    key=f"confirm_delete_{selected_brief_id}",
                )
                if st.button(
                    "Remove case brief",
                    disabled=not confirm_delete,
                    key=f"delete_brief_{selected_brief_id}",
                ):
                    case_briefs[:] = [
                        brief for brief in case_briefs if brief["brief_id"] != selected_brief_id
                    ]
                    st.rerun()

with new_brief_tab:
    st.subheader("Build a case brief", icon=":material/note_add:")
    st.caption("Use your assigned opinion and class notes as the source of truth.")
    with st.form("new_case_brief", clear_on_submit=True):
        name_column, course_column = st.columns(2)
        with name_column:
            case_name = st.text_input("Case name", key="new_case_name")
            citation = st.text_input("Citation", placeholder="Optional", key="new_citation")
        with course_column:
            course = st.text_input("Course", placeholder="e.g. Civil Procedure", key="new_course")
            topic = st.text_input("Topic or doctrine", placeholder="e.g. Personal jurisdiction", key="new_topic")

        year_column, procedure_column = st.columns(2)
        with year_column:
            year = st.text_input("Year", placeholder="Optional", key="new_year")
        with procedure_column:
            procedure = st.text_input(
                "Procedural posture",
                placeholder="How did the case reach this court?",
                key="new_procedure",
            )

        facts = st.text_area("Key facts", key="new_facts")
        issue = st.text_area("Issue", key="new_issue")
        rule = st.text_area("Rule from your materials", key="new_rule")
        holding = st.text_area("Holding", key="new_holding")
        reasoning = st.text_area("Court's reasoning", key="new_reasoning")
        exam_note = st.text_area(
            "Exam connection",
            placeholder="What distinction, trigger, or counterargument should you remember?",
            key="new_exam_note",
        )
        submitted = st.form_submit_button(
            "Save case brief",
            type="primary",
            icon=":material/bookmark_add:",
            width="stretch",
        )

    if submitted:
        try:
            case_briefs.append(
                create_case_brief(
                    case_name=case_name,
                    course=course,
                    topic=topic,
                    citation=citation,
                    year=year,
                    facts=facts,
                    procedure=procedure,
                    issue=issue,
                    rule=rule,
                    holding=holding,
                    reasoning=reasoning,
                    exam_note=exam_note,
                )
            )
            st.session_state["case_notice"] = "Case brief saved to your library."
            st.rerun()
        except ValueError as error:
            st.error(str(error))

with recall_tab:
    st.subheader("Retrieve before you review", icon=":material/psychology:")
    st.caption("Try to state the issue, rule, and holding from memory before revealing your notes.")
    if not case_briefs:
        st.info("Add a case brief first to build your own recall practice set.")
    else:
        recall_courses = ["All courses", *courses]
        recall_course = st.selectbox("Practice course", recall_courses, key="recall_course")
        recall_briefs = [
            brief for brief in case_briefs
            if recall_course == "All courses" or brief["course"] == recall_course
        ]
        recall_options = case_picker_options(recall_briefs)
        recall_brief_label = st.selectbox(
            "Choose a case",
            options=list(recall_options),
            key="recall_brief_id",
        )
        recall_brief = recall_options[recall_brief_label]
        recall_brief_id = recall_brief["brief_id"]
        with st.container(border=True):
            st.markdown("**Facts to work from**")
            st.write(recall_brief["facts"])
            if recall_brief["procedure"]:
                st.markdown("**Procedural posture**")
                st.write(recall_brief["procedure"])
        st.text_area(
            "Your issue, rule, and holding from memory",
            placeholder="Write your recall attempt before opening the reference notes.",
            key=f"recall_answer_{recall_brief_id}",
        )
        if st.button(
            "Reveal reference notes",
            icon=":material/visibility:",
            key=f"reveal_{recall_brief_id}",
        ):
            st.session_state["revealed_brief_id"] = recall_brief_id
        if st.session_state.revealed_brief_id == recall_brief_id:
            st.markdown("**Issue**")
            st.write(recall_brief["issue"])
            st.markdown("**Rule from your notes**")
            st.write(recall_brief["rule"])
            st.markdown("**Holding**")
            st.write(recall_brief["holding"])
            st.markdown("**Reasoning**")
            st.write(recall_brief["reasoning"])
            if recall_brief["exam_note"]:
                st.markdown("**Exam connection**")
                st.write(recall_brief["exam_note"])

with study_tab:
    st.subheader("Focused study log", icon=":material/timer:")
    log_column, chart_column = st.columns([1, 1.35], gap="large")
    with log_column:
        with st.container(border=True):
            with st.form("session_form", clear_on_submit=True):
                session_date = st.date_input("Study date", value=date.today(), key="session_date")
                if courses:
                    subject = st.selectbox(
                        "Course or subject",
                        courses,
                        accept_new_options=True,
                        key="study_subject",
                    )
                else:
                    subject = st.text_input(
                        "Course or subject",
                        placeholder="e.g. Contracts",
                        key="study_subject",
                    )
                focus_minutes = st.slider(
                    "Focused minutes",
                    min_value=15,
                    max_value=180,
                    value=45,
                    step=15,
                )
                notes = st.text_input("What did you work on?", placeholder="Optional")
                submitted = st.form_submit_button(
                    "Add study session",
                    type="primary",
                    icon=":material/check:",
                    width="stretch",
                )

            if submitted:
                try:
                    st.session_state.sessions.append(
                        create_session(session_date, subject, focus_minutes, notes)
                    )
                    st.session_state["session_notice"] = "Study session added."
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

        if st.session_state.sessions:
            with st.expander("Manage study log", icon=":material/edit:"):
                selected_session = st.selectbox(
                    "Choose a session to remove",
                    options=range(len(st.session_state.sessions)),
                    format_func=lambda index: (
                        f"{st.session_state.sessions[index]['date']} · "
                        f"{st.session_state.sessions[index]['subject']} · "
                        f"{st.session_state.sessions[index]['focus_minutes']} min"
                    ),
                    key="remove_session_index",
                )
                if st.button("Remove selected session", icon=":material/delete:"):
                    st.session_state.sessions.pop(selected_session)
                    st.rerun()

    with chart_column:
        with st.container(border=True):
            st.markdown(
                f"**Week of {summary['week_start'].strftime('%b %d')}** · "
                f"{summary['total_minutes'] / 60:.1f} of "
                f"{st.session_state.weekly_goal_hours} hours"
            )
            daily_rows = [
                {"Day": day.strftime("%a"), "Minutes": minutes}
                for day, minutes in summary["daily_minutes"].items()
            ]
            st.bar_chart(pd.DataFrame(daily_rows), x="Day", y="Minutes", color="#28624D")
            if summary["sessions"]:
                subject_rows = (
                    pd.DataFrame(summary["sessions"])
                    .groupby("subject", as_index=False)["focus_minutes"]
                    .sum()
                    .rename(columns={"subject": "Course", "focus_minutes": "Minutes"})
                    .sort_values("Minutes", ascending=False)
                )
                st.caption("Time by course")
                st.bar_chart(subject_rows, x="Course", y="Minutes", color="#B86C54")

    st.subheader("Recent study sessions", icon=":material/history:")
    if st.session_state.sessions:
        recent_sessions = sorted(
            st.session_state.sessions,
            key=lambda session: (session["date"], session["subject"]),
            reverse=True,
        )[:10]
        recent_table = pd.DataFrame(recent_sessions).rename(
            columns={
                "date": "Date",
                "subject": "Course",
                "focus_minutes": "Minutes",
                "notes": "Notes",
            }
        )
        st.dataframe(recent_table, hide_index=True)
    else:
        st.caption("No study sessions logged yet.")

if notice := st.session_state.pop("case_notice", None):
    st.toast(notice, icon=":material/check_circle:")
if notice := st.session_state.pop("session_notice", None):
    st.toast(notice, icon=":material/check_circle:")