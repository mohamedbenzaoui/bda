import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configuration remains the same
EXAM_DURATION = 90
TIME_SLOTS = ["08:30", "11:00", "14:00"]
START_DATE = datetime(2026, 1, 10)
END_DATE = datetime(2026, 1, 25)
MAX_ROOMS_PER_SLOT = 50

ROLES = {
    "vice_dean": "Vice-Dean / Dean",
    "admin_exams": "Exams Administrator",
    "department_head": "Department Head",
    "teacher": "Teacher",
    "student": "Student"
}

st.set_page_config(page_title="Exams Platform", layout="wide", initial_sidebar_state="expanded")

# New 100% design - different colors, different arrangement
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;600;700;900&family=Montserrat:wght@400;600;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Raleway', sans-serif;
}

/* Background with completely different gradient */
.main {
    background: linear-gradient(165deg, #0a0e27 0%, #1e3a5f 35%, #2c5f7c 100%);
    min-height: 100vh;
    padding: 3rem 2rem;
}

/* Main card with square shape instead of circular */
.hero-section {
    background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 50%, #c44569 100%);
    padding: 4rem 3rem;
    margin-bottom: 3rem;
    clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
    box-shadow: 0 25px 50px rgba(255, 107, 107, 0.3);
}

.hero-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 4rem;
    font-weight: 900;
    color: #fff;
    text-align: left;
    line-height: 1.2;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 3px;
}

.hero-description {
    font-size: 1.4rem;
    color: rgba(255,255,255,0.9);
    text-align: left;
    font-weight: 300;
    max-width: 600px;
}

.user-badge-horizontal {
    display: inline-flex;
    align-items: center;
    gap: 1.5rem;
    background: rgba(255,255,255,0.2);
    padding: 1.2rem 2.5rem;
    border-radius: 50px;
    margin-top: 2rem;
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255,255,255,0.3);
}

.user-badge-icon {
    font-size: 2.5rem;
}

.user-badge-text {
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
}

/* Horizontal statistics instead of vertical */
.stats-horizontal {
    display: flex;
    gap: 1.5rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}

.stat-box-horizontal {
    flex: 1;
    min-width: 200px;
    background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
    padding: 2rem;
    border-radius: 15px;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 210, 255, 0.3);
    transition: all 0.3s ease;
}

.stat-box-horizontal:hover {
    transform: scale(1.05) rotate(-2deg);
}

.stat-icon-large {
    font-size: 4rem;
    opacity: 0.9;
}

.stat-content-horizontal {
    flex: 1;
}

.stat-label-horizontal {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8);
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.stat-value-horizontal {
    font-size: 2.8rem;
    font-weight: 900;
    color: white;
}

/* Content box with rectangular shape */
.content-box {
    background: white;
    border-radius: 12px;
    padding: 2.5rem;
    margin: 2rem 0;
    box-shadow: 0 5px 25px rgba(0,0,0,0.15);
    border-left: 8px solid #ff6b6b;
}

/* Section title with underline */
.section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #2c3e50;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 4px solid #ff6b6b;
    text-transform: uppercase;
}

/* Simple design alerts */
.notification-box {
    background: #fff3cd;
    border: 3px solid #ffc107;
    border-radius: 10px;
    padding: 2rem;
    margin: 1.5rem 0;
}

.notification-box.error {
    background: #f8d7da;
    border-color: #dc3545;
}

.notification-box.success {
    background: #d4edda;
    border-color: #28a745;
}

.notification-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
}

.notification-value {
    font-size: 3rem;
    font-weight: 900;
}

/* Completely different exam card - horizontal */
.exam-horizontal-card {
    background: linear-gradient(to right, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
    padding: 1.8rem;
    margin: 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 2rem;
    border: 2px solid #dee2e6;
    transition: all 0.3s ease;
}

.exam-horizontal-card:hover {
    background: linear-gradient(to right, #e3f2fd 0%, #bbdefb 100%);
    border-color: #2196f3;
    transform: translateY(-3px);
}

.exam-time-block {
    background: #ff6b6b;
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    min-width: 120px;
}

.exam-time {
    font-size: 2rem;
    font-weight: 900;
}

.exam-date {
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

.exam-details-flex {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.exam-title-horizontal {
    font-size: 1.6rem;
    font-weight: 700;
    color: #2c3e50;
}

.exam-meta {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
}

.exam-meta-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #495057;
    font-weight: 600;
}

/* Login page - side design */
.login-split-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    min-height: 80vh;
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    margin: 2rem auto;
    max-width: 1200px;
}

.login-left-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 4rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: white;
}

.login-brand {
    font-size: 3.5rem;
    font-weight: 900;
    margin-bottom: 2rem;
}

.login-tagline {
    font-size: 1.4rem;
    line-height: 1.8;
    opacity: 0.95;
}

.login-right-panel {
    padding: 4rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.login-form-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #2c3e50;
    margin-bottom: 2rem;
}

/* Buttons with sharp corners */
.stButton > button {
    background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 1.2rem 3rem;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 6px 20px rgba(17, 153, 142, 0.4);
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #38ef7d 0%, #11998e 100%);
    box-shadow: 0 8px 30px rgba(17, 153, 142, 0.6);
    transform: translateY(-2px);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

.sidebar-profile-box {
    background: rgba(255,255,255,0.1);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    border: 2px solid rgba(255,255,255,0.2);
}

.sidebar-title {
    color: white;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.sidebar-role {
    background: #ff6b6b;
    color: white;
    padding: 1rem;
    border-radius: 8px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
}

.sidebar-name {
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
    text-align: center;
}

/* Different department badge */
.department-header {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 2rem 3rem;
    border-radius: 12px;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
}

.department-name {
    font-size: 2.5rem;
    font-weight: 900;
    text-transform: uppercase;
}

/* Square date badge */
.date-header-box {
    background: #2c3e50;
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 8px;
    margin: 2rem 0;
    font-size: 1.4rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Data table */
.dataframe {
    border-radius: 10px !important;
    border: 2px solid #dee2e6 !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    height: 10px;
    border-radius: 5px;
}

/* Tools grid layout */
.tools-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin: 2rem 0;
}

.tool-card {
    background: white;
    border: 3px solid #e9ecef;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.tool-card:hover {
    border-color: #11998e;
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(17, 153, 142, 0.2);
}

.tool-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
}

.tool-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #2c3e50;
}

/* Charts */
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    margin: 2rem 0;
}

/* Different design for metrics */
.metric-row {
    display: flex;
    gap: 2rem;
    margin: 2rem 0;
}

.metric-simple {
    flex: 1;
    background: white;
    padding: 2rem;
    border-radius: 10px;
    border-top: 5px solid #ff6b6b;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    text-align: center;
}

.metric-simple-label {
    font-size: 0.9rem;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.metric-simple-value {
    font-size: 3rem;
    font-weight: 900;
    color: #2c3e50;
}

/* Responsive for small screens */
@media (max-width: 768px) {
    .login-split-container {
        grid-template-columns: 1fr;
    }
    
    .login-left-panel {
        display: none;
    }
    
    .stats-horizontal {
        flex-direction: column;
    }
    
    .tools-grid {
        grid-template-columns: 1fr;
    }
    
    .metric-row {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)

# Session State
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_dept_id" not in st.session_state:
    st.session_state.user_dept_id = None

# Database functions remain unchanged
def get_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
    except mysql.connector.Error as err:
        st.error(f"❌ Connection error: {err}")
        return None

def execute_query(query, params=None):
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    try:
        if params:
            import numpy as np
            params = tuple(int(p) if isinstance(p, np.integer) else float(p) if isinstance(p, np.floating) else p for p in params)
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"❌ Query error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

@st.cache_data(ttl=300)
def get_departments():
    return execute_query("SELECT id, nom FROM departements ORDER BY nom")

@st.cache_data(ttl=300)
def get_formations_by_dept(dept_id=None):
    if dept_id:
        return execute_query("SELECT id, nom FROM formations WHERE dept_id = %s ORDER BY nom", params=(dept_id,))
    return execute_query("SELECT id, nom, dept_id FROM formations ORDER BY nom")

@st.cache_data(ttl=300)
def get_teachers_by_dept(dept_id=None):
    if dept_id:
        return execute_query("SELECT id, nom FROM professeurs WHERE dept_id = %s ORDER BY nom", params=(dept_id,))
    return execute_query("SELECT id, nom, dept_id FROM professeurs ORDER BY nom")

@st.cache_data(ttl=60)
def load_schedule_complete(dept_id=None, formation_id=None, date_filter=None):
    query = """SELECT e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id, p.nom AS teacher, l.nom AS room, l.capacity, e.date_time, e.duration_minutes, COUNT(DISTINCT i.student_id) AS registered_count, d.nom AS department, d.id AS department_id
    FROM exams e JOIN modules m ON m.id = e.module_id JOIN formations f ON f.id = m.formation_id JOIN departments d ON d.id = f.dept_id JOIN teachers p ON p.id = e.teacher_id JOIN exam_rooms l ON l.id = e.room_id LEFT JOIN registrations i ON i.module_id = e.module_id WHERE 1=1"""
    params = []
    if dept_id:
        query += " AND d.id = %s"
        params.append(dept_id)
    if formation_id:
        query += " AND f.id = %s"
        params.append(formation_id)
    if date_filter:
        query += " AND DATE(e.date_time) = %s"
        params.append(date_filter)
    query += " GROUP BY e.id, m.nom, f.nom, f.id, p.nom, l.nom, l.capacity, e.date_time, e.duration_minutes, d.nom, d.id ORDER BY e.date_time, f.nom"
    return execute_query(query, params=tuple(params) if params else None)

@st.cache_data(ttl=60)
def get_global_kpis():
    kpis = {}
    for key, query in {
        "nb_exams": "SELECT COUNT(*) as val FROM exams",
        "nb_rooms": "SELECT COUNT(*) as val FROM exam_rooms",
        "nb_teachers": "SELECT COUNT(*) as val FROM teachers",
        "nb_students": "SELECT COUNT(*) as val FROM students"
    }.items():
        result = execute_query(query)
        kpis[key] = float(result.iloc[0, 0]) if not result.empty else 0
    return kpis

@st.cache_data(ttl=60)
def get_global_occupancy():
    return execute_query("""SELECT l.nom AS room, l.capacity, COUNT(e.id) AS nb_exams, ROUND(AVG(CASE WHEN ins.registered_count IS NOT NULL THEN (ins.registered_count / l.capacity) * 100 ELSE 0 END), 1) AS occupancy_rate FROM exam_rooms l LEFT JOIN exams e ON e.room_id = l.id LEFT JOIN (SELECT module_id, COUNT(student_id) AS registered_count FROM registrations GROUP BY module_id) ins ON ins.module_id = e.module_id GROUP BY l.id, l.nom, l.capacity ORDER BY occupancy_rate DESC""")

@st.cache_data(ttl=60)
def get_stats_by_department():
    return execute_query("""SELECT d.nom AS department, COUNT(DISTINCT e.id) AS nb_exams, COUNT(DISTINCT m.id) AS nb_modules, COUNT(DISTINCT f.id) AS nb_formations FROM departments d LEFT JOIN formations f ON f.dept_id = d.id LEFT JOIN modules m ON m.formation_id = f.id LEFT JOIN exams e ON e.module_id = m.id GROUP BY d.id, d.nom ORDER BY nb_exams DESC""")

@st.cache_data(ttl=60)
def get_teaching_hours():
    return execute_query("""SELECT p.nom AS teacher, d.nom AS department, COUNT(e.id) AS nb_exams, SUM(e.duration_minutes) / 60 AS total_hours, COUNT(s.exam_id) AS nb_supervisions FROM teachers p JOIN departments d ON d.id = p.dept_id LEFT JOIN exams e ON e.teacher_id = p.id LEFT JOIN supervisions s ON s.teacher_id = p.id GROUP BY p.id, p.nom, d.nom ORDER BY total_hours DESC""")

@st.cache_data(ttl=60)
def get_student_schedule(formation_id):
    return execute_query("""SELECT DISTINCT e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id, p.nom AS teacher, l.nom AS room, l.capacity, e.date_time, e.duration_minutes, COUNT(DISTINCT i.student_id) AS registered_count, d.nom AS department, d.id AS department_id FROM exams e JOIN modules m ON m.id = e.module_id JOIN formations f ON f.id = m.formation_id JOIN departments d ON d.id = f.dept_id JOIN teachers p ON p.id = e.teacher_id JOIN exam_rooms l ON l.id = e.room_id LEFT JOIN registrations i ON i.module_id = e.module_id WHERE f.id = %s GROUP BY e.id, m.nom, f.nom, f.id, p.nom, l.nom, l.capacity, e.date_time, e.duration_minutes, d.nom, d.id ORDER BY e.date_time, f.nom""", params=(formation_id,))

def generate_optimized_schedule():
    conn = get_connection()
    if not conn:
        return 0, 0
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("DELETE FROM exams")
        conn.commit()
        cur.execute("""SELECT m.id AS module_id, m.nom AS module, f.id AS formation_id, f.dept_id AS dept_id, COALESCE(COUNT(DISTINCT i.student_id), 1) AS nb_students FROM modules m JOIN formations f ON f.id = m.formation_id LEFT JOIN registrations i ON i.module_id = m.id GROUP BY m.id, m.nom, f.id, f.dept_id ORDER BY nb_students DESC""")
        modules = cur.fetchall()
        cur.execute("SELECT id, capacity, nom FROM exam_rooms ORDER BY capacity DESC")
        rooms = cur.fetchall()
        cur.execute("SELECT id, nom FROM teachers")
        teachers = cur.fetchall()
        if not modules or not rooms or not teachers:
            st.error("❌ Insufficient data")
            return 0, 0
        students_per_module = {}
        cur.execute("SELECT module_id, student_id FROM registrations")
        for row in cur.fetchall():
            if row['module_id'] not in students_per_module:
                students_per_module[row['module_id']] = []
            students_per_module[row['module_id']].append(row['student_id'])
        progress_bar = st.progress(0)
        status_text = st.empty()
        formation_day, room_time, student_day, rooms_occupied_per_slot = {}, {}, {}, {}
        teacher_exams_count = {p["id"]: 0 for p in teachers}
        success, failed, failed_modules, exams_to_insert = 0, 0, [], []
        for i, module in enumerate(modules):
            progress_bar.progress((i + 1) / len(modules))
            status_text.text(f"⏳ Scheduling: {module['module']} ({i+1}/{len(modules)})")
            scheduled = False
            module_students = students_per_module.get(module["module_id"], [])
            start_idx = i % len(TIME_SLOTS)
            time_slots_priority = TIME_SLOTS[start_idx:] + TIME_SLOTS[:start_idx]
            for day_offset in range((END_DATE - START_DATE).days + 1):
                if scheduled:
                    break
                exam_date = (START_DATE + timedelta(days=day_offset)).date()
                if (module["formation_id"], exam_date) in formation_day:
                    continue
                for hour in time_slots_priority:
                    if scheduled:
                        break
                    dt = datetime.strptime(f"{exam_date} {hour}", "%Y-%m-%d %H:%M")
                    if rooms_occupied_per_slot.get(dt, 0) >= MAX_ROOMS_PER_SLOT:
                        continue
                    if any((student_id, exam_date) in student_day for student_id in module_students):
                        continue
                    for room in rooms:
                        if scheduled:
                            break
                        if room["capacity"] < module["nb_students"]:
                            continue
                        if (room["id"], dt) in room_time:
                            continue
                        teacher_found = sorted(teachers, key=lambda p: teacher_exams_count[p["id"]])[0]
                        exams_to_insert.append((module["module_id"], teacher_found["id"], room["id"], dt, EXAM_DURATION))
                        room_time[(room["id"], dt)] = True
                        formation_day[(module["formation_id"], exam_date)] = True
                        rooms_occupied_per_slot[dt] = rooms_occupied_per_slot.get(dt, 0) + 1
                        teacher_exams_count[teacher_found["id"]] += 1
                        for student_id in module_students:
                            student_day[(student_id, exam_date)] = True
                        success += 1
                        scheduled = True
            if not scheduled:
                failed += 1
                failed_modules.append(module["module"])
        if exams_to_insert:
            cur.executemany("INSERT INTO exams (module_id, teacher_id, room_id, date_time, duration_minutes) VALUES (%s, %s, %s, %s, %s)", exams_to_insert)
            conn.commit()
        progress_bar.empty()
        status_text.empty()
        if failed_modules:
            with st.expander(f"⚠️ Unscheduled modules ({failed})"):
                for mod in failed_modules[:20]:
                    st.write(f"- {mod}")
                if failed > 20:
                    st.write(f"... and {failed - 20} more")
        return success, failed
    except Exception as e:
        conn.rollback()
        st.error(f"❌ Generation error: {e}")
        return 0, 0
    finally:
        conn.close()

# Completely new login page
def login_page():
    st.markdown('<div class="login-split-container">', unsafe_allow_html=True)
    
    # Left panel
    st.markdown("""
        <div class="login-left-panel">
            <div class="login-brand">EXAM SYSTEM</div>
            <div class="login-tagline">
                Advanced platform for university exam management<br>
                Smart scheduling, planning and monitoring system<br>
                Comprehensive digital solutions
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Right panel
    col1, col2 = st.columns([1, 2])
    with col2:
        st.markdown('<div class="login-right-panel"><h2 class="login-form-title">LOGIN</h2>', unsafe_allow_html=True)
        
        role = st.selectbox("Select account type", list(ROLES.values()), key="role_select")
        
        if role == ROLES["vice_dean"]:
            if st.button("Login as Vice-Dean", use_container_width=True, key="login_vd"):
                st.session_state.user_role, st.session_state.user_name = "vice_dean", "Vice-Dean"
                st.rerun()
        
        elif role == ROLES["admin_exams"]:
            if st.button("Login as Administrator", use_container_width=True, key="login_admin"):
                st.session_state.user_role, st.session_state.user_name = "admin_exams", "Administrator"
                st.rerun()
        
        elif role == ROLES["department_head"]:
            depts = get_departments()
            if not depts.empty:
                dept_name = st.selectbox("Select Department", depts["nom"].tolist())
                if st.button("Login", use_container_width=True, key="login_chef"):
                    dept_id = depts[depts["nom"] == dept_name]["id"].values[0]
                    st.session_state.user_role, st.session_state.user_name, st.session_state.user_dept_id = "department_head", f"Head {dept_name}", dept_id
                    st.rerun()
        
        elif role == ROLES["teacher"]:
            teachers = get_teachers_by_dept()
            if not teachers.empty:
                teacher_name = st.selectbox("Select your name", teachers["nom"].tolist())
                if st.button("Login", use_container_width=True, key="login_prof"):
                    teacher_data = teachers[teachers["nom"] == teacher_name].iloc[0]
                    st.session_state.user_role, st.session_state.user_name, st.session_state.user_dept_id = "teacher", teacher_name, teacher_data["dept_id"]
                    st.rerun()
        
        elif role == ROLES["student"]:
            formations = get_formations_by_dept()
            if not formations.empty:
                formation_name = st.selectbox("Select your program", formations["nom"].tolist())
                if st.button("Login", use_container_width=True, key="login_student"):
                    formation_data = formations[formations["nom"] == formation_name].iloc[0]
                    st.session_state.user_role, st.session_state.user_name, st.session_state.user_dept_id = "student", "Student", formation_data["dept_id"]
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Vice-Dean dashboard - new design
def dashboard_vice_dean():
    st.markdown(f"""
        <div class="hero-section">
            <div class="hero-title">STRATEGIC DASHBOARD</div>
            <div class="hero-description">Global view and detailed analysis of exams</div>
            <div class="user-badge-horizontal">
                <div class="user-badge-icon">👤</div>
                <div class="user-badge-text">{st.session_state.user_name}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    kpis = get_global_kpis()
    
    # Horizontal statistics
    st.markdown('<div class="stats-horizontal">', unsafe_allow_html=True)
    stats_data = [
        ("📚", int(kpis["nb_exams"]), "TOTAL EXAMS"),
        ("🏛️", int(kpis["nb_rooms"]), "AVAILABLE ROOMS"),
        ("👨‍🏫", int(kpis["nb_teachers"]), "TEACHERS"),
        ("🎓", 13000, "STUDENTS")
    ]
    
    for icon, value, label in stats_data:
        st.markdown(f"""
            <div class="stat-box-horizontal">
                <div class="stat-icon-large">{icon}</div>
                <div class="stat-content-horizontal">
                    <div class="stat-label-horizontal">{label}</div>
                    <div class="stat-value-horizontal">{value}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Alerts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="notification-box success">
                <div class="notification-title">✅ ROOM CONFLICTS</div>
                <div class="notification-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="notification-box success">
                <div class="notification-title">✅ TEACHER CONFLICTS</div>
                <div class="notification-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.markdown('<div class="content-box"><h2 class="section-title">ROOM OCCUPANCY</h2>', unsafe_allow_html=True)
    occupancy = get_global_occupancy()
    if not occupancy.empty:
        fig = px.bar(occupancy, x="room", y="occupancy_rate", color="occupancy_rate", 
                     color_continuous_scale=["#11998e", "#38ef7d", "#ffd200"])
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Raleway", size=12))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(occupancy, use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box"><h2 class="section-title">DEPARTMENT STATISTICS</h2>', unsafe_allow_html=True)
    stats_dept = get_stats_by_department()
    if not stats_dept.empty:
        fig = px.bar(stats_dept, x="department", y="nb_exams", color="nb_exams",
                     color_continuous_scale=["#667eea", "#764ba2"])
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Raleway"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(stats_dept, use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box"><h2 class="section-title">TEACHER WORKLOAD</h2>', unsafe_allow_html=True)
    hours = get_teaching_hours()
    if not hours.empty:
        fig = px.scatter(hours, x="nb_exams", y="total_hours", size="nb_supervisions",
                        color="department", hover_name="teacher", size_max=40)
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Raleway"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(hours, use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)

# Administrator dashboard - new design
def dashboard_admin_exams():
    st.markdown(f"""
        <div class="hero-section">
            <div class="hero-title">ADMINISTRATION PANEL</div>
            <div class="hero-description">Complete management and automatic generation</div>
            <div class="user-badge-horizontal">
                <div class="user-badge-icon">⚙️</div>
                <div class="user-badge-text">{st.session_state.user_name}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-box"><h2 class="section-title">MANAGEMENT TOOLS</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="tool-card"><div class="tool-icon">🚀</div><div class="tool-title">AUTO GENERATION</div></div>', unsafe_allow_html=True)
        if st.button("LAUNCH", use_container_width=True, key="gen_schedule"):
            with st.spinner("Processing..."):
                import time
                start = time.time()
                success, failed = generate_optimized_schedule()
                elapsed = time.time() - start
                total = success + failed
                rate = (success / total * 100) if total > 0 else 0
                st.markdown(f"""
                    <div class="notification-box success">
                        <div class="notification-title">✅ COMPLETED</div>
                        <p style="font-size: 1.2rem; margin-top: 1rem;">{success}/{total} modules ({rate:.1f}%) in {elapsed:.2f}s</p>
                    </div>
                """, unsafe_allow_html=True)
                if failed == 0:
                    st.balloons()
                st.cache_data.clear()
                st.rerun()
    
    with col2:
        st.markdown('<div class="tool-card"><div class="tool-icon">🔄</div><div class="tool-title">REFRESH</div></div>', unsafe_allow_html=True)
        if st.button("REFRESH", use_container_width=True, key="refresh"):
            st.cache_data.clear()
            st.success("✅ Data refreshed")
            st.rerun()
    
    with col3:
        st.markdown('<div class="tool-card"><div class="tool-icon">🗑️</div><div class="tool-title">RESET</div></div>', unsafe_allow_html=True)
        if st.button("CLEAR", use_container_width=True, key="reset"):
            conn = get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM exams")
                conn.commit()
                conn.close()
                st.success("✅ Schedule cleared")
                st.cache_data.clear()
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box"><h2 class="section-title">COMPLETE SCHEDULE</h2>', unsafe_allow_html=True)
    schedule = load_schedule_complete()
    if not schedule.empty:
        st.markdown('<div class="metric-row">', unsafe_allow_html=True)
        metrics = [
            ("📚 EXAMS", len(schedule)),
            ("🏛️ DEPARTMENTS", schedule["department"].nunique()),
            ("📖 PROGRAMS", schedule["formation"].nunique())
        ]
        for label, value in metrics:
            st.markdown(f"""
                <div class="metric-simple">
                    <div class="metric-simple-label">{label}</div>
                    <div class="metric-simple-value">{value}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.dataframe(schedule, use_container_width=True, height=500)
        csv = schedule.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD CSV", csv, "schedule.csv", "text/csv", key="dl_csv")
    else:
        st.info("No data available")
    st.markdown('</div>', unsafe_allow_html=True)

# Department head dashboard - new design
def dashboard_department_head():
    st.markdown(f"""
        <div class="hero-section">
            <div class="hero-title">DEPARTMENT SPACE</div>
            <div class="hero-description">Supervision and monitoring of exams</div>
            <div class="user-badge-horizontal">
                <div class="user-badge-icon">🏛️</div>
                <div class="user-badge-text">{st.session_state.user_name}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    dept_id = st.session_state.user_dept_id
    dept_schedule = load_schedule_complete(dept_id=dept_id)
    
    if not dept_schedule.empty:
        st.markdown(f"""
            <div class="department-header">
                <div class="department-name">🏛️ {dept_schedule.iloc[0]["department"]}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="stats-horizontal">', unsafe_allow_html=True)
        stats = [
            ("📚", len(dept_schedule), "EXAMS"),
            ("📖", dept_schedule["formation"].nunique(), "PROGRAMS"),
            ("✅", len(dept_schedule), "APPROVED")
        ]
        for icon, value, label in stats:
            st.markdown(f"""
                <div class="stat-box-horizontal">
                    <div class="stat-icon-large">{icon}</div>
                    <div class="stat-content-horizontal">
                        <div class="stat-label-horizontal">{label}</div>
                        <div class="stat-value-horizontal">{value}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="content-box"><h2 class="section-title">EXAMS BY PROGRAM</h2>', unsafe_allow_html=True)
        for formation in dept_schedule["formation"].unique():
            st.markdown(f"### 📖 {formation}")
            formation_data = dept_schedule[dept_schedule["formation"] == formation]
            for _, exam in formation_data.iterrows():
                dt = pd.to_datetime(exam['date_time'])
                st.markdown(f"""
                    <div class="exam-horizontal-card">
                        <div class="exam-time-block">
                            <div class="exam-time">{dt.strftime('%H:%M')}</div>
                            <div class="exam-date">{dt.strftime('%d/%m/%Y')}</div>
                        </div>
                        <div class="exam-details-flex">
                            <div class="exam-title-horizontal">{exam['module']}</div>
                            <div class="exam-meta">
                                <div class="exam-meta-item">🏫 {exam['room']}</div>
                                <div class="exam-meta-item">👨‍🏫 {exam['teacher']}</div>
                                <div class="exam-meta-item">👥 {exam['registered_count']} students</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="content-box"><h2 class="section-title">ANALYSIS</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            dept_schedule["date"] = pd.to_datetime(dept_schedule["date_time"]).dt.date
            exams_per_day = dept_schedule.groupby("date").size().reset_index(name="nb_exams")
            fig = px.bar(exams_per_day, x="date", y="nb_exams", title="Per day")
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Raleway"))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            exams_per_program = dept_schedule.groupby("formation").size().reset_index(name="nb_exams")
            fig = px.pie(exams_per_program, values="nb_exams", names="formation", title="By program")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No data")

# Teacher dashboard - new design
def dashboard_teacher():
    st.markdown(f"""
        <div class="hero-section">
            <div class="hero-title">MY SPACE</div>
            <div class="hero-description">My supervisions and responsibilities</div>
            <div class="user-badge-horizontal">
                <div class="user-badge-icon">👨‍🏫</div>
                <div class="user-badge-text">{st.session_state.user_name}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    query = """SELECT e.id, m.nom AS module, f.nom AS formation, d.nom AS department, l.nom AS room, e.date_time, COUNT(DISTINCT i.student_id) AS registered_count FROM exams e JOIN modules m ON m.id = e.module_id JOIN formations f ON f.id = m.formation_id JOIN departments d ON d.id = f.dept_id JOIN exam_rooms l ON l.id = e.room_id JOIN teachers p ON p.id = e.teacher_id LEFT JOIN registrations i ON i.module_id = m.id WHERE p.nom = %s GROUP BY e.id, m.nom, f.nom, d.nom, l.nom, e.date_time ORDER BY e.date_time"""
    my_exams = execute_query(query, params=(st.session_state.user_name,))
    
    if not my_exams.empty:
        st.markdown(f"""
            <div class="stat-box-horizontal" style="max-width: 500px; margin: 2rem auto;">
                <div class="stat-icon-large">📚</div>
                <div class="stat-content-horizontal">
                    <div class="stat-label-horizontal">MY SUPERVISIONS</div>
                    <div class="stat-value-horizontal">{len(my_exams)}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="content-box"><h2 class="section-title">MY CALENDAR</h2>', unsafe_allow_html=True)
        for _, exam in my_exams.iterrows():
            dt = pd.to_datetime(exam['date_time'])
            st.markdown(f"""
                <div class="exam-horizontal-card">
                    <div class="exam-time-block">
                        <div class="exam-time">{dt.strftime('%H:%M')}</div>
                        <div class="exam-date">{dt.strftime('%d/%m/%Y')}</div>
                    </div>
                    <div class="exam-details-flex">
                        <div class="exam-title-horizontal">{exam['module']}</div>
                        <div class="exam-meta">
                            <div class="exam-meta-item">📖 {exam['formation']}</div>
                            <div class="exam-meta-item">🏛️ {exam['department']}</div>
                            <div class="exam-meta-item">🏫 {exam['room']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No supervisions scheduled")

# Student dashboard - new design
def dashboard_student():
    st.markdown("""
        <div class="hero-section">
            <div class="hero-title">MY CALENDAR</div>
            <div class="hero-description">My personal exams</div>
            <div class="user-badge-horizontal">
                <div class="user-badge-icon">🎓</div>
                <div class="user-badge-text">Student</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    formations = get_formations_by_dept(st.session_state.user_dept_id)
    if not formations.empty:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        formation_selected = st.selectbox("My program", formations["nom"].tolist())
        formation_id = formations[formations["nom"] == formation_selected]["id"].values[0]
        st.markdown('</div>', unsafe_allow_html=True)
        
        student_schedule = get_student_schedule(formation_id)
        if not student_schedule.empty:
            st.markdown(f"""
                <div class="stat-box-horizontal" style="max-width: 500px; margin: 2rem auto;">
                    <div class="stat-icon-large">📚</div>
                    <div class="stat-content-horizontal">
                        <div class="stat-label-horizontal">MY EXAMS</div>
                        <div class="stat-value-horizontal">{len(student_schedule)}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="content-box"><h2 class="section-title">PERSONAL SCHEDULE</h2>', unsafe_allow_html=True)
            student_schedule["date"] = pd.to_datetime(student_schedule["date_time"]).dt.date
            for date in sorted(student_schedule["date"].unique()):
                st.markdown(f'<div class="date-header-box">📅 {date.strftime("%A %d %B %Y").upper()}</div>', unsafe_allow_html=True)
                day_exams = student_schedule[student_schedule["date"] == date]
                for _, exam in day_exams.iterrows():
                    dt = pd.to_datetime(exam['date_time'])
                    st.markdown(f"""
                        <div class="exam-horizontal-card">
                            <div class="exam-time-block">
                                <div class="exam-time">{dt.strftime('%H:%M')}</div>
                                <div class="exam-date">{dt.strftime('%d/%m')}</div>
                            </div>
                            <div class="exam-details-flex">
                                <div class="exam-title-horizontal">{exam['module']}</div>
                                <div class="exam-meta">
                                    <div class="exam-meta-item">🏫 {exam['room']}</div>
                                    <div class="exam-meta-item">👨‍🏫 {exam['teacher']}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            csv = student_schedule.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DOWNLOAD", csv, "my_calendar.csv", "text/csv", key="dl_student")
        else:
            st.info("No exams scheduled")
    else:
        st.warning("No program available")

# Navigation
def main():
    with st.sidebar:
        if st.session_state.user_role:
            st.markdown("""
                <div class="sidebar-profile-box">
                    <div class="sidebar-title">ACTIVE ACCOUNT</div>
                    <div class="sidebar-role">{}</div>
                    <div class="sidebar-name">{}</div>
                </div>
            """.format(ROLES[st.session_state.user_role], st.session_state.user_name), unsafe_allow_html=True)
            
            if st.button("🚪 LOGOUT", use_container_width=True, key="logout"):
                st.session_state.user_role = None
                st.session_state.user_name = None
                st.session_state.user_dept_id = None
                st.rerun()
    
    if not st.session_state.user_role:
        login_page()
    elif st.session_state.user_role == "vice_dean":
        dashboard_vice_dean()
    elif st.session_state.user_role == "admin_exams":
        dashboard_admin_exams()
    elif st.session_state.user_role == "department_head":
        dashboard_department_head()
    elif st.session_state.user_role == "teacher":
        dashboard_teacher()
    elif st.session_state.user_role == "student":
        dashboard_student()

if __name__ == "__main__":
    main()
