# Casebook Studio

**A focused study workspace for Nigerian Law School.** Casebook Studio helps students turn assigned cases and class notes into a searchable, course-organized casebook, practice recalling each case before revealing their notes, and build a steady study routine across a demanding term.

The problem it addresses is familiar: case notes end up scattered across notebooks and documents, rules blur together between courses, and rereading can feel productive without showing what you can actually recall. Casebook Studio gives each case a consistent brief structure, makes those notes searchable, and adds an active-recall step before review. A weekly study log helps students see how they are using their time.

## Study workflow

- **Brief cases:** Capture the facts, procedural posture, issue, rule, holding, reasoning, and your exam connection.
- **Organize your courses:** Add your own course names and topics, then search all brief sections or filter your library.
- **Practice active recall:** Start from the facts, write the issue, rule, and holding from memory, then reveal your own reference notes.
- **Protect study time:** Set a weekly goal and review focused time by day and course.
- **Keep your work portable:** Export or restore the casebook as JSON and the study log as CSV.

Casebook Studio is designed to fit the courses and topics you enter, rather than assume one school timetable or supply generic legal rules. It does not generate legal rules or verify citations. Use your assigned opinions, statutes, course materials, and lecturers as the authority. This is a study tool, not legal advice or a substitute for Nigerian legal research.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment, install dependencies, and start Streamlit:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Run the full test suite:

```bash
python -m unittest discover -v
```

## Publish on GitHub

1. On GitHub, create a new **public** repository named `casebook-studio`. Leave the README, `.gitignore`, and license options unchecked because this project already has those files.
2. In the VS Code terminal, run these commands from the project folder. The local Git repository is already initialized. Use the no-reply email shown in your GitHub email settings if you want your personal email hidden from commits. Replace the placeholders with your own values:

```bash
git config user.name "Your Name"
git config user.email "YOUR_GITHUB_NOREPLY_EMAIL"
git add .
git status --short
git commit -m "Build Casebook Studio law school study app"
git remote add origin https://github.com/YOUR_USERNAME/casebook-studio.git
git push -u origin main
```

Review `git status --short` before committing. The generated backup filenames are ignored by `.gitignore`; do not commit personal notes, credentials, or confidential material.

## Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and select **Create app**.
2. Choose your `casebook-studio` repository, the `main` branch, and `app.py` as the app file.
3. Select **Deploy**. Streamlit installs the app dependencies from `requirements.txt`.
4. Add the public app URL to your portfolio. The source repository and deployed app can both be shared from your portfolio page.

GitHub Actions runs the test suite on pushes and pull requests.

## Data and privacy

Briefs and study sessions stay in Streamlit session state; the app does not write them to a server-side database, and hosted session data may be cleared. Export backups regularly and import them when you return or switch devices. Avoid entering sensitive personal information or confidential client information. Exported backup files are ignored by Git by default.

## Project layout

```text
app.py                    Streamlit user interface
casebook_data.py          Brief validation, search, and JSON backups
focus_data.py             Study-session logic and CSV backups
hello.py                  Companion command-line score manager
test_app.py               Streamlit workflow tests
test_casebook_data.py     Casebook logic tests
test_focus_data.py        Study-log logic tests
test_hello.py             Score-manager tests
requirements.txt          Runtime dependencies
```