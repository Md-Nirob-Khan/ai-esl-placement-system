import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="AI-Based ESL Placement & Admission System",
    page_icon="🎓",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: #0b1220;
    color: white;
}
.header-card {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    padding: 28px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
}
.card {
    background: #ffffff;
    color: #111827;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
}
.card h3, .card h2, .card p {
    color: #111827;
}
.level-card {
    background: linear-gradient(135deg, #16a34a, #22c55e);
    color: white;
    padding: 22px;
    border-radius: 18px;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
}
.warning-card {
    background: linear-gradient(135deg, #f97316, #facc15);
    color: #111827;
    padding: 18px;
    border-radius: 16px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Database ----------------
conn = sqlite3.connect("esl_full_system.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE,
    name TEXT,
    email TEXT,
    age INTEGER,
    phone TEXT,
    previous_level TEXT,
    enrollment_no TEXT,
    registration_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    correct_answer TEXT,
    mark INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    grammar_score INTEGER,
    vocabulary_score INTEGER,
    reading_score INTEGER,
    speaking_score INTEGER,
    total_score INTEGER,
    recommended_level TEXT,
    weakness TEXT,
    test_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS accounting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    payment_status TEXT,
    amount REAL,
    payment_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS financial_aid (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    aid_status TEXT,
    aid_percentage INTEGER,
    note TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    final_status TEXT,
    approved_level TEXT,
    officer_note TEXT,
    approval_date TEXT
)
""")

conn.commit()

# ---------------- Default Questions ----------------
cursor.execute("SELECT COUNT(*) FROM questions")
if cursor.fetchone()[0] == 0:
    default_questions = [
        ("Grammar", "I ___ a student.", "am", "is", "are", "am", 10),
        ("Grammar", "She ___ going to school.", "are", "is", "am", "is", 10),
        ("Grammar", "Past tense of 'go' is:", "goed", "went", "goes", "went", 5),
        ("Vocabulary", "Opposite of 'big' is:", "small", "tall", "long", "small", 10),
        ("Vocabulary", "Synonym of 'happy' is:", "sad", "glad", "angry", "glad", 10),
        ("Vocabulary", "'Fast' means:", "quick", "slow", "weak", "quick", 5),
        ("Reading", "Maria studies English every day. What does Maria study?", "Math", "English", "Science", "English", 10),
        ("Reading", "Why does Maria study English?", "To improve communication", "To play games", "To sleep", "To improve communication", 10),
        ("Reading", "How often does Maria study English?", "Every day", "Once a month", "Never", "Every day", 5),
    ]
    cursor.executemany("""
    INSERT INTO questions(section, question, option1, option2, option3, correct_answer, mark)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, default_questions)
    conn.commit()

# ---------------- Functions ----------------
def get_level(score):
    if score <= 25:
        return "Level 1 - Beginner"
    elif score <= 50:
        return "Level 2 - Elementary"
    elif score <= 75:
        return "Level 3 - Intermediate"
    else:
        return "Level 4 - Advanced"

def weakness_analysis(grammar, vocabulary, reading, speaking):
    weak = []
    if grammar < 15:
        weak.append("Grammar")
    if vocabulary < 15:
        weak.append("Vocabulary")
    if reading < 15:
        weak.append("Reading")
    if speaking < 15:
        weak.append("Speaking")
    if not weak:
        return "Good overall performance. Student is ready for higher-level ESL learning."
    return "Need improvement in: " + ", ".join(weak)

def load_table(table):
    return pd.read_sql_query(f"SELECT * FROM {table}", conn)

# ---------------- Header ----------------
st.markdown("""
<div class="header-card">
<h1>🎓 AI-Based ESL Placement & Admission System</h1>
<p>DFD-based full system: Registration, Faculty, Test, Evaluation, Accounting, Financial Aid, Admission Office and Reports.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
st.sidebar.title("📌 System Menu")
menu = st.sidebar.radio("Select Module", [
    "🏠 Dashboard",
    "👨‍🎓 Student Registration",
    "👩‍🏫 Faculty Panel",
    "📝 Placement Test",
    "💰 Accounting",
    "💵 Financial Aid",
    "🏫 Admission Office",
    "📊 Records & Reports"
])

# ---------------- Dashboard ----------------
if menu == "🏠 Dashboard":
    students = load_table("students")
    results = load_table("results")
    admission = load_table("admission")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"<div class='card'><h3>👨‍🎓 Total Students</h3><h2>{len(students)}</h2></div>", unsafe_allow_html=True)
    with c2:
        avg = round(results["total_score"].mean(), 2) if not results.empty else 0
        st.markdown(f"<div class='card'><h3>📈 Average Score</h3><h2>{avg}</h2></div>", unsafe_allow_html=True)
    with c3:
        approved = len(admission[admission["final_status"] == "Approved"]) if not admission.empty else 0
        st.markdown(f"<div class='card'><h3>✅ Approved</h3><h2>{approved}</h2></div>", unsafe_allow_html=True)
    with c4:
        highest = results["total_score"].max() if not results.empty else 0
        st.markdown(f"<div class='card'><h3>🏆 Highest Score</h3><h2>{highest}</h2></div>", unsafe_allow_html=True)

    st.markdown("## 📊 Analytics")

    if results.empty:
        st.warning("No test result found yet.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            level_count = results["recommended_level"].value_counts().reset_index()
            level_count.columns = ["Level", "Count"]
            fig = px.pie(level_count, names="Level", values="Count", title="ESL Level Distribution")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(results, x="student_id", y="total_score", color="recommended_level", title="Student Score Comparison")
            st.plotly_chart(fig2, use_container_width=True)

# ---------------- Student Registration ----------------
elif menu == "👨‍🎓 Student Registration":
    st.header("👨‍🎓 Student Registration")

    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("Student ID")
        name = st.text_input("Student Name")
        email = st.text_input("Email")
    with col2:
        age = st.number_input("Age", min_value=10, max_value=80, step=1)
        phone = st.text_input("Phone")
        previous_level = st.selectbox("Previous English Background", ["None", "Basic", "Intermediate", "Advanced"])

    if st.button("Register Student"):
        if student_id == "" or name == "":
            st.error("Student ID and Name are required.")
        else:
            enrollment_no = "ENR-" + student_id
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                cursor.execute("""
                INSERT INTO students(student_id, name, email, age, phone, previous_level, enrollment_no, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_id, name, email, age, phone, previous_level, enrollment_no, date))
                conn.commit()
                st.success(f"Student registered successfully. Enrollment No: {enrollment_no}")
            except:
                st.error("This Student ID already exists.")

# ---------------- Faculty Panel ----------------
elif menu == "👩‍🏫 Faculty Panel":
    st.header("👩‍🏫 Faculty Question Management")

    st.subheader("Add New Question")

    section = st.selectbox("Section", ["Grammar", "Vocabulary", "Reading"])
    question = st.text_area("Question")
    option1 = st.text_input("Option 1")
    option2 = st.text_input("Option 2")
    option3 = st.text_input("Option 3")
    correct = st.text_input("Correct Answer")
    mark = st.number_input("Mark", min_value=1, max_value=25, value=5)

    if st.button("Add Question"):
        if question == "" or correct == "":
            st.error("Question and correct answer required.")
        else:
            cursor.execute("""
            INSERT INTO questions(section, question, option1, option2, option3, correct_answer, mark)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (section, question, option1, option2, option3, correct, mark))
            conn.commit()
            st.success("Question added successfully.")

    st.subheader("Question Bank")
    st.dataframe(load_table("questions"), use_container_width=True)

# ---------------- Placement Test ----------------
elif menu == "📝 Placement Test":
    st.header("📝 Placement Test")

    students = load_table("students")
    if students.empty:
        st.warning("Please register a student first.")
    else:
        selected_student = st.selectbox("Select Student ID", students["student_id"].tolist())

        questions = load_table("questions")
        grammar = vocabulary = reading = 0

        answers = {}

        for _, q in questions.iterrows():
           st.markdown(f"""
<div style="
    background:#ffffff;
    color:#111827;
    padding:18px;
    border-radius:14px;
    margin-top:18px;
    margin-bottom:10px;
    border-left:6px solid #2563eb;
">
    <h4 style="margin:0; color:#2563eb;">{q['section']} Section</h4>
    <p style="font-size:18px; font-weight:700; margin-top:8px;">
        {q['question']}
    </p>
</div>
""", unsafe_allow_html=True)
           ans = st.radio(
                  "Choose answer",
                    [q["option1"], q["option2"], q["option3"]],
                    index=None,
                    key=f"q_{q['id']}"
                    )
        answers[q["id"]] = ans

speaking = st.number_input(
    "Speaking Confidence / Oral Assessment Score (0-25)",
    min_value=0,
    max_value=25,
    value=10,
    step=1
)

if st.button("Submit Test"):
        if st.button("Submit Test"):
            for _, q in questions.iterrows():
              if answers[q["id"]] is not None and answers[q["id"]] == q["correct_answer"]:
                    if q["section"] == "Grammar":
                        grammar += q["mark"]
                    elif q["section"] == "Vocabulary":
                        vocabulary += q["mark"]
                    elif q["section"] == "Reading":
                        reading += q["mark"]

            total = grammar + vocabulary + reading + speaking
            level = get_level(total)
            weakness = weakness_analysis(grammar, vocabulary, reading, speaking)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
            INSERT INTO results(student_id, grammar_score, vocabulary_score, reading_score, speaking_score, total_score, recommended_level, weakness, test_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (selected_student, grammar, vocabulary, reading, speaking, total, level, weakness, date))
            conn.commit()

            st.success("Test evaluated successfully.")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Grammar", grammar)
            c2.metric("Vocabulary", vocabulary)
            c3.metric("Reading", reading)
            c4.metric("Speaking", speaking)
            c5.metric("Total", total)

            st.progress(total / 100)

            st.markdown(f"<div class='level-card'>Recommended ESL Level: {level}</div>", unsafe_allow_html=True)
            st.markdown("### 🤖 AI-Based Weakness Analysis")
            st.markdown(f"<div class='warning-card'>{weakness}</div>", unsafe_allow_html=True)

            score_df = pd.DataFrame({
                "Section": ["Grammar", "Vocabulary", "Reading", "Speaking"],
                "Score": [grammar, vocabulary, reading, speaking]
            })
            fig = px.bar(score_df, x="Section", y="Score", title="Section-wise Score Analysis", text="Score")
            st.plotly_chart(fig, use_container_width=True)

# ---------------- Accounting ----------------
elif menu == "💰 Accounting":
    st.header("💰 Accounting / Payment Status")

    students = load_table("students")
    if students.empty:
        st.warning("No student registered.")
    else:
        student_id = st.selectbox("Select Student ID", students["student_id"].tolist())
        payment_status = st.selectbox("Payment Status", ["Paid", "Pending", "Partial"])
        amount = st.number_input("Amount", min_value=0.0, step=10.0)

        if st.button("Save Payment Status"):
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO accounting(student_id, payment_status, amount, payment_date)
            VALUES (?, ?, ?, ?)
            """, (student_id, payment_status, amount, date))
            conn.commit()
            st.success("Payment status saved.")

    st.subheader("Payment Records")
    st.dataframe(load_table("accounting"), use_container_width=True)

# ---------------- Financial Aid ----------------
elif menu == "💵 Financial Aid":
    st.header("💵 Financial Aid Office")

    students = load_table("students")
    if students.empty:
        st.warning("No student registered.")
    else:
        student_id = st.selectbox("Select Student ID", students["student_id"].tolist())
        aid_status = st.selectbox("Financial Aid Status", ["Eligible", "Not Eligible", "Under Review"])
        aid_percentage = st.slider("Aid Percentage", 0, 100, 0)
        note = st.text_area("Note")

        if st.button("Save Financial Aid Info"):
            cursor.execute("""
            INSERT INTO financial_aid(student_id, aid_status, aid_percentage, note)
            VALUES (?, ?, ?, ?)
            """, (student_id, aid_status, aid_percentage, note))
            conn.commit()
            st.success("Financial aid information saved.")

    st.subheader("Financial Aid Records")
    st.dataframe(load_table("financial_aid"), use_container_width=True)

# ---------------- Admission Office ----------------
elif menu == "🏫 Admission Office":
    st.header("🏫 Admission Office Final Approval")

    results = load_table("results")

    if results.empty:
        st.warning("No test result found.")
    else:
        student_id = st.selectbox("Select Student ID", results["student_id"].unique().tolist())

        latest_result = results[results["student_id"] == student_id].iloc[-1]
        recommended_level = latest_result["recommended_level"]

        st.info(f"Recommended Level: {recommended_level}")
        final_status = st.selectbox("Final Admission Status", ["Approved", "Pending", "Rejected"])
        approved_level = st.selectbox(
            "Approved ESL Level",
            ["Level 1 - Beginner", "Level 2 - Elementary", "Level 3 - Intermediate", "Level 4 - Advanced"],
            index=["Level 1 - Beginner", "Level 2 - Elementary", "Level 3 - Intermediate", "Level 4 - Advanced"].index(recommended_level)
        )
        officer_note = st.text_area("Officer Note")

        if st.button("Save Admission Decision"):
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO admission(student_id, final_status, approved_level, officer_note, approval_date)
            VALUES (?, ?, ?, ?, ?)
            """, (student_id, final_status, approved_level, officer_note, date))
            conn.commit()
            st.success("Admission decision saved successfully.")

    st.subheader("Admission Decisions")
    st.dataframe(load_table("admission"), use_container_width=True)

# ---------------- Records & Reports ----------------
elif menu == "📊 Records & Reports":
    st.header("📊 Records & Reports")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Students",
        "Questions",
        "Results",
        "Accounting",
        "Financial Aid",
        "Admission"
    ])

    with tab1:
        df = load_table("students")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Students CSV", df.to_csv(index=False), "students.csv")

    with tab2:
        df = load_table("questions")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Questions CSV", df.to_csv(index=False), "questions.csv")

    with tab3:
        df = load_table("results")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Results CSV", df.to_csv(index=False), "results.csv")

    with tab4:
        df = load_table("accounting")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Accounting CSV", df.to_csv(index=False), "accounting.csv")

    with tab5:
        df = load_table("financial_aid")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Financial Aid CSV", df.to_csv(index=False), "financial_aid.csv")

    with tab6:
        df = load_table("admission")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download Admission CSV", df.to_csv(index=False), "admission.csv")

    st.markdown("## 📌 ESL Level Criteria")
    level_df = pd.DataFrame({
        "Score Range": ["0–25", "26–50", "51–75", "76–100"],
        "ESL Level": ["Level 1 Beginner", "Level 2 Elementary", "Level 3 Intermediate", "Level 4 Advanced"],
        "Description": [
            "Basic understanding, limited vocabulary, simple sentences",
            "Basic communication, simple texts, developing skills",
            "Good communication, understand main ideas, complex texts",
            "Fluent communication, complex texts, advanced skills"
        ]
    })
    st.table(level_df)