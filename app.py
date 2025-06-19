import streamlit as st
import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import json
from streamlit_echarts import st_echarts

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect('universities.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS universities
                 (id INTEGER PRIMARY KEY, name TEXT, acronym TEXT, region TEXT, type TEXT,
                  avg_fees INTEGER, difficulty TEXT, location TEXT, description TEXT,
                  facilities TEXT, programs TEXT, admission_requirements TEXT)''')
    conn.commit()
    return conn

# --- Web Scraping Function ---
def scrape_university_data():
    conn = init_db()
    c = conn.cursor()
    
    base_url = "https://www.tcu.go.tz/services/accreditation/universities-registered-tanzania"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    scraped_universities = []
    page = 1
    max_pages = 5  # Limit to prevent infinite loops; adjust based on site

    try:
        while page <= max_pages:
            url = f"{base_url}?page={page}" if page > 1 else base_url
            st.write(f"Scraping page {page}: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            university_rows = soup.select('table.views-table tbody tr')
            if not university_rows:
                st.write(f"No more universities found on page {page}. Stopping.")
                break

            for idx, row in enumerate(university_rows):
                cells = row.find_all('td')
                if len(cells) >= 4:
                    name_full = cells[1].text.strip()
                    name_parts = name_full.replace(')', '').split('(')
                    name = name_parts[0].strip()
                    acronym = name_parts[1].strip() if len(name_parts) > 1 else ''.join(word[0].upper() for word in name.split()[:3])
                    
                    head_office = cells[2].text.strip()
                    uni_type = cells[3].text.replace('University', '').replace('College', '').replace('Campus, Centre and Institute', '').strip()
                    
                    difficulty = "Medium"
                    if "Dar es Salaam" in head_office and "Public" in uni_type:
                        difficulty = "High"
                    elif "Health" in name or "Medicine" in name or "Science and Technology" in name:
                        difficulty = "High" if uni_type == "Public" else "Very High" if uni_type == "Private" else "High"
                    
                    avg_fees = 1500000
                    if "Private" in cells[3].text:
                        avg_fees = 2000000 + ((idx + page * 10) * 50000) % 2500000
                    
                    generic_programs = [
                        {"name": "General Studies", "duration": 3, "prospects": "Diverse career paths", "program_difficulty": "Medium"},
                        {"name": "Diploma in Business", "duration": 2, "prospects": "Small business management", "program_difficulty": "Low"}
                    ]
                    generic_facilities = ["Library", "Labs"]
                    
                    scraped_universities.append({
                        'id': len(scraped_universities) + 1,
                        'name': name,
                        'acronym': acronym,
                        'region': head_office,
                        'type': uni_type,
                        'avg_fees': avg_fees,
                        'difficulty': difficulty,
                        'location': head_office,
                        'description': f"This is a {uni_type} institution located in {head_office}, Tanzania. It is renowned for its contributions to various fields of study.",
                        'facilities': json.dumps(generic_facilities),
                        'programs': json.dumps(generic_programs),
                        'admission_requirements': "Minimum of D grades in 4 relevant subjects (placeholder)."
                    })
            
            page += 1
            time.sleep(1)  # Avoid overwhelming the server

        if scraped_universities:
            st.success(f"Successfully scraped {len(scraped_universities)} universities from TCU.")
            c.execute('DELETE FROM universities')
            conn.commit()
            for uni in scraped_universities:
                c.execute('''INSERT INTO universities
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (uni['id'], uni['name'], uni['acronym'], uni['region'], uni['type'],
                           uni['avg_fees'], uni['difficulty'], uni['location'], uni['description'],
                           uni['facilities'], uni['programs'], uni['admission_requirements']))
            conn.commit()
        else:
            st.warning("Scraping returned no data. Using sample data.")
            insert_sample_data(c, conn)
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network or HTTP error during scraping: {e}. Using sample data.")
        insert_sample_data(c, conn)
    except Exception as e:
        st.error(f"An unexpected error occurred during scraping: {e}. Using sample data.")
        insert_sample_data(c, conn)
    finally:
        conn.close()

# --- Helper function to insert sample data ---
def insert_sample_data(c, conn):
    sample_data = [
        (1, "University of Dar es Salaam", "UDSM", "Dar es Salaam", "Public", 1500000, "High", "Mlimani",
         "The oldest and largest public university in Tanzania.", json.dumps(["Library", "Labs", "Dorms", "Sports Complex"]),
         json.dumps([
             {"name": "BSc in Computer Science", "duration": 3, "prospects": "Software Developer, Data Scientist", "program_difficulty": "High"},
             {"name": "Bachelor of Laws (LLB)", "duration": 4, "prospects": "Lawyer, Legal Advisor", "program_difficulty": "High"}
         ]), "Minimum of B+ average in Science subjects."),
        (2, "Sokoine University of Agriculture", "SUA", "Morogoro", "Public", 1300000, "Medium", "Morogoro Town",
         "Leading in agriculture and veterinary sciences.", json.dumps(["Farms", "Labs", "Library"]),
         json.dumps([
             {"name": "BSc in Agriculture", "duration": 3, "prospects": "Agricultural Officer", "program_difficulty": "Medium"},
             {"name": "Doctor of Veterinary Medicine", "duration": 5, "prospects": "Veterinary Doctor", "program_difficulty": "High"}
         ]), "Minimum of C grades in Science subjects."),
        (3, "Ardhi University", "ARU", "Dar es Salaam", "Public", 1400000, "Medium", "Ubungo",
         "Specializes in land and environmental sciences.", json.dumps(["GIS Lab", "Library", "Dorms"]),
         json.dumps([
             {"name": "BSc in Land Management", "duration": 4, "prospects": "Valuer, Land Officer", "program_difficulty": "Medium"},
             {"name": "BSc in Architecture", "duration": 5, "prospects": "Architect", "program_difficulty": "Very High"}
         ]), "Minimum of C grades in Math, Physics, Geography."),
        (4, "University of Dodoma", "UDOM", "Dodoma", "Public", 1200000, "Medium", "Dodoma City",
         "Large university with diverse programs.", json.dumps(["Lecture Halls", "Library", "Hostels"]),
         json.dumps([
             {"name": "Bachelor of Arts in Education", "duration": 3, "prospects": "Teacher", "program_difficulty": "Medium"},
             {"name": "BSc in Nursing", "duration": 4, "prospects": "Nurse", "program_difficulty": "High"}
         ]), "Average pass in relevant subjects."),
        (5, "St. Augustine University of Tanzania", "SAUT", "Mwanza", "Private", 2000000, "Medium", "Mwanza City",
         "Prominent private university with multiple campuses.", json.dumps(["Library", "Hostels", "Computer Labs"]),
         json.dumps([
             {"name": "Bachelor of Arts in Mass Communication", "duration": 3, "prospects": "Journalist", "program_difficulty": "Medium"},
             {"name": "Bachelor of Business Administration", "duration": 3, "prospects": "Manager", "program_difficulty": "Medium"}
         ]), "Minimum of D grades in 4 subjects."),
        (6, "Mzumbe University", "MU", "Morogoro", "Public", 1350000, "High", "Mzumbe Town",
         "Renowned for public administration and law.", json.dumps(["Library", "Computer Labs", "Dorms"]),
         json.dumps([
             {"name": "Bachelor of Public Administration", "duration": 3, "prospects": "Civil Servant", "program_difficulty": "High"},
             {"name": "Bachelor of Laws (LLB)", "duration": 4, "prospects": "Lawyer", "program_difficulty": "High"}
         ]), "Strong passes in Arts subjects."),
        (7, "Hubert Kairuki Memorial University", "HKMU", "Dar es Salaam", "Private", 4500000, "High", "Mikocheni",
         "Specialized in health sciences.", json.dumps(["Hospital", "Labs", "Library"]),
         json.dumps([
             {"name": "Doctor of Medicine", "duration": 5, "prospects": "Medical Doctor", "program_difficulty": "Very High"},
             {"name": "BSc in Nursing", "duration": 4, "prospects": "Nurse", "program_difficulty": "High"}
         ]), "High passes in Chemistry, Biology, Physics."),
        (8, "Nelson Mandela African Institution of Science and Technology", "NM-AIST", "Arusha", "Public", 3000000, "Very High", "Tengeru",
         "Postgraduate-focused STEM institution.", json.dumps(["Advanced Labs", "Research Centers"]),
         json.dumps([
             {"name": "MSc in Data Science", "duration": 2, "prospects": "Data Scientist", "program_difficulty": "Very High"}
         ]), "Strong Bachelor's in STEM field."),
        (9, "Muhimbili University of Health and Allied Sciences", "MUHAS", "Dar es Salaam", "Public", 1600000, "High", "Upanga",
         "Premier health sciences institution.", json.dumps(["Teaching Hospital", "Labs", "Library"]),
         json.dumps([
             {"name": "Bachelor of Pharmacy", "duration": 4, "prospects": "Pharmacist", "program_difficulty": "High"},
             {"name": "Doctor of Dental Surgery", "duration": 5, "prospects": "Dentist", "program_difficulty": "Very High"}
         ]), "High passes in Chemistry, Biology, Physics."),
        (10, "Open University of Tanzania", "OUT", "Dar es Salaam", "Public", 1000000, "Low", "Kinondoni",
         "Offers distance learning programs.", json.dumps(["E-Library", "Online Platforms"]),
         json.dumps([
             {"name": "Bachelor of Business Administration (ODL)", "duration": 3, "prospects": "Business Manager", "program_difficulty": "Medium"}
         ]), "Passes in 4 subjects."),
        (11, "Tumaini University Makumira", "TUMA", "Arusha", "Private", 1800000, "Medium", "Makumira",
         "Faith-based university with diverse programs.", json.dumps(["Library", "Hostels", "Chapel"]),
         json.dumps([
             {"name": "Bachelor of Education", "duration": 3, "prospects": "Teacher", "program_difficulty": "Medium"}
         ]), "Minimum of D grades in 4 subjects."),
        (12, "Catholic University of Health and Allied Sciences", "CUHAS", "Mwanza", "Private", 3500000, "High", "Bugando",
         "Focuses on health sciences.", json.dumps(["Hospital", "Labs", "Library"]),
         json.dumps([
             {"name": "Doctor of Medicine", "duration": 5, "prospects": "Medical Doctor", "program_difficulty": "Very High"}
         ]), "High passes in Chemistry, Biology, Physics."),
        (13, "St. Joseph University in Tanzania", "SJUIT", "Dar es Salaam", "Private", 2500000, "Medium", "Mbezi",
         "Specializes in engineering and health sciences.", json.dumps(["Labs", "Library", "Workshops"]),
         json.dumps([
             {"name": "BSc in Civil Engineering", "duration": 4, "prospects": "Civil Engineer", "program_difficulty": "High"}
         ]), "Minimum of C grades in Math, Physics."),
        (14, "Teofilo Kisanji University", "TEKU", "Mbeya", "Private", 1700000, "Medium", "Mbeya City",
         "Offers diverse academic programs.", json.dumps(["Library", "Hostels", "Computer Labs"]),
         json.dumps([
             {"name": "Bachelor of Business Administration", "duration": 3, "prospects": "Manager", "program_difficulty": "Medium"}
         ]), "Minimum of D grades in 4 subjects."),
        (15, "Muslim University of Morogoro", "MUM", "Morogoro", "Private", 1600000, "Medium", "Morogoro",
         "Faith-based with focus on arts and sciences.", json.dumps(["Library", "Mosque", "Hostels"]),
         json.dumps([
             {"name": "Bachelor of Arts in Education", "duration": 3, "prospects": "Teacher", "program_difficulty": "Medium"}
         ]), "Minimum of D grades in 4 subjects.")
    ]
    c.executemany('''INSERT OR IGNORE INTO universities
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_data)
    conn.commit()

# --- Load data from database ---
@st.cache_data
def load_university_data():
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM universities", conn)
    conn.close()
    df['facilities'] = df['facilities'].apply(json.loads)
    df['programs'] = df['programs'].apply(json.loads)
    return df

# --- Streamlit app ---
def main():
    st.set_page_config(page_title="StackUniversity", layout="wide")
    
    # --- Custom CSS ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stApp { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        h1.st-title { font-size: 2.5rem; font-weight: bold; color: #1e293b; text-align: center; margin-bottom: 0.5rem; }
        h1.st-title span { color: #2563eb; }
        .st-card { 
            background-color: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; 
            padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
            transition: all 0.2s ease-in-out; height: 100%; display: flex; flex-direction: column;
        }
        .st-card:hover { transform: translateY(-3px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .st-tag { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 500; margin-right: 0.5rem; margin-bottom: 0.5rem;}
        .btn-primary { background-color: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer; }
        .btn-primary:hover { background-color: #1d4ed8; }
        .btn-secondary { background-color: #e2e8f0; color: #1e293b; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer; }
        .btn-secondary:hover { background-color: #cbd5e1; }
        .stButton>button { width: 100%; }
        .button-container { display: flex; gap: 0.5rem; margin-top: auto; }
        .stDataFrame { overflow-x: auto; }
        .stTabs [data-baseweb="tab-list"] { gap: 16px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: nowrap; border-bottom: 1px solid #ddd;
            background-color: #f8fafc; border-radius: 0.5rem 0.5rem 0 0; padding: 10px 20px; transition: all 0.2s ease-in-out; }
        .stTabs [aria-selected="true"] { border-bottom-color: #2563eb !important; color: #2563eb !important;
            background-color: white !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)
    
    # --- Header ---
    st.markdown("<h1 class='st-title'>Stack<span>University</span></h1>", unsafe_allow_html=True)
    st.write("Your guide to Tanzanian universities. Discover, compare, and make informed decisions.")
    
    # --- Initialize Session State ---
    if 'search_text' not in st.session_state:
        st.session_state.search_text = ""
    if 'region' not in st.session_state:
        st.session_state.region = "All Regions"
    if 'type_' not in st.session_state:
        st.session_state.type_ = "All Types"
    if 'max_fees' not in st.session_state:
        st.session_state.max_fees = 10000000
    if 'sort_by' not in st.session_state:
        st.session_state.sort_by = "Name (A-Z)"
    if 'comparison_list' not in st.session_state:
        st.session_state.comparison_list = []
    if 'selected_uni' not in st.session_state:
        st.session_state.selected_uni = None
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "home"
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 0
    if 'wizard_preferences' not in st.session_state:
        st.session_state.wizard_preferences = {}

    # --- Scrape/Load Data Button ---
    st.markdown("---")
    st.info("💡 **New data available!** Click 'Update Data' to refresh university listings from TCU.")
    if st.button("Update Data (Scrape from TCU)", help="Fetches the latest university list.", type="primary"):
        with st.spinner("Scraping university data..."):
            scrape_university_data()
            st.cache_data.clear()
            st.rerun()
    st.markdown("---")
    
    df = load_university_data()

    # --- Main Navigation ---
    if st.session_state.current_view == "home":
        st.header("Welcome to StackUniversity!")
        st.markdown("""
        <p style='font-size: 1.1rem; line-height: 1.6;'>
        Navigate university choices in Tanzania with ease. StackUniversity simplifies your decision-making process.
        </p>
        """, unsafe_allow_html=True)
        st.image("https://placehold.co/800x300/e0e7ff/3b82f6?text=Study+in+Tanzania", caption="Discover your future!", use_column_width=True)
        col_home1, col_home2 = st.columns(2)
        with col_home1:
            if st.button("Start Your Journey (Guided Fit)", key="start_wizard_btn", type="primary"):
                st.session_state.current_view = "wizard"
                st.session_state.wizard_step = 0
                st.session_state.wizard_preferences = {}
                st.rerun()
        with col_home2:
            if st.button("Explore All Universities", key="explore_all_btn", type="secondary"):
                st.session_state.current_view = "explore"
                st.rerun()

    elif st.session_state.current_view == "wizard":
        st.header("Find Your Best Fit")
        st.markdown("Answer questions to get personalized recommendations.")

        wizard_steps = [
            "Preferred region?",
            "University type?",
            "Annual budget (TZS)?",
            "Academic interest?",
            "Preferred difficulty?",
            "Recommendations"
        ]
        
        st.info(f"Step {st.session_state.wizard_step + 1} of {len(wizard_steps)}: {wizard_steps[st.session_state.wizard_step]}")

        if st.session_state.wizard_step == 0:
            regions = ['Any'] + sorted(df['region'].unique().tolist())
            pref_region = st.selectbox(wizard_steps[0], regions, key="wiz_region_select")
            if pref_region != 'Any':
                st.session_state.wizard_preferences['region'] = pref_region
            else:
                st.session_state.wizard_preferences.pop('region', None)

        elif st.session_state.wizard_step == 1:
            uni_types = ['Any', 'Public', 'Private']
            pref_type = st.radio(wizard_steps[1], uni_types, key="wiz_type_radio")
            if pref_type != 'Any':
                st.session_state.wizard_preferences['type'] = pref_type
            else:
                st.session_state.wizard_preferences.pop('type', None)

        elif st.session_state.wizard_step == 2:
            pref_fees = st.slider(wizard_steps[2], 1000000, 10000000, 3000000, 500000, key="wiz_fees_slider")
            st.session_state.wizard_preferences['max_fees'] = pref_fees
            st.write(f"You selected: Up to {pref_fees:,} TZS")

        elif st.session_state.wizard_step == 3:
            academic_interests = ['Any', 'STEM', 'Humanities', 'Business', 'Health Sciences', 'Agriculture', 'Law', 'Education']
            pref_interest = st.selectbox(wizard_steps[3], academic_interests, key="wiz_interest_select")
            if pref_interest != 'Any':
                st.session_state.wizard_preferences['academic_interest'] = pref_interest
            else:
                st.session_state.wizard_preferences.pop('academic_interest', None)

        elif st.session_state.wizard_step == 4:
            difficulty_levels = ['Any', 'Low', 'Medium', 'High', 'Very High']
            pref_difficulty = st.radio(wizard_steps[4], difficulty_levels, key="wiz_difficulty_radio")
            if pref_difficulty != 'Any':
                st.session_state.wizard_preferences['difficulty'] = pref_difficulty
            else:
                st.session_state.wizard_preferences.pop('difficulty', None)

        col_wiz_nav1, col_wiz_nav2 = st.columns(2)
        with col_wiz_nav1:
            if st.session_state.wizard_step > 0:
                if st.button("← Previous", key="wiz_prev_btn", type="secondary"):
                    st.session_state.wizard_step -= 1
                    st.rerun()
        with col_wiz_nav2:
            if st.session_state.wizard_step < len(wizard_steps) - 1:
                if st.button("Next →", key="wiz_next_btn", type="primary"):
                    st.session_state.wizard_step += 1
                    st.rerun()
            else:
                st.markdown("---")
                st.subheader("Your Recommendations:")
                
                reco_df = df.copy()
                prefs = st.session_state.wizard_preferences

                if 'region' in prefs:
                    reco_df = reco_df[reco_df['region'] == prefs['region']]
                if 'type' in prefs:
                    reco_df = reco_df[reco_df['type'] == prefs['type']]
                if 'max_fees' in prefs:
                    reco_df = reco_df[reco_df['avg_fees'] <= prefs['max_fees']]
                if 'difficulty' in prefs:
                    reco_df = reco_df[reco_df['difficulty'] == prefs['difficulty']]
                
                if 'academic_interest' in prefs and prefs['academic_interest'] != 'Any':
                    interest_lower = prefs['academic_interest'].lower()
                    reco_df = reco_df[
                        reco_df['programs'].apply(lambda x: any(interest_lower in p['name'].lower() for p in x if isinstance(p, dict) and 'name' in p))
                    ]
                
                if reco_df.empty:
                    st.warning("No universities match your criteria. Try adjusting preferences.")
                else:
                    st.write(f"Found {len(reco_df)} recommendations:")
                    for _, uni in reco_df.sort_values('difficulty').head(5).iterrows():
                        with st.container(border=True):
                            st.markdown(f"""
                            <h3 class='text-xl font-bold'>{uni['name']} ({uni['acronym']})</h3>
                            <p class='text-sm text-gray-500'>{uni['region']} | {uni['type']}</p>
                            <div class='my-2'>
                                <span class='st-tag bg-green-100 text-green-800'>{uni['difficulty']} Difficulty</span>
                            </div>
                            <p class='text-gray-600 text-sm'>{uni['description']}</p>
                            """, unsafe_allow_html=True)
                            if st.button("View Details", key=f"reco_view_{uni['id']}", type="secondary"):
                                st.session_state.selected_uni = uni
                                st.session_state.current_view = "details"
                                st.rerun()

        if st.button("Back to Home", key="wiz_back_home_btn", type="secondary"):
            st.session_state.current_view = "home"
            st.rerun()

    elif st.session_state.current_view == "details":
        uni = st.session_state.selected_uni
        if uni is None:
            st.warning("No university selected. Please go back to explore.")
            if st.button("Back to Explore", key="details_fallback_btn", type="secondary"):
                st.session_state.current_view = "explore"
                st.rerun()
            return
            
        st.header(f"{uni['name']} Details")
        st.markdown(f"""
            <p class='text-gray-500'>{uni['location']}, {uni['region']}</p>
            <div class='grid grid-cols-1 sm:grid-cols-3 gap-4 text-center my-6'>
                <div class='bg-gray-50 p-3 rounded-lg'>
                    <div class='text-sm text-gray-500'>Type</div>
                    <div class='font-semibold'>{uni['type']}</div>
                </div>
                <div class='bg-gray-50 p-3 rounded-lg'>
                    <div class='text-sm text-gray-500'>Difficulty</div>
                    <div class='font-semibold'>{uni['difficulty']}</div>
                </div>
                <div class='bg-gray-50 p-3 rounded-lg'>
                    <div class='text-sm text-gray-500'>Avg. Fees</div>
                    <div class='font-semibold'>{uni['avg_fees']:,} TZS/yr</div>
                </div>
            </div>
            <h4 class='text-xl font-semibold'>About</h4>
            <p class='text-gray-600'>{uni['description']}</p>
            """, unsafe_allow_html=True)
        
        with st.expander("Admission Requirements", expanded=True):
            st.write(uni['admission_requirements'])
            st.info("Check the university's website for specific requirements.")

        with st.expander("Facilities", expanded=True):
            st.markdown("<div class='flex flex-wrap gap-2'>", unsafe_allow_html=True)
            for f in uni['facilities']:
                st.markdown(f"<span class='st-tag bg-gray-100 text-gray-700'>{f}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Programs Offered", expanded=True):
            if isinstance(uni['programs'], list) and uni['programs']:
                for p in uni['programs']:
                    if isinstance(p, dict) and 'name' in p and 'duration' in p and 'prospects' in p and 'program_difficulty' in p:
                        st.markdown(f"""
                            <div class='border-t border-gray-200 pt-3 mt-3'>
                                <h5 class='font-semibold'>{p['name']}</h5>
                                <p class='text-sm text-gray-600'>Duration: {p['duration']} years | Difficulty: {p['program_difficulty']}</p>
                                <p class='text-sm text-gray-700'>Career Prospects: {p['prospects']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning(f"Malformed program data for {uni['name']}: {p}")
            else:
                st.info(f"No program details available for {uni['name']}.")

        if st.button("← Back to Explore", key="back_to_explore_btn", type="secondary"):
            st.session_state.selected_uni = None
            st.session_state.current_view = "explore"
            st.rerun()

    else:
        tab1, tab2, tab3 = st.tabs(["Explore Universities", f"Compare ({len(st.session_state.comparison_list)})", "Data Insights"])
        
        with tab1:
            st.header("Explore Universities")
            st.markdown("Filter or search for universities and programs.")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.subheader("Filter Your Search")
                st.session_state.search_text = st.text_input("Search by Name/Program", value=st.session_state.search_text, placeholder="e.g., UDSM, Computer Science", key="search_input")
                st.session_state.region = st.selectbox("Region", ['All Regions'] + sorted(df['region'].unique().tolist()), index=0, key="region_select")
                st.session_state.type_ = st.selectbox("University Type", ['All Types', 'Public', 'Private'], index=0, key="type_select")
                st.session_state.max_fees = st.slider("Max Annual Fees (TZS)", 1000000, 10000000, 10000000, 500000, key="fees_slider")
                st.session_state.sort_by = st.selectbox("Sort by", ["Name (A-Z)", "Name (Z-A)", "Fees (Low-High)", "Fees (High-Low)"], index=0, key="sort_by_select")
                
                if st.button("Reset Filters", type="secondary", key="reset_filters"):
                    st.session_state.search_text = ""
                    st.session_state.region = "All Regions"
                    st.session_state.type_ = "All Types"
                    st.session_state.max_fees = 10000000
                    st.session_state.sort_by = "Name (A-Z)"
                    st.rerun()
            
            filtered_df = df.copy()
            if st.session_state.search_text:
                search_text_lower = st.session_state.search_text.lower()
                filtered_df = filtered_df[
                    filtered_df['name'].str.lower().str.contains(search_text_lower, na=False) |
                    filtered_df['programs'].apply(lambda x: any(search_text_lower in p['name'].lower() for p in x if isinstance(p, dict) and 'name' in p))
                ]
            if st.session_state.region != "All Regions":
                filtered_df = filtered_df[filtered_df['region'] == st.session_state.region]
            if st.session_state.type_ != "All Types":
                filtered_df = filtered_df[filtered_df['type'] == st.session_state.type_]
            filtered_df = filtered_df[filtered_df['avg_fees'] <= st.session_state.max_fees]
            
            sort_key = {
                "Name (A-Z)": "name",
                "Name (Z-A)": "name",
                "Fees (Low-High)": "avg_fees",
                "Fees (High-Low)": "avg_fees"
            }[st.session_state.sort_by]
            ascending = st.session_state.sort_by in ["Name (A-Z)", "Fees (Low-High)"]
            filtered_df = filtered_df.sort_values(sort_key, ascending=ascending)
            
            with col2:
                st.markdown(f"<p class='text-sm text-gray-600'><strong>{len(filtered_df)}</strong> results found.</p>", unsafe_allow_html=True)
                if filtered_df.empty:
                    st.info("No universities match your filters. Try adjusting criteria.")
                
                num_cols = 3
                cols = st.columns(num_cols)
                col_idx = 0
                for _, uni in filtered_df.iterrows():
                    with cols[col_idx]:
                        with st.container(border=True):
                            st.markdown(f"""
                            <h3 class='text-xl font-bold'>{uni['name']} ({uni['acronym']})</h3>
                            <p class='text-sm text-gray-500'>{uni['region']}</p>
                            <div class='my-4'>
                                <span class='st-tag bg-blue-100 text-blue-800'>{uni['type']}</span>
                                <span class='st-tag bg-green-100 text-green-800'>{uni['difficulty']} Difficulty</span>
                            </div>
                            <p class='text-gray-600 text-sm flex-grow'>{uni['description']}</p>
                            """, unsafe_allow_html=True)
                            
                            with st.container():
                                st.markdown("<div class='button-container'>", unsafe_allow_html=True)
                                if st.button("View Details", key=f"view_{uni['id']}", type="secondary"):
                                    st.write(f"View Details clicked for {uni['name']}")
                                    st.session_state.selected_uni = uni
                                    st.session_state.current_view = "details"
                                    st.rerun()
                                is_comparing = uni['id'] in st.session_state.comparison_list
                                if st.button("Remove" if is_comparing else "Add to Compare", key=f"compare_{uni['id']}", type="primary" if not is_comparing else "secondary"):
                                    st.write(f"{'Remove' if is_comparing else 'Add to Compare'} clicked for {uni['name']}")
                                    if is_comparing:
                                        st.session_state.comparison_list.remove(uni['id'])
                                    elif len(st.session_state.comparison_list) < 4:
                                        st.session_state.comparison_list.append(uni['id'])
                                    else:
                                        st.error("You can only compare up to 4 universities.")
                                    st.rerun()
                                st.markdown("</div>", unsafe_allow_html=True)
                    col_idx = (col_idx + 1) % num_cols
        
        with tab2:
            st.header("Compare Universities")
            st.markdown("Select up to 4 universities to compare.")
            if not st.session_state.comparison_list:
                st.info("No universities selected for comparison.")
            else:
                compare_df = df[df['id'].isin(st.session_state.comparison_list)]
                
                feature_names = ["Region", "Type", "Avg. Annual Fees", "Difficulty", "Number of Programs", "Admission Requirements", "Facilities"]
                
                comparison_data = []
                for feature in feature_names:
                    row_data = {"Feature": feature}
                    for _, uni_row in compare_df.iterrows():
                        if feature == "Avg. Annual Fees":
                            row_data[uni_row['name']] = f"{uni_row['avg_fees']:,} TZS"
                        elif feature == "Number of Programs":
                            row_data[uni_row['name']] = len(uni_row['programs'])
                        elif feature == "Facilities":
                            row_data[uni_row['name']] = ", ".join(uni_row['facilities'])
                        elif feature == "Admission Requirements":
                            row_data[uni_row['name']] = uni_row.get('admission_requirements', 'N/A')
                        else:
                            row_data[uni_row['name']] = uni_row.get(feature.replace(" ", "_").lower(), 'N/A')
                    comparison_data.append(row_data)

                st.dataframe(pd.DataFrame(comparison_data).set_index("Feature"), use_container_width=True)
                
                if st.button("Clear Comparison List", type="secondary"):
                    st.session_state.comparison_list = []
                    st.rerun()
        
        with tab3:
            st.header("University Data Insights")
            st.write("Overview of the university landscape in Tanzania.")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Universities by Region")
                region_counts = df['region'].value_counts().to_dict()
                region_options = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "xAxis": {"type": "category", "data": list(region_counts.keys()), "axisLabel": {"interval": 0, "rotate": 45}},
                    "yAxis": {"type": "value", "name": "Number of Universities"},
                    "series": [{"data": list(region_counts.values()), "type": "bar", "itemStyle": {"color": "#3b82f6"}}]
                }
                st_echarts(options=region_options, height="400px", key="region_chart")
            
            with col_chart2:
                st.subheader("Distribution of University Types")
                type_counts = df['type'].value_counts().to_dict()
                pie_colors = {"Public": "#3b82f6", "Private": "#22c55e"}
                type_options = {
                    "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b}: {c} ({d}%)"},
                    "legend": {"bottom": "0%", "left": "center", "data": list(type_counts.keys())},
                    "series": [{
                        "name": "University Type",
                        "type": "pie",
                        "radius": ["40%", "70%"],
                        "avoidLabelOverlap": False,
                        "label": {"show": False, "position": "center"},
                        "emphasis": {"label": {"show": True, "fontSize": "20", "fontWeight": "bold"}},
                        "labelLine": {"show": False},
                        "data": [{"value": v, "name": k, "itemStyle": {"color": pie_colors.get(k, '#94a3b8')}} for k, v in type_counts.items()],
                    }]
                }
                st_echarts(options=type_options, height="450px", key="type_chart")
            
            st.subheader("University Difficulty Distribution")
            difficulty_order = ['Low', 'Medium', 'High', 'Very High']
            difficulty_counts = df['difficulty'].value_counts().reindex(difficulty_order, fill_value=0).to_dict()
            difficulty_options = {
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "xAxis": {"type": "category", "data": list(difficulty_counts.keys()), "axisLabel": {"interval": 0, "rotate": 0}},
                "yAxis": {"type": "value", "name": "Number of Universities"},
                "series": [{"data": list(difficulty_counts.values()), "type": "bar", "itemStyle": {"color": "#f97316"}}]
            }
            st_echarts(options=difficulty_options, height="400px", key="difficulty_chart")

if __name__ == "__main__":
    main()