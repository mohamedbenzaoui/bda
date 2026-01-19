إليك نسخة معدلة بشكل كبير من الواجهة مع تغيير ترتيب العناصر ونظام ألوان جديد (ثيم أزرق-بنفسجي داكن مع لمسات نيون خفيفة – أكثر عصرية وأنيقة لعام 2026).
Pythonimport streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import plotly.express as px

# ────────────────────────────────────────────────
# CONFIG GLOBALE (inchangée)
# ────────────────────────────────────────────────
DUREE_EXAM = 90
CRENEAUX = ["08:30", "11:00", "14:00"]
DATE_DEBUT = datetime(2026, 1, 10)
DATE_FIN = datetime(2026, 1, 25)
MAX_SALLES_PER_SLOT = 50

ROLES = {
    "vice_doyen": "Vice-Doyen",
    "admin_exams": "Gestionnaire Examens",
    "chef_dept": "Responsable Département",
    "enseignant": "Enseignant",
    "etudiant": "Étudiant"
}

st.set_page_config(page_title="EXAMEN 2026 • Plateforme Universitaire", layout="wide")

# ────────────────────────────────────────────────
# THÈME COMPLETEMENT NOUVEAU : Bleu-Néon / Violet Sombre 2026
# ────────────────────────────────────────────────
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Inter:wght@300;400;500;600&display=swap');

    :root {
        --bg-primary: #0a001f;
        --bg-secondary: #120036;
        --accent-main: #7c3aed;
        --accent-light: #a78bfa;
        --accent-dark: #5b21b6;
        --text-main: #f3e8ff;
        --text-muted: #c4b5fd;
        --card-bg: rgba(30, 20, 60, 0.65);
        --border-glow: rgba(124, 58, 237, 0.35);
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }

    body, .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f002e 100%);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1.5px;
    }

    .header-glow {
        background: linear-gradient(90deg, #a78bfa, #7c3aed, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        text-align: center;
        text-shadow: 0 0 20px rgba(167,139,250,0.5);
        margin: 1.5rem 0 0.8rem;
    }

    .subtitle-neon {
        color: var(--text-muted);
        text-align: center;
        font-size: 1.15rem;
        margin-bottom: 2.5rem;
        letter-spacing: 0.8px;
    }

    .card-neon {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-glow);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1.2rem 0;
        box-shadow: 0 8px 32px rgba(124,58,237,0.18);
        transition: all 0.35s ease;
    }

    .card-neon:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 50px rgba(124,58,237,0.35);
        border-color: var(--accent-light);
    }

    .stButton > button {
        background: linear-gradient(90deg, var(--accent-main), var(--accent-dark));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.6rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(124,58,237,0.4);
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, var(--accent-light), var(--accent-main));
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(167,139,250,0.5);
    }

    .metric-box {
        background: rgba(20, 10, 50, 0.7);
        border-radius: 14px;
        padding: 1.4rem;
        text-align: center;
        border: 1px solid rgba(167,139,250,0.25);
    }

    .metric-number {
        font-size: 2.8rem;
        font-weight: 700;
        color: var(--accent-light);
        margin: 0.4rem 0;
        text-shadow: 0 0 15px rgba(167,139,250,0.6);
    }

    .metric-label {
        color: var(--text-muted);
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }

    .section-divider {
        height: 2px;
        background: linear-gradient(to right, transparent, var(--accent-main), transparent);
        margin: 2.8rem 0;
    }

    .exam-card {
        background: rgba(15, 5, 40, 0.75);
        border-left: 5px solid var(--accent-main);
        border-radius: 10px;
        padding: 1.3rem;
        margin-bottom: 1.2rem;
    }
</style>""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# PAGE LOGIN → Changement ordre + style
# ────────────────────────────────────────────────
def page_login_new():
    st.markdown('<h1 class="header-glow">EXAMEN<span style="color:#c084fc;">+</span> 2026</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-neon">Système intelligent de gestion des examens universitaires</p>', unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 2.4, 1])
        with col2:
            with st.container():
                st.markdown('<div class="card-neon">', unsafe_allow_html=True)
                
                st.markdown("### Choisissez votre profil")
                
                # Nouvel ordre : les rôles les plus "importants" en haut
                role_order = [
                    ROLES["vice_doyen"],
                    ROLES["admin_exams"],
                    ROLES["chef_dept"],
                    ROLES["enseignant"],
                    ROLES["etudiant"]
                ]
                
                role_selected = st.radio(
                    label="Profil",
                    options=role_order,
                    label_visibility="collapsed",
                    horizontal=False
                )

                role_key = [k for k,v in ROLES.items() if v == role_selected][0]

                # Champs contextuels selon le rôle (affichés après sélection)
                if role_key in ["chef_dept", "enseignant", "etudiant"]:
                    if role_key == "chef_dept":
                        depts = get_departements()
                        if not depts.empty:
                            dept = st.selectbox("Département", depts["nom"].tolist())
                    elif role_key == "enseignant":
                        profs = get_professeurs_by_dept()
                        if not profs.empty:
                            prof = st.selectbox("Votre nom", profs["nom"].tolist())
                    elif role_key == "etudiant":
                        forms = get_formations_by_dept()
                        if not forms.empty:
                            form = st.selectbox("Votre formation", forms["nom"].tolist())

                if st.button(f"ENTRER → {role_selected}", type="primary", use_container_width=True):
                    st.session_state.user_role = role_key
                    st.session_state.user_name = role_selected
                    
                    # Attribution rapide des infos
                    if role_key == "vice_doyen":
                        st.session_state.user_name = "Vice-Doyen"
                    elif role_key == "admin_exams":
                        st.session_state.user_name = "Gestionnaire Examens"
                    elif role_key == "chef_dept":
                        st.session_state.user_dept_id = depts[depts["nom"] == dept]["id"].values[0]
                        st.session_state.user_name = f"Chef {dept}"
                    elif role_key == "enseignant":
                        row = profs[profs["nom"] == prof].iloc[0]
                        st.session_state.user_dept_id = row["dept_id"]
                        st.session_state.user_name = prof
                    elif role_key == "etudiant":
                        row = forms[forms["nom"] == form].iloc[0]
                        st.session_state.user_dept_id = row["dept_id"]
                        st.session_state.user_name = "Étudiant"
                        
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Exemple Dashboard Vice-Doyen (nouveau layout + couleurs)
# ────────────────────────────────────────────────
def dashboard_vice_doyen_new():
    st.markdown('<h1 class="header-glow">TABLEAU DE BORD EXÉCUTIF</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-neon">Vue stratégique globale – Janvier 2026</p>', unsafe_allow_html=True)

    # KPIs en haut – 4 colonnes
    kpis = get_kpis_globaux()
    cols = st.columns(4)
    values = [
        (int(kpis.get("nb_examens", 0)), "EXAMENS", "📝"),
        (int(kpis.get("nb_salles", 0)), "SALLES", "🏛️"),
        (int(kpis.get("nb_profs", 0)), "ENSEIGNANTS", "👨‍🏫"),
        (13200, "ÉTUDIANTS", "🎓")
    ]

    for col, (val, lbl, ico) in zip(cols, values):
        with col:
            st.markdown(f'''
            <div class="metric-box">
                <div style="font-size:2.6rem; margin-bottom:0.5rem;">{ico}</div>
                <div class="metric-number">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Graphiques côte à côte
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Taux d’occupation des salles")
        occ = get_occupation_globale()
        if not occ.empty:
            fig = px.bar(
                occ.head(12),
                x="salle",
                y="taux_occupation",
                color="taux_occupation",
                color_continuous_scale=["#6ee7b7", "#fbbf24", "#f87171"]
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                             font_color='#e9d5ff', height=420)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### Répartition par département")
        stats = get_stats_par_departement()
        fig_pie = px.pie(stats, values="nb_examens", names="departement",
                        color_discrete_sequence=px.colors.sequential.Voilet)
        fig_pie.update_layout(font_color='#e9d5ff')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Vous pouvez continuer à adapter les autres dashboards de la même manière...

# ────────────────────────────────────────────────
# POINT D'ENTRÉE PRINCIPAL
# ────────────────────────────────────────────────
def main():
    if "user_role" not in st.session_state:
        st.session_state.user_role = None

    with st.sidebar:
        st.markdown("### MENU")
        if st.session_state.user_role:
            st.info(f"Connecté : **{ROLES[st.session_state.user_role]}**")
            if st.button("Déconnexion", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    if not st.session_state.user_role:
        page_login_new()
    elif st.session_state.user_role == "vice_doyen":
        dashboard_vice_doyen_new()
    # ... ajouter les autres dashboards avec le même style

if __name__ == "__main__":
    main()
