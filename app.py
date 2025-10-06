# Final Response Instructions: This is the only file generated for app.py.
# The app is a complete, ready-to-run Streamlit web application.
# To run:
# 1. Save the contents of requirements.txt and app.py to the same folder.
# 2. Run 'pip install -r requirements.txt'
# 3. Run 'streamlit run app.py'
#
# This application will create two files and one folder in the same directory:
# - users.json: Stores user registration data (hashed password, onboarding status).
# - data.json: Stores all persistent application data (analysis history, points, routines, etc.).
# - reports/: Stores generated PDF reports.
#
# All data is local. To reset the application, delete users.json and data.json.
# This app contains no external API calls, databases, or network requests.

import streamlit as st
import json
import hashlib
import uuid
import os
from PIL import Image
import io
import pandas as pd
import altair as alt
from fpdf import FPDF
from datetime import datetime, date, timedelta

# --- Configuration & Constants ---
USERS_FILE = 'users.json'
DATA_FILE = 'data.json'
REPORTS_FOLDER = 'reports'
DEFAULT_THEME_COLOR = '#EAF6FF' # Soft blue
ACCENT_COLOR = '#007BFF'

# --- Initialization & Data Management ---

def load_data(file_path, default_data):
    """Loads data from a JSON file, or creates it if it doesn't exist."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(file_path, 'w') as f:
            json.dump(default_data, f, indent=4)
        return default_data
    except json.JSONDecodeError:
        st.error(f"Error decoding {file_path}. The file might be corrupted.")
        return default_data

def save_data(file_path, data):
    """Saves data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving data to {file_path}: {e}")

# Global data containers
# Note for future development: Replace this simple JSON storage with a more robust DB (e.g., Firebase, Supabase, PostgreSQL)
# The user_data can be accessed via st.session_state['user_data'] to avoid passing it around.
USERS = load_data(USERS_FILE, {})
DATA = load_data(DATA_FILE, {})
if REPORTS_FOLDER not in os.listdir('.'):
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

# --- Localization & Translation ---
# Simple dictionary for English/Hindi translations

def get_i18n(key):
    """Translates a key based on the current language in session state."""
    lang = st.session_state.get('language', 'English')
    translations = {
        'English': {
            # Authentication
            'login': 'Login', 'register': 'Register', 'logout': 'Logout',
            'username': 'Username', 'password': 'Password',
            'login_success': 'Logged in successfully!',
            'reg_success': 'Registration successful! Please log in.',
            'invalid_cred': 'Invalid username or password.',
            'user_exists': 'Username already exists.',
            # Sidebar
            'onboarding': 'Onboarding', 'dashboard': 'Dashboard',
            'skin_analyzer': 'Skin Analyzer', 'my_routine': 'My Routine',
            'marketplace': 'Product Marketplace', 'my_kit': 'Personalized Kit',
            'academy': 'Skincare Academy', 'forum': 'Community Forum',
            'expert_consult': 'Consult an Expert', 'hyper_advice': 'Hyper-Personalized Advice',
            'ai_chatbot': 'AI Chatbot', 'daily_checker': 'Daily Routine AI Checker',
            'lang_toggle': 'Language',
            # Onboarding
            'setup_title': '2-Minute Onboarding Setup',
            'full_name': 'Full Name', 'age': 'Age', 'location': 'Location (Country/City)',
            'primary_concerns': 'Primary Concerns', 'skin_type': 'Skin Type',
            'pref_lang': 'Preferred Language', 'onboard_complete': 'Onboarding Complete!',
            'onboard_btn': 'Save Onboarding',
            # Dashboard
            'welcome': 'Welcome,', 'skin_score': 'Skin Score', 'routine_summary': 'Quick Routine Summary',
            'score_over_time': 'Skin Score over Time', 'start_analysis': 'Start Skin Analysis',
            'last_score': 'Last Score', 'last_analysis_date': 'Last Analysis Date',
            'daily_pts': 'Daily Points', 'total_pts': 'Total Points',
            # Generic
            'coming_soon': 'Coming Soon', 'download_report': 'Download Report',
            'save_kit': 'Save to My Kit', 'post_question': 'Post Question',
            'submit_request': 'Submit Request', 'simulate': 'Simulate',
            'morning_routine': 'Morning Routine', 'evening_routine': 'Evening Routine',
            'completion': 'Completion', 'streak': 'Routine Streak',
            'view_analysis_details': 'View Analysis Details',
            'points_earned': 'Points Earned:', 'today_score': "Today's Routine Score",
            'good_job': 'Good job! You completed your routine.',
            'more_work': 'You missed some steps. Try again tomorrow!',
            'analysis_header': 'Your Hyper-Personalized Skin Analysis',
            'detected_type': 'Detected Skin Type', 'current_score': 'Current Skin Score',
            'future_proj': 'Future Score Projection', 'hydration': 'Hydration Score',
            'acne_risk': 'Acne Risk %', 'pig_risk': 'Pigmentation Risk %',
            'pore_vis': 'Pore Visibility Estimate', 'sleep_impact': 'Sleep Impact %',
            'stress_impact': 'Stress Impact %', 'recs': 'Personalized Recommendations',
            'lifestyle_actions': 'Lifestyle Actions', 'product_categories': 'Product Categories',
            'analysis_not_found': 'No analysis found. Please run the Skin Analyzer first.',
            'kit_empty': 'Your Personalized Kit is empty. Save products from the Marketplace.',
            'why_this_kit': 'Why this Kit is Recommended for You',
            'community_q': 'Community Questions & Answers',
            'your_question': 'Your Question', 'post': 'Post',
            'new_post': 'Post a New Question', 'ask_expert': 'Ask an Expert',
            'pref_date_time': 'Preferred Date/Time', 'short_note': 'Short Note',
            'requests_submitted': 'Submitted Requests', 'no_requests': 'No pending requests.',
        },
        'हिंदी': {
            # Authentication
            'login': 'लॉगिन', 'register': 'रजिस्टर', 'logout': 'लॉग आउट',
            'username': 'उपयोगकर्ता नाम', 'password': 'पासवर्ड',
            'login_success': 'सफलतापूर्वक लॉग इन किया गया!',
            'reg_success': 'पंजीकरण सफल! कृपया लॉग इन करें।',
            'invalid_cred': 'अमान्य उपयोगकर्ता नाम या पासवर्ड।',
            'user_exists': 'उपयोगकर्ता नाम पहले से मौजूद है।',
            # Sidebar
            'onboarding': 'ऑनबोर्डिंग', 'dashboard': 'डैशबोर्ड',
            'skin_analyzer': 'त्वचा विश्लेषक', 'my_routine': 'मेरी दिनचर्या',
            'marketplace': 'उत्पाद बाज़ार', 'my_kit': 'व्यक्तिगत किट',
            'academy': 'स्किनकेयर अकादमी', 'forum': 'सामुदायिक मंच',
            'expert_consult': 'विशेषज्ञ से परामर्श', 'hyper_advice': 'अति-व्यक्तिगत सलाह',
            'ai_chatbot': 'एआई चैटबॉट', 'daily_checker': 'दैनिक दिनचर्या एआई चेकर',
            'lang_toggle': 'भाषा',
            # Onboarding
            'setup_title': '2-मिनट ऑनबोर्डिंग सेटअप',
            'full_name': 'पूरा नाम', 'age': 'आयु', 'location': 'स्थान (देश/शहर)',
            'primary_concerns': 'प्राथमिक चिंताएं', 'skin_type': 'त्वचा का प्रकार',
            'pref_lang': 'पसंदीदा भाषा', 'onboard_complete': 'ऑनबोर्डिंग पूर्ण!',
            'onboard_btn': 'ऑनबोर्डिंग सहेजें',
            # Dashboard
            'welcome': 'स्वागत है,', 'skin_score': 'त्वचा स्कोर', 'routine_summary': 'त्वरित दिनचर्या सारांश',
            'score_over_time': 'समय के साथ त्वचा स्कोर', 'start_analysis': 'त्वचा विश्लेषण शुरू करें',
            'last_score': 'अंतिम स्कोर', 'last_analysis_date': 'अंतिम विश्लेषण तिथि',
            'daily_pts': 'दैनिक अंक', 'total_pts': 'कुल अंक',
            # Generic
            'coming_soon': 'जल्द आ रहा है', 'download_report': 'रिपोर्ट डाउनलोड करें',
            'save_kit': 'मेरी किट में सहेजें', 'post_question': 'प्रश्न पोस्ट करें',
            'submit_request': 'अनुरोध सबमिट करें', 'simulate': 'सिम्युलेट करें',
            'morning_routine': 'सुबह की दिनचर्या', 'evening_routine': 'शाम की दिनचर्या',
            'completion': 'पूर्णता', 'streak': 'दिनचर्या स्ट्रीक',
            'view_analysis_details': 'विश्लेषण विवरण देखें',
            'points_earned': 'अर्जित अंक:', 'today_score': 'आज का दिनचर्या स्कोर',
            'good_job': 'अच्छा काम! आपने अपनी दिनचर्या पूरी कर ली है।',
            'more_work': 'आपने कुछ कदम छोड़ दिए। कल फिर से प्रयास करें!',
            'analysis_header': 'आपका अति-व्यक्तिगत त्वचा विश्लेषण',
            'detected_type': 'पता चला त्वचा प्रकार', 'current_score': 'वर्तमान त्वचा स्कोर',
            'future_proj': 'भविष्य का स्कोर अनुमान', 'hydration': 'जलयोजन स्कोर',
            'acne_risk': 'मुँहासे जोखिम %', 'pig_risk': 'पिगमेंटेशन जोखिम %',
            'pore_vis': 'छिद्र दृश्यता अनुमान', 'sleep_impact': 'नींद का प्रभाव %',
            'stress_impact': 'तनाव का प्रभाव %', 'recs': 'व्यक्तिगत सिफारिशें',
            'lifestyle_actions': 'जीवनशैली कार्य', 'product_categories': 'उत्पाद श्रेणियाँ',
            'analysis_not_found': 'कोई विश्लेषण नहीं मिला। कृपया पहले त्वचा विश्लेषक चलाएँ।',
            'kit_empty': 'आपकी व्यक्तिगत किट खाली है। मार्केटप्लेस से उत्पाद सहेजें।',
            'why_this_kit': 'यह किट आपके लिए क्यों अनुशंसित है',
            'community_q': 'सामुदायिक प्रश्न और उत्तर',
            'your_question': 'आपका प्रश्न', 'post': 'पोस्ट करें',
            'new_post': 'एक नया प्रश्न पोस्ट करें', 'ask_expert': 'विशेषज्ञ से पूछें',
            'pref_date_time': 'पसंदीदा तिथि/समय', 'short_note': 'छोटा नोट',
            'requests_submitted': 'अनुरोध सबमिट किए गए', 'no_requests': 'कोई लंबित अनुरोध नहीं।',
        }
    }
    return translations[lang].get(key, key)


# --- Utility Functions ---

def hash_password(password, salt=None):
    """Hashes a password using SHA256 with a salt."""
    if salt is None:
        salt = uuid.uuid4().hex
    hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed_password, salt

def check_password(hashed_password, password, salt):
    """Checks a password against a stored hash and salt."""
    return hashed_password == hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def get_user_data(username):
    """Initializes or returns the user's entry in the main DATA store."""
    if username not in DATA:
        DATA[username] = {
            'onboarding': {},
            'analysis_history': [],
            'points': 0,
            'routine': {'morning': [], 'evening': []},
            'kit': [],
            'daily_completion': {},
            'forum_posts': [],
            'expert_requests': [],
        }
        save_data(DATA_FILE, DATA)
    return DATA[username]

def update_user_points(username, points):
    """Updates user's total points and saves the data."""
    DATA[username]['points'] = DATA[username].get('points', 0) + points
    save_data(DATA_FILE, DATA)
    return DATA[username]['points']

def get_current_user():
    """Returns the current logged-in username or None."""
    return st.session_state.get('logged_in_user')

# --- Authentication Pages ---

def login_register_page():
    """The main entry page for login and registration."""
    st.markdown(f"""
        <style>
            .stApp {{
                background-color: {DEFAULT_THEME_COLOR};
            }}
            .stButton>button {{
                background-color: {ACCENT_COLOR};
                color: white;
                border-radius: 5px;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Welcome to Your Skincare AI Assistant")
    st.write("Please **Login** or **Register** to continue.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(get_i18n('login'))
        with st.form("login_form"):
            username = st.text_input(get_i18n('username'))
            password = st.text_input(get_i18n('password'), type="password")
            login_submitted = st.form_submit_button(get_i18n('login'))
            
            if login_submitted:
                if username in USERS:
                    user_record = USERS[username]
                    if check_password(user_record['password'], password, user_record['salt']):
                        st.session_state['logged_in_user'] = username
                        st.session_state['page'] = 'Dashboard' # Default to Dashboard after login
                        st.success(get_i18n('login_success'))
                        st.rerun()
                    else:
                        st.error(get_i18n('invalid_cred'))
                else:
                    st.error(get_i18n('invalid_cred'))
                    
    with col2:
        st.subheader(get_i18n('register'))
        with st.form("register_form"):
            new_username = st.text_input(get_i18n('username'), key='reg_user')
            new_password = st.text_input(get_i18n('password'), type="password", key='reg_pass')
            register_submitted = st.form_submit_button(get_i18n('register'))
            
            if register_submitted:
                if new_username in USERS:
                    st.error(get_i18n('user_exists'))
                elif not new_username or not new_password:
                    st.error("Username and password cannot be empty.")
                else:
                    hashed_pass, salt = hash_password(new_password)
                    USERS[new_username] = {'password': hashed_pass, 'salt': salt}
                    save_data(USERS_FILE, USERS)
                    get_user_data(new_username) # Initialize user data
                    st.success(get_i18n('reg_success'))

# --- Sidebar and Main App Layout ---

def sidebar_menu():
    """Shows the main sidebar navigation after login."""
    st.sidebar.markdown(f"""
        <style>
            [data-testid="stSidebar"] {{
                background-color: {DEFAULT_THEME_COLOR};
            }}
            .sidebar .st-bb {{ /* Streamlit Cloud compatibility for sidebar selector */
                color: {ACCENT_COLOR};
            }}
            div[data-testid="stSidebarNav"] li a {{
                color: #333333; /* Default text color */
            }}
            div[data-testid="stSidebarNav"] li .current-page a {{
                background-color: {ACCENT_COLOR};
                color: white;
                border-radius: 5px;
            }}
        </style>
    """, unsafe_allow_html=True)

    username = get_current_user()
    if not username:
        return

    st.sidebar.image("https://via.placeholder.com/150x50.png?text=SkinAI+Logo", use_column_width=True) # Placeholder Logo
    st.sidebar.subheader(f"👋 {get_i18n('welcome')} {username}")

    # Language Toggle
    lang_options = ['English', 'हिंदी']
    selected_lang = st.sidebar.selectbox(get_i18n('lang_toggle'), lang_options, key='lang_select', index=lang_options.index(st.session_state.get('language', 'English')))
    st.session_state['language'] = selected_lang

    menu_items = {
        get_i18n('onboarding'): 'Onboarding',
        get_i18n('dashboard'): 'Dashboard',
        get_i18n('skin_analyzer'): 'Skin Analyzer',
        get_i18n('my_routine'): 'My Routine',
        get_i18n('marketplace'): 'Product Marketplace',
        get_i18n('my_kit'): 'Personalized Kit',
        get_i18n('academy'): 'Skincare Academy',
        get_i18n('forum'): 'Community Forum',
        get_i18n('expert_consult'): 'Consult an Expert',
        get_i18n('hyper_advice'): 'Hyper-Personalized Advice',
        get_i18n('ai_chatbot'): 'AI Chatbot',
        get_i18n('daily_checker'): 'Daily Routine AI Checker',
    }
    
    # Set initial page if not set
    if 'page' not in st.session_state:
        user_data = get_user_data(username)
        if user_data['onboarding']:
            st.session_state['page'] = 'Dashboard'
        else:
            st.session_state['page'] = 'Onboarding'

    # Display the menu using radio buttons for the most control
    selected_menu = st.sidebar.radio("Navigation", list(menu_items.keys()), index=list(menu_items.values()).index(st.session_state['page']))
    st.session_state['page'] = menu_items[selected_menu]

    st.sidebar.markdown("---")
    if st.sidebar.button(get_i18n('logout')):
        st.session_state['logged_in_user'] = None
        st.session_state['page'] = 'Login'
        st.rerun()

# --- Page Implementations ---

# Helper for Onboarding and Analyzer
CONCERNS = ['Acne', 'Pigmentation', 'Wrinkles', 'Sensitivity', 'Dryness', 'Oily']
SKIN_TYPES = ['Normal', 'Dry', 'Oily', 'Combination', 'Sensitive']
LANGUAGES = ['English', 'हिंदी']

def onboarding_page():
    """Page 1: Collects initial user setup data."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('onboarding'))
    st.header(get_i18n('setup_title'))
    
    if user_data['onboarding']:
        st.success(get_i18n('onboard_complete'))
        st.info("You can update your details below.")

    with st.form("onboarding_form"):
        # Load existing data or set defaults
        onboard_data = user_data.get('onboarding', {})
        
        full_name = st.text_input(get_i18n('full_name'), value=onboard_data.get('full_name', ''))
        age = st.number_input(get_i18n('age'), min_value=1, max_value=120, value=onboard_data.get('age', 25))
        location = st.text_input(get_i18n('location'), value=onboard_data.get('location', ''))
        
        # Multi-select for concerns
        default_concerns = onboard_data.get('primary_concerns', [])
        primary_concerns = st.multiselect(get_i18n('primary_concerns'), CONCERNS, default=default_concerns)
        
        # Dropdowns
        default_skin_type_index = SKIN_TYPES.index(onboard_data.get('skin_type', SKIN_TYPES[0]))
        skin_type = st.selectbox(get_i18n('skin_type'), SKIN_TYPES, index=default_skin_type_index)
        
        default_lang_index = LANGUAGES.index(onboard_data.get('preferred_language', LANGUAGES[0]))
        preferred_language = st.selectbox(get_i18n('pref_lang'), LANGUAGES, index=default_lang_index)
        
        submitted = st.form_submit_button(get_i18n('onboard_btn'))
        
        if submitted:
            user_data['onboarding'] = {
                'full_name': full_name,
                'age': age,
                'location': location,
                'primary_concerns': primary_concerns,
                'skin_type': skin_type,
                'preferred_language': preferred_language,
                'timestamp': datetime.now().isoformat()
            }
            save_data(DATA_FILE, DATA)
            st.success("Onboarding data saved successfully!")
            st.session_state['page'] = 'Dashboard' # Move to Dashboard after setup
            st.rerun()

def dashboard_page():
    """Page 2: Shows user a summary of their data."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('dashboard'))
    
    if not user_data['onboarding']:
        st.warning("Please complete your **Onboarding** first.")
        if st.button("Go to Onboarding"):
            st.session_state['page'] = 'Onboarding'
            st.rerun()
        return

    # --- Metrics Section ---
    last_analysis = user_data['analysis_history'][-1] if user_data['analysis_history'] else None
    
    col1, col2, col3, col4 = st.columns(4)
    
    last_score = last_analysis['current_score'] if last_analysis else 'N/A'
    last_date = datetime.fromisoformat(last_analysis['timestamp']).strftime('%b %d, %Y') if last_analysis else 'N/A'
    
    col1.metric(get_i18n('last_score'), last_score, delta="Score (0-100)")
    col2.metric(get_i18n('total_pts'), user_data['points'])
    col3.metric(get_i18n('last_analysis_date'), last_date)
    
    # Calculate routine streak
    daily_completions = user_data.get('daily_completion', {})
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Check if the user completed yesterday's routine
    yesterday_str = yesterday.isoformat()
    yesterday_completed = daily_completions.get(yesterday_str, {}).get('is_complete', False)
    
    # Simplistic streak calculation: just check if yesterday was done and count from there
    # This is a placeholder for a more robust DB-backed calculation.
    streak_count = 0
    if daily_completions.get((today - timedelta(days=1)).isoformat(), {}).get('is_complete', False):
        for i in range(1, 100): # Max 100 day check
            day_str = (today - timedelta(days=i)).isoformat()
            if daily_completions.get(day_str, {}).get('is_complete', False):
                streak_count += 1
            else:
                break
    
    col4.metric(get_i18n('streak'), streak_count)

    st.markdown("---")

    # --- Charts & CTAs ---
    col5, col6 = st.columns([3, 1])

    with col5:
        st.subheader(get_i18n('score_over_time'))
        
        if user_data['analysis_history']:
            history_df = pd.DataFrame([
                {'Date': datetime.fromisoformat(a['timestamp']).date(), 'Score': a['current_score']}
                for a in user_data['analysis_history']
            ])
            # Ensure only unique dates for charting
            history_df = history_df.drop_duplicates(subset=['Date'], keep='last')
            
            chart = alt.Chart(history_df).mark_line(point=True).encode(
                x=alt.X('Date', axis=alt.Axis(title='Date', format='%b %d')),
                y=alt.Y('Score', axis=alt.Axis(title='Skin Score (0-100)', domain=[0, 100])),
                tooltip=['Date', 'Score']
            ).properties(
                title=get_i18n('score_over_time')
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Run your first **Skin Analyzer** to see your score history!")
            
    with col6:
        st.subheader(get_i18n('routine_summary'))
        
        last_routine = last_analysis['routine_morning'] + last_analysis['routine_evening'] if last_analysis else []
        if last_routine:
            st.markdown(f"**{len(last_routine)}** Steps in Routine")
            
            st.caption("Last Analysis Routine Steps:")
            for i, step in enumerate(last_routine[:3]):
                st.write(f"- {step.split(':')[0]}")
            if len(last_routine) > 3:
                st.caption(f"... and {len(last_routine) - 3} more steps.")
                
            if st.button("Go to My Routine"):
                st.session_state['page'] = 'My Routine'
                st.rerun()
        else:
            st.info("No routine found. Please run a **Skin Analyzer** first.")
        
    st.markdown("---")

    if st.button(get_i18n('start_analysis'), use_container_width=True, key='dashboard_cta'):
        st.session_state['page'] = 'Skin Analyzer'
        st.rerun()

def create_pdf_report(analysis_data, username):
    """Creates a basic PDF report using fpdf2."""
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'Hyper-Personalized Skin Analysis Report', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Report for {username}', 0, 0, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(234, 246, 255) # Soft Blue
            self.cell(0, 8, title, 0, 1, 'L', fill=True)
            self.ln(2)

        def chapter_body(self, body):
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 5, body)
            self.ln()

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Report Meta
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f"Date: {datetime.fromisoformat(analysis_data['timestamp']).strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.ln(5)

    # Summary
    pdf.chapter_title("1. Analysis Summary")
    summary = (
        f"Detected Skin Type: {analysis_data['detected_skin_type']}\n"
        f"Current Skin Score: {analysis_data['current_score']} / 100\n"
        f"Future Score Projection (90 days): {analysis_data['future_score_proj_90']}"
    )
    pdf.chapter_body(summary)
    
    # Detailed Scores
    pdf.chapter_title("2. Detailed Breakdown")
    detail = (
        f"Hydration Score: {analysis_data['hydration_score']}%\n"
        f"Acne Risk: {analysis_data['acne_risk_pct']}%\n"
        f"Pigmentation Risk: {analysis_data['pigmentation_risk_pct']}%\n"
        f"Pore Visibility Estimate: {analysis_data['pore_visibility_estimate']}\n"
        f"Sleep Impact: {analysis_data['sleep_impact_pct']}%\n"
        f"Stress Impact: {analysis_data['stress_impact_pct']}%\n"
    )
    pdf.chapter_body(detail)

    # Recommendations
    pdf.chapter_title("3. Personalized Routine & Recommendations")
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, "Morning Routine:", 0, 1)
    pdf.set_font('Arial', '', 10)
    for step in analysis_data['routine_morning']:
        pdf.cell(0, 5, f"- {step}", 0, 1)
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, "Evening Routine:", 0, 1)
    pdf.set_font('Arial', '', 10)
    for step in analysis_data['routine_evening']:
        pdf.cell(0, 5, f"- {step}", 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, "Product Categories:", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.chapter_body(", ".join(analysis_data['recommendations']['product_categories']))

    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, "Lifestyle Actions:", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.chapter_body(analysis_data['recommendations']['lifestyle_actions'])


    # Save to BytesIO for Streamlit download
    pdf_output = pdf.output(dest='S').encode('latin1') # 'S' returns the document as a string (bytes)

    return pdf_output

def pseudo_analyze_image(uploaded_file, lifestyle_factors, user_data):
    """
    High-quality pseudo-analysis function.
    NOTE: This is a placeholder for a real ML model.
    Future development: Replace this with a function that calls a local TFLite or PyTorch model:
    e.g., model.predict(preprocessed_image).
    """
    
    # 1. Image Feature Extraction (Pseudo)
    try:
        image = Image.open(uploaded_file)
        # Convert to RGB (in case it's a PNG with transparency)
        image = image.convert('RGB')
        
        # Simple RGB Mean and Contrast
        rgb_mean = [sum(c) / (image.width * image.height) for c in image.split()]
        avg_brightness = sum(rgb_mean) / 3
        
        # Simple Contrast (placeholder: standard deviation of pixel values)
        # Real contrast requires more complex histogram analysis
        # For simplicity, we'll use a hardcoded value based on brightness for the demo
        contrast_heuristic = 0.5 if avg_brightness < 100 or avg_brightness > 200 else 1.0
        
        # Skin Tone Heuristic (Pseudo-detection)
        if rgb_mean[0] > rgb_mean[1] * 1.1 and rgb_mean[0] > rgb_mean[2] * 1.1:
            # High Red component can indicate redness/inflammation
            redness_factor = 1.2
        else:
            redness_factor = 1.0
            
    except Exception as e:
        # Fallback in case of image error (e.g., corrupted file)
        st.warning(f"Image analysis error ({e}). Using fallback heuristics.")
        avg_brightness = 150
        contrast_heuristic = 1.0
        redness_factor = 1.0
    
    # 2. Lifestyle Factor Integration
    sleep_score = (lifestyle_factors['sleep_hours'] - 5) / 5 # 0 to 1 scale (5hrs=0, 10hrs=1)
    water_score = lifestyle_factors['water_intake'] / 4 # 0 to 1 scale (0L=0, 4L=1)
    stress_score = (10 - lifestyle_factors['stress_level']) / 10 # 0 to 1 scale (10=0, 0=1)
    diet_score = lifestyle_factors['diet_quality'] / 5 # 0 to 1 scale (0=0, 5=1)
    
    # 3. Deterministic Scoring Logic
    # Base score combines image stats + lifestyle
    # Weights: Image (40%), Lifestyle (60%)
    
    base_image_score = (avg_brightness / 255.0) * 0.4 + (1.0 - contrast_heuristic) * 0.2
    
    lifestyle_impact_score = (
        sleep_score * 0.25 + 
        water_score * 0.25 + 
        stress_score * 0.35 + 
        diet_score * 0.15
    )
    
    # Final Score (0-100)
    current_score = int((base_image_score * 0.4 + lifestyle_impact_score * 0.6) * 100 * (1/redness_factor))
    current_score = max(50, min(95, current_score)) # Clamp between 50 and 95 for realism

    # 4. Detailed Breakdown Generation (Deterministic based on scores)
    
    # Hydration
    hydration_score = int((water_score * 0.6 + avg_brightness/255 * 0.4) * 100)
    hydration_score = max(50, min(99, hydration_score))

    # Acne Risk
    # High oil (if skin type is oily) + high stress + poor diet = high risk
    onboard_skin_type = user_data['onboarding']['skin_type']
    base_risk = 50 - (current_score / 2) # Base risk inverse to overall score
    if onboard_skin_type in ['Oily', 'Combination']: base_risk += 10
    acne_risk_pct = int(base_risk + (1-stress_score) * 15 + (1-diet_score) * 10)
    acne_risk_pct = min(90, max(10, acne_risk_pct))

    # Pigmentation Risk (Placeholder based on redness and overall skin quality)
    pigmentation_risk_pct = int(20 + (1-base_image_score) * 15 + (1-water_score) * 10)
    pigmentation_risk_pct = min(70, max(5, pigmentation_risk_pct))

    # Future Projection: Assume improvement if current score is low and lifestyle is good.
    future_delta = int((lifestyle_impact_score - 0.5) * 20) # Max +- 10 points
    
    proj_7 = min(100, current_score + max(0, future_delta // 3))
    proj_30 = min(100, current_score + max(0, future_delta))
    proj_90 = min(100, current_score + max(0, future_delta * 2))
    
    # Explanation
    explanation = f"Your score is **{current_score}**. The image analysis detected a fair quality skin base, but a higher **{int(avg_brightness/255 * 100)}% average brightness** which can be a sign of mild dryness/redness. The most significant factor impacting your score is your **Stress Level** (contributing {int((1-stress_score)*100)}% to the negative impact). Improvements in sleep and stress management are projected to increase your score significantly in 90 days."

    # Personalized Routine (Based on concerns and scores)
    morning_routine = ["Cleanse: Gentle Hydrating Cleanser", "Treat: Vitamin C Serum", "Protect: SPF 30+ Sunscreen"]
    evening_routine = ["Cleanse: Double Cleanse (Oil + Foam)", "Treat: Niacinamide Serum", "Moisturize: Barrier Repair Cream"]
    
    # Adjust routine based on concerns
    if 'Acne' in user_data['onboarding']['primary_concerns'] or acne_risk_pct > 50:
        evening_routine[1] = "Treat: Salicylic Acid (BHA) Serum"
    if 'Wrinkles' in user_data['onboarding']['primary_concerns']:
        evening_routine.append("Treat: Retinoid Cream (3x/week)")
        
    # Recommendations
    product_categories = ['Hyaluronic Acid Serums', 'Ceramide Moisturizers', 'Broad Spectrum Sunscreens']
    lifestyle_actions = "Focus on **Stress Reduction** (daily 10 min meditation). Increase **Water Intake** to 3L/day. Target 8 hours of sleep."

    # Return the full analysis dictionary
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'image_features': {'avg_brightness': avg_brightness, 'redness_factor': redness_factor},
        'lifestyle_factors': lifestyle_factors,
        'detected_skin_type': onboard_skin_type, # Use the self-reported one for now
        'current_score': current_score,
        'future_score_proj_7': proj_7,
        'future_score_proj_30': proj_30,
        'future_score_proj_90': proj_90,
        'explanation': explanation,
        'hydration_score': hydration_score,
        'acne_risk_pct': acne_risk_pct,
        'pigmentation_risk_pct': pigmentation_risk_pct,
        'pore_visibility_estimate': 'High' if onboard_skin_type in ['Oily', 'Combination'] or acne_risk_pct > 50 else 'Low',
        'sleep_impact_pct': int((1-sleep_score) * 100),
        'stress_impact_pct': int((1-stress_score) * 100),
        'recommendations': {
            'product_categories': product_categories,
            'lifestyle_actions': lifestyle_actions
        },
        'routine_morning': morning_routine,
        'routine_evening': evening_routine
    }
    
    return analysis_results

def skin_analyzer_page():
    """Page 3: Skin Analyzer - pseudo ML function and report download."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('skin_analyzer'))

    if not user_data['onboarding']:
        st.warning("Please complete your **Onboarding** first.")
        return

    st.info("Upload a selfie for analysis. No actual ML is run; a deterministic pseudo-analysis will be generated based on image features and lifestyle inputs.")

    col_form, col_img = st.columns([1, 1])

    with col_form:
        st.subheader("Lifestyle Inputs")
        with st.form("analyzer_form"):
            uploaded_file = st.file_uploader("Upload Selfie (JPG/PNG)", type=["jpg", "jpeg", "png"])
            
            st.markdown("---")
            st.subheader("Lifestyle Factors")
            
            sleep_hours = st.slider("Sleep Hours (last 7 days average)", 4, 12, 7)
            water_intake = st.slider("Water Intake (Liters/day)", 0.5, 4.0, 2.0, step=0.5)
            stress_level = st.slider("Stress Level (1=Low, 10=High)", 1, 10, 5)
            diet_quality = st.slider("Diet Quality (1=Poor, 5=Excellent)", 1, 5, 3)
            
            analyze_submitted = st.form_submit_button("Run Analysis")

    with col_img:
        st.subheader("Uploaded Image")
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Selfie", use_column_width=True)
        else:
            st.image("https://via.placeholder.com/300x300.png?text=Upload+Selfie", use_column_width=True)

    if analyze_submitted and uploaded_file is not None:
        with st.spinner('Running Hyper-Personalized Analysis...'):
            lifestyle_factors = {
                'sleep_hours': sleep_hours,
                'water_intake': water_intake,
                'stress_level': stress_level,
                'diet_quality': diet_quality
            }
            analysis_results = pseudo_analyze_image(uploaded_file, lifestyle_factors, user_data)
            
            # Save results
            user_data['analysis_history'].append(analysis_results)
            update_user_points(username, 10) # +10 points for each analysis
            save_data(DATA_FILE, DATA)
            st.session_state['last_analysis'] = analysis_results
            st.success("Analysis Complete! +10 Points Earned.")
            st.balloons()
            st.rerun() # Rerun to display results clearly

    if 'last_analysis' in st.session_state or user_data['analysis_history']:
        # Always use the latest analysis if available
        current_analysis = st.session_state.get('last_analysis', user_data['analysis_history'][-1])
        st.markdown("---")
        st.header(get_i18n('analysis_header'))
        
        # 1. Summary
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric(get_i18n('current_score'), f"{current_analysis['current_score']}/100")
        col_s2.metric(get_i18n('detected_type'), current_analysis['detected_skin_type'])
        col_s3.metric(get_i18n('future_proj'), f"{current_analysis['future_score_proj_90']} (90 days)")
        
        st.markdown("---")
        st.subheader("Analysis Explanation")
        st.info(current_analysis['explanation'])

        # 2. Detailed Breakdown
        st.subheader("Detailed Breakdown")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        col_d1.metric(get_i18n('hydration'), f"{current_analysis['hydration_score']}%")
        col_d1.metric(get_i18n('sleep_impact'), f"{current_analysis['sleep_impact_pct']}%")
        
        col_d2.metric(get_i18n('acne_risk'), f"{current_analysis['acne_risk_pct']}%")
        col_d2.metric(get_i18n('stress_impact'), f"{current_analysis['stress_impact_pct']}%")
        
        col_d3.metric(get_i18n('pig_risk'), f"{current_analysis['pigmentation_risk_pct']}%")
        col_d3.metric(get_i18n('pore_vis'), current_analysis['pore_visibility_estimate'])

        st.markdown("---")
        # 3. Recommendations
        st.subheader(get_i18n('recs'))
        
        with st.expander(get_i18n('product_categories')):
            st.markdown(", ".join([f"**{c}**" for c in current_analysis['recommendations']['product_categories']]))
            st.caption("These categories are recommended based on your scores and self-reported concerns.")
            
        with st.expander(get_i18n('lifestyle_actions')):
            st.markdown(current_analysis['recommendations']['lifestyle_actions'])
            st.caption("Your daily habits are the key to long-term skin health.")
            
        # 4. Download Report
        st.markdown("---")
        pdf_bytes = create_pdf_report(current_analysis, username)
        
        st.download_button(
            label=get_i18n('download_report'),
            data=pdf_bytes,
            file_name=f"SkinAI_Report_{username}_{date.today().isoformat()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

def my_routine_page():
    """Page 4: Shows user's routine, tracking, and gamification."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('my_routine'))
    
    last_analysis = user_data['analysis_history'][-1] if user_data['analysis_history'] else None
    
    if not last_analysis:
        st.warning(get_i18n('analysis_not_found'))
        return

    current_routine = {
        'morning': last_analysis['routine_morning'],
        'evening': last_analysis['routine_evening']
    }
    
    st.subheader(f"Your Current Hyper-Personalized Routine (From last analysis on {datetime.fromisoformat(last_analysis['timestamp']).strftime('%b %d, %Y')})")
    
    col_score, col_points = st.columns(2)
    col_score.metric("Total Points", user_data['points'])
    # The 'streak' calculation is simplified in dashboard; here we just display total points.
    
    st.markdown("---")
    
    today_str = date.today().isoformat()
    daily_completion = user_data['daily_completion'].get(today_str, {'morning': {}, 'evening': {}})

    # --- Morning Routine ---
    st.subheader(get_i18n('morning_routine'))
    with st.container(border=True):
        morning_completed = 0
        total_morning = len(current_routine['morning'])
        for i, step in enumerate(current_routine['morning']):
            step_key = f'morning_{i}'
            default_checked = daily_completion['morning'].get(step_key, False)
            if st.checkbox(step, key=step_key, value=default_checked):
                daily_completion['morning'][step_key] = True
                morning_completed += 1
            else:
                daily_completion['morning'][step_key] = False
        
        st.progress(morning_completed / total_morning, text=f"{morning_completed}/{total_morning} steps completed.")

    st.markdown("---")
    
    # --- Evening Routine ---
    st.subheader(get_i18n('evening_routine'))
    with st.container(border=True):
        evening_completed = 0
        total_evening = len(current_routine['evening'])
        for i, step in enumerate(current_routine['evening']):
            step_key = f'evening_{i}'
            default_checked = daily_completion['evening'].get(step_key, False)
            if st.checkbox(step, key=step_key, value=default_checked):
                daily_completion['evening'][step_key] = True
                evening_completed += 1
            else:
                daily_completion['evening'][step_key] = False
        
        st.progress(evening_completed / total_evening, text=f"{evening_completed}/{total_evening} steps completed.")
        
    st.markdown("---")
    
    # --- Gamification & Save ---
    total_steps = total_morning + total_evening
    total_completed = morning_completed + evening_completed
    
    is_complete_today = total_completed == total_steps
    
    if st.button("Finalize Today's Routine & Claim Points", use_container_width=True):
        # Only award points once per day
        if not user_data['daily_completion'].get(today_str, {}).get('is_complete', False):
            points_to_award = 0
            
            if is_complete_today:
                points_to_award = 5 # +5 for daily full routine completion
                st.success(f"{get_i18n('good_job')} +{points_to_award} points awarded!")
            else:
                st.info(get_i18n('more_work'))
            
            # Update user data
            user_data['daily_completion'][today_str] = {
                'morning': daily_completion['morning'],
                'evening': daily_completion['evening'],
                'is_complete': is_complete_today,
                'points_awarded': points_to_award
            }
            if points_to_award > 0:
                update_user_points(username, points_to_award)
            save_data(DATA_FILE, DATA)
            st.rerun()
        else:
            st.warning("You have already finalized your routine for today.")

def product_marketplace_page():
    """Page 5: Static product list with filters and save-to-kit functionality."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('marketplace'))
    
    # Static Product Data
    PRODUCTS = [
        {'id': 1, 'name': 'Hydrating Gentle Cleanser', 'price': 19.99, 'concern': ['Dryness', 'Sensitivity'], 'ingredients': ['Ceramides', 'Hyaluronic Acid'], 'description': 'A non-foaming, gentle cleanser that respects the skin barrier.', 'link': 'https://affiliate.link/cleanser'},
        {'id': 2, 'name': '2% Salicylic Acid Serum', 'price': 24.50, 'concern': ['Acne', 'Oily'], 'ingredients': ['Salicylic Acid', 'Niacinamide'], 'description': 'Targets blackheads and breakouts, exfoliating deep inside the pores.', 'link': 'https://affiliate.link/salicylic'},
        {'id': 3, 'name': 'Vitamin C Brightening Serum', 'price': 45.00, 'concern': ['Pigmentation', 'Wrinkles'], 'ingredients': ['Ascorbic Acid', 'Vitamin E'], 'description': 'Potent antioxidant that brightens skin and protects against environmental damage.', 'link': 'https://affiliate.link/vitaminc'},
        {'id': 4, 'name': 'Mineral SPF 50 Sunscreen', 'price': 29.00, 'concern': ['All'], 'ingredients': ['Zinc Oxide', 'Titanium Dioxide'], 'description': 'Broad-spectrum mineral filter, no white cast on most skin tones.', 'link': 'https://affiliate.link/spf'},
        {'id': 5, 'name': 'Retinol 0.5% Night Cream', 'price': 39.99, 'concern': ['Wrinkles'], 'ingredients': ['Retinol', 'Peptides'], 'description': 'Powerful night cream to reduce signs of aging.', 'link': 'https://affiliate.link/retinol'},
    ]
    
    # --- Filtering Sidebar ---
    st.sidebar.markdown("## Marketplace Filters")
    all_concerns = sorted(list(set(c for p in PRODUCTS for c in p['concern'])))
    selected_concerns = st.sidebar.multiselect("Filter by Concern", all_concerns, key='market_concern')
    
    all_ingredients = sorted(list(set(i for p in PRODUCTS for i in p['ingredients'])))
    selected_ingredients = st.sidebar.multiselect("Filter by Key Ingredient", all_ingredients, key='market_ingr')
    
    # --- Filtering Logic ---
    filtered_products = PRODUCTS
    
    if selected_concerns:
        filtered_products = [p for p in filtered_products if any(c in p['concern'] for c in selected_concerns)]
        
    if selected_ingredients:
        filtered_products = [p for p in filtered_products if any(i in p['ingredients'] for i in selected_ingredients)]
        
    st.info(f"Showing **{len(filtered_products)}** products.")

    # --- Product Display ---
    kit_ids = [p['id'] for p in user_data['kit']]

    for i, product in enumerate(filtered_products):
        if i % 2 == 0:
            cols = st.columns(2)
            col = cols[0]
        else:
            col = cols[1]

        with col:
            with st.container(border=True):
                st.subheader(product['name'])
                st.markdown(f"**${product['price']:.2f}** | Concerns: *{', '.join(product['concern'])}*")
                st.caption(product['description'])
                st.markdown(f"**Key Ingredients:** {', '.join(product['ingredients'])}")
                
                col_btn1, col_btn2 = st.columns([1, 1])
                
                # Affiliate Link button (placeholder)
                col_btn1.link_button("View Product (Affiliate)", product['link'], use_container_width=True)
                
                # Save to Kit button
                if product['id'] in kit_ids:
                    col_btn2.button("In My Kit (Remove)", key=f"remove_{product['id']}", use_container_width=True)
                    if col_btn2.button("In My Kit (Remove)", key=f"remove_{product['id']}", use_container_width=True):
                        user_data['kit'] = [p for p in user_data['kit'] if p['id'] != product['id']]
                        save_data(DATA_FILE, DATA)
                        st.toast(f"Removed **{product['name']}** from your kit.")
                        st.rerun()
                else:
                    if col_btn2.button(get_i18n('save_kit'), key=f"save_{product['id']}", use_container_width=True):
                        # Save only a necessary subset of product data
                        user_data['kit'].append({
                            'id': product['id'],
                            'name': product['name'],
                            'concern': product['concern']
                        })
                        save_data(DATA_FILE, DATA)
                        st.toast(f"Added **{product['name']}** to your kit!")
                        st.rerun()

def personalized_kit_page():
    """Page 6: Shows saved products and explains their relevance."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('my_kit'))
    
    kit = user_data['kit']
    last_analysis = user_data['analysis_history'][-1] if user_data['analysis_history'] else None
    
    st.subheader(f"Current Kit ({len(kit)} Products)")

    if not kit:
        st.warning(get_i18n('kit_empty'))
        return

    # --- Display Kit ---
    for i, product in enumerate(kit):
        if i % 3 == 0:
            cols = st.columns(3)
            col = cols[0]
        elif i % 3 == 1:
            col = cols[1]
        else:
            col = cols[2]
            
        with col:
            with st.container(border=True):
                st.markdown(f"**{product['name']}**")
                st.caption(f"Targets: {', '.join(product['concern'])}")
                
                if st.button("Remove", key=f"remove_kit_{product['id']}", use_container_width=True):
                    user_data['kit'] = [p for p in user_data['kit'] if p['id'] != product['id']]
                    save_data(DATA_FILE, DATA)
                    st.toast(f"Removed {product['name']}.")
                    st.rerun()
    
    st.markdown("---")
    
    # --- Explainable Kit Section ---
    st.subheader(get_i18n('why_this_kit'))
    
    if last_analysis:
        st.info(f"Based on your last analysis (Score: {last_analysis['current_score']}, Acne Risk: {last_analysis['acne_risk_pct']}%).")
        
        # Analyze why each product is needed
        kit_concerns = set(c for p in kit for c in p['concern'])
        
        st.markdown("**Your Kit Concerns:**")
        
        if 'Acne' in kit_concerns and last_analysis['acne_risk_pct'] > 50:
            st.markdown("- **Acne:** Your kit includes *Acne* targeting products, which is essential given your **high Acne Risk** in the last analysis.")
        
        if 'Dryness' in kit_concerns and last_analysis['hydration_score'] < 70:
            st.markdown("- **Dryness/Hydration:** Products for *Dryness* help address your **low Hydration Score** of {last_analysis['hydration_score']}% found in the analysis.")
            
        if 'Wrinkles' in kit_concerns and last_analysis['future_score_proj_90'] < last_analysis['current_score']:
            st.markdown("- **Anti-Aging/Wrinkles:** Products targeting *Wrinkles* support your long-term skin health, especially when lifestyle factors (stress/sleep) are negatively impacting your projection.")
            
        if not kit_concerns:
             st.warning("Your kit doesn't seem to cover the main issues identified in your analysis. Consider checking the Marketplace!")
    else:
        st.warning(get_i18n('analysis_not_found'))

def skincare_academy_page():
    """Page 7: Static content library and video links."""
    st.title(get_i18n('academy'))
    st.subheader("Video Library")
    
    # Static YouTube Embeds (placeholders)
    youtube_videos = [
        {"title": "The Science of Skin Barriers", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ?controls=0"}, # Rickroll
        {"title": "Beginner's Guide to Retinol", "url": "https://www.youtube.com/embed/zH0jL2d9zOQ?controls=0"},
    ]
    
    cols = st.columns(2)
    for i, video in enumerate(youtube_videos):
        with cols[i % 2]:
            st.markdown(f"#### {video['title']}")
            st.markdown(f'<iframe width="100%" height="200" src="{video["url"]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Article Library")
    
    # Simple search and static articles
    search_query = st.text_input("Search Articles...", key='article_search')
    
    articles = {
        "What is the Skin Microbiome?": "The skin microbiome is the vast ecosystem of microorganisms that live on your skin. A balanced microbiome is essential for a strong skin barrier and overall skin health. Disruptions can lead to conditions like acne, eczema, and rosacea. Look for products with prebiotics and postbiotics.",
        "How Diet Impacts Acne": "Research shows a strong correlation between high glycemic index diets and dairy consumption with increased acne severity. Focus on antioxidant-rich foods, omega-3 fatty acids, and plenty of fiber for clearer skin.",
        "The Truth About Hyaluronic Acid": "Hyaluronic Acid (HA) is a powerful humectant, meaning it draws moisture from the air and deeper layers of the skin to the surface. It can hold up to 1000 times its weight in water, making it excellent for hydration. Ensure you apply it on damp skin!",
    }
    
    filtered_articles = {k: v for k, v in articles.items() if search_query.lower() in k.lower() or search_query.lower() in v.lower()}
    
    if filtered_articles:
        for title, content in filtered_articles.items():
            with st.expander(title):
                st.write(content)
                st.caption("Source: SkinAI Internal Research (Placeholder)")
    else:
        st.info("No articles found matching your search.")

def community_forum_page():
    """Page 8: Basic local Q&A forum."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('forum'))
    
    st.subheader(get_i18n('community_q'))
    
    # --- Post New Question ---
    st.markdown("---")
    st.subheader(get_i18n('new_post'))
    with st.form("new_post_form", clear_on_submit=True):
        post_title = st.text_input(get_i18n('your_question'), placeholder="e.g., Best serum for combination skin?")
        post_body = st.text_area("Details", placeholder="Elaborate on your question here...")
        
        if st.form_submit_button(get_i18n('post_question')):
            if post_title and post_body:
                new_post = {
                    'id': uuid.uuid4().hex,
                    'user': username,
                    'title': post_title,
                    'body': post_body,
                    'timestamp': datetime.now().isoformat(),
                    'comments': []
                }
                user_data['forum_posts'].insert(0, new_post)
                save_data(DATA_FILE, DATA)
                st.success("Your question has been posted!")
                st.rerun()
            else:
                st.error("Please fill in both the question and details.")
                
    st.markdown("---")
    
    # --- Display Existing Posts (Shared across all users for the demo) ---
    all_posts = []
    for user in DATA:
        all_posts.extend(DATA[user].get('forum_posts', []))
        
    # Sort by time
    all_posts.sort(key=lambda x: x['timestamp'], reverse=True)
    
    if all_posts:
        for post in all_posts:
            with st.container(border=True):
                st.subheader(post['title'])
                st.caption(f"Posted by **{post['user']}** on {datetime.fromisoformat(post['timestamp']).strftime('%b %d, %H:%M')}")
                st.write(post['body'])
                
                # Simple comment feature (in-memory per session for demo, but saved for future use)
                with st.expander(f"View/Add Comments ({len(post['comments'])})"):
                    for comment in post['comments']:
                        st.markdown(f"**{comment['user']}**: {comment['body']}")
                        st.caption(datetime.fromisoformat(comment['timestamp']).strftime('%H:%M'))
                    
                    comment_text = st.text_input("Your comment:", key=f"comment_{post['id']}")
                    if st.button("Add Comment", key=f"add_comment_{post['id']}"):
                        if comment_text:
                            # Note: To fully implement this, we'd need to find the post ID in the DATA structure
                            # and add the comment there. For a demo, we will simply use the current post object
                            # but acknowledge that this is *not* persistent across users in this simplified code.
                            # The persistent comments would require the real ID lookup.
                            st.info("Comment feature is a placeholder. In a real app, this would be saved persistently.")
                            post['comments'].append({'user': username, 'body': comment_text, 'timestamp': datetime.now().isoformat()})
                            # Re-save the main DATA file (expensive, but necessary for this simple JSON structure)
                            save_data(DATA_FILE, DATA)
                            st.rerun()
                        else:
                            st.warning("Comment cannot be empty.")
    else:
        st.info("No questions posted yet. Be the first!")

def consult_expert_page():
    """Page 9: Booking demo form."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('expert_consult'))
    
    st.subheader(get_i18n('ask_expert'))
    
    with st.form("expert_consult_form", clear_on_submit=True):
        name = st.text_input(get_i18n('full_name'), value=user_data['onboarding'].get('full_name', ''))
        email = st.text_input("Email", placeholder="you@example.com")
        
        col_date, col_time = st.columns(2)
        pref_date = col_date.date_input("Preferred Date", min_value=date.today())
        pref_time = col_time.time_input("Preferred Time")
        
        short_note = st.text_area(get_i18n('short_note'), placeholder="What would you like to discuss?")
        
        if st.form_submit_button(get_i18n('submit_request')):
            if name and email and short_note:
                new_request = {
                    'id': uuid.uuid4().hex,
                    'user': username,
                    'name': name,
                    'email': email,
                    'date': pref_date.isoformat(),
                    'time': pref_time.isoformat(),
                    'note': short_note,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'Pending'
                }
                user_data['expert_requests'].append(new_request)
                save_data(DATA_FILE, DATA)
                st.success("Your consultation request has been submitted. An expert will reach out soon!")
            else:
                st.error("Please fill in all fields.")

    st.markdown("---")
    st.subheader(get_i18n('requests_submitted'))
    
    requests = sorted(user_data['expert_requests'], key=lambda x: x['timestamp'], reverse=True)
    if requests:
        for request in requests:
            status_color = "green" if request['status'] == 'Confirmed' else "orange"
            st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; border-left: 5px solid {ACCENT_COLOR}; background-color: white;">
                    <p style="margin: 0;"><strong>Date:</strong> {request['date']} at {request['time']}</p>
                    <p style="margin: 0;"><strong>Note:</strong> {request['note'][:50]}...</p>
                    <p style="margin: 0; color: {status_color};"><strong>Status:</strong> {request['status']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info(get_i18n('no_requests'))

def hyper_personalized_advice_page():
    """Page 10: Static write-up with a simulation tool."""
    st.title(get_i18n('hyper_advice'))

    # The required comprehensive write-up
    st.subheader("The Future of Hyper-Personalization in Skincare")
    st.markdown("""
    Hyper-personalization moves beyond general skin types (dry, oily, combination) to treat the unique needs of the individual, moment-to-moment. It integrates **external data** (weather, pollution), **physiological data** (sleep, stress, diet), and **biometric data** (DNA, microbiome) to craft a truly bespoke routine.
    
    ### Holistic Integration: The New Frontier
    
    Our skin is a direct mirror of our internal state. True personalization must therefore be holistic:
    
    * **Diet:** Inflammatory foods (high sugar, some dairy) directly contribute to acne and premature aging. A hyper-personalized plan suggests specific anti-inflammatory ingredients (omega-3s, antioxidants) tailored to your skin’s current inflammatory markers.
    * **Sleep:** Poor sleep elevates cortisol (stress hormone), which breaks down collagen and impairs barrier function, leading to sensitivity and breakouts. Our AI integrates sleep tracking to suggest barrier-repair creams and calming ingredients before a predicted bad night.
    * **Stress:** Chronic stress is one of the most significant yet overlooked factors in skin health. It triggers everything from eczema flare-ups to hormonal acne. The hyper-personalized approach provides targeted lifestyle actions (meditation, breathwork) alongside ingredients like Centella Asiatica or Niacinamide to combat the physiological effects of stress on the skin.
    
    By combining high-resolution image analysis with these critical lifestyle factors, we can not only identify current issues but **proactively predict** future skin conditions, allowing for preventative care that maximizes long-term results.
    """)
    
    st.markdown("---")

    # --- Simulation Tool ---
    st.subheader("Lifestyle Score Delta Simulator")
    st.info("See how improving your habits could impact your score.")

    col_sim1, col_sim2 = st.columns(2)
    
    with col_sim1:
        st.caption("Current State (Simulated Defaults)")
        sim_sleep = st.slider("Sleep Hours", 4, 12, 6, key='sim_sleep')
        sim_water = st.slider("Water Intake (L/day)", 0.5, 4.0, 1.5, step=0.5, key='sim_water')
        sim_stress = st.slider("Stress Level (1-10)", 1, 10, 8, key='sim_stress')
        sim_diet = st.slider("Diet Quality (1-5)", 1, 5, 2, key='sim_diet')

    with col_sim2:
        st.caption("Optimized Target State")
        opt_sleep = st.slider("Sleep Hours", 4, 12, 8, key='opt_sleep')
        opt_water = st.slider("Water Intake (L/day)", 0.5, 4.0, 3.0, step=0.5, key='opt_water')
        opt_stress = st.slider("Stress Level (1-10)", 1, 10, 3, key='opt_stress')
        opt_diet = st.slider("Diet Quality (1-5)", 1, 5, 4, key='opt_diet')

    if st.button(get_i18n('simulate'), use_container_width=True):
        # Deterministic logic for score delta
        score_base = 70
        
        # Current Delta (Negative impact for poor habits)
        cur_delta = (6 - sim_sleep) * 2 + (2.5 - sim_water) * 3 + (sim_stress - 5) * 1.5 + (3 - sim_diet) * 2
        current_score = int(score_base - cur_delta)
        current_score = max(50, min(90, current_score))
        
        # Optimized Delta (Positive impact for good habits)
        opt_delta = (8 - opt_sleep) * 2 + (3.5 - opt_water) * 3 + (opt_stress - 5) * 1.5 + (4 - opt_diet) * 2
        optimized_score = int(score_base - opt_delta)
        optimized_score = max(70, min(99, optimized_score))
        
        score_delta = optimized_score - current_score
        
        st.markdown("---")
        st.subheader("Simulation Results")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Current Score Estimate", current_score)
        col_res2.metric("Optimized Score Estimate", optimized_score)
        col_res3.metric("Predicted Score Delta", f"+{score_delta}", delta="Potential Improvement")
        
        st.subheader("Actionable Insights")
        
        actions = []
        if opt_sleep > sim_sleep: actions.append(f"- **Increase Sleep:** Target {opt_sleep} hours/night to boost skin repair.")
        if opt_water > sim_water: actions.append(f"- **Hydrate More:** Increase water intake to {opt_water}L/day for better plumpness.")
        if opt_stress < sim_stress: actions.append(f"- **Reduce Stress:** Implement a daily 10-minute mindfulness practice.")
        if opt_diet > sim_diet: actions.append(f"- **Improve Diet:** Focus on whole foods and anti-inflammatory ingredients.")
        
        st.markdown("\n".join(actions))

def ai_chatbot_page():
    """Page 11: Simple FAQ with pre-seeded questions/answers."""
    st.title(get_i18n('ai_chatbot'))
    st.subheader("Pre-seeded Skincare Q&A")
    st.info("No external AI calls are made. Select a question to see the expert answer.")
    
    faq = {
        "What is the best routine order?": "The general rule is thinnest to thickest consistency: Cleanser > Toner > Serum > Eye Cream > Moisturizer > Sunscreen (AM only).",
        "Can I mix Vitamin C and Retinol?": "It's generally advised not to mix them in the same routine, as it can cause irritation. Use Vitamin C in the morning and Retinol at night.",
        "Why is my skin suddenly breaking out?": "Sudden breakouts can be caused by hormonal changes, stress, diet (especially high GI foods), or a new product introduced into your routine.",
        "What does 'non-comedogenic' mean?": "It means the product has been formulated in a way that is less likely to block pores, which is especially important for acne-prone and oily skin types.",
        "How much sunscreen should I use?": "You should use about a nickel-sized amount for your face alone to achieve the SPF protection listed on the bottle. Reapply every two hours.",
        "How often should I exfoliate?": "For chemical exfoliants (AHAs/BHAs), 2-3 times per week is usually sufficient. Over-exfoliating can damage your skin barrier.",
    }
    
    questions = list(faq.keys())
    
    for question in questions:
        with st.expander(f"Q: {question}"):
            st.write(f"**A:** {faq[question]}")

def daily_routine_ai_checker_page():
    """Page 12: Daily checklist and points award."""
    username = get_current_user()
    user_data = get_user_data(username)
    st.title(get_i18n('daily_checker'))
    st.subheader("Daily Holistic Checklist")
    
    today_str = date.today().isoformat()
    daily_completion = user_data['daily_completion'].get(today_str, {'checker': {}})
    
    # 15 Tasks for Morning/Night
    tasks = {
        'AM_1': "Applied prescribed Vitamin C/Antioxidant Serum (AM)",
        'AM_2': "Applied Sunscreen with SPF 30+ (AM)",
        'AM_3': "Consumed a full glass of water upon waking",
        'AM_4': "Engaged in 5 minutes of mindful breathing/meditation",
        'AM_5': "Avoided high-sugar breakfast",
        'PM_1': "Completed double cleanse (PM)",
        'PM_2': "Applied prescribed Retinol/Active Treatment (PM)",
        'PM_3': "Applied eye cream and moisturized neck/chest (PM)",
        'PM_4': "Avoided screen time 30 mins before bed",
        'PM_5': "Logged 7+ hours of sleep last night",
        'LIFE_1': "Ate 3+ servings of vegetables/fruits",
        'LIFE_2': "Drank 2L+ of water throughout the day",
        'LIFE_3': "Avoided picking/touching face unnecessarily",
        'LIFE_4': "Changed pillowcase/towel (weekly check)",
        'LIFE_5': "Completed a 30-min physical activity",
    }
    
    current_checker = daily_completion.get('checker', {})
    
    st.markdown("---")
    st.subheader("Morning & Evening Tasks")
    
    col_am, col_pm = st.columns(2)
    
    # Morning Tasks
    am_tasks = {k: v for k, v in tasks.items() if k.startswith('AM')}
    with col_am:
        for k, v in am_tasks.items():
            default = current_checker.get(k, False)
            current_checker[k] = st.checkbox(v, value=default, key=k)

    # Evening Tasks
    pm_tasks = {k: v for k, v in tasks.items() if k.startswith('PM')}
    with col_pm:
        for k, v in pm_tasks.items():
            default = current_checker.get(k, False)
            current_checker[k] = st.checkbox(v, value=default, key=k)

    st.markdown("---")
    st.subheader("Holistic Lifestyle Tasks")
    
    # Lifestyle Tasks
    life_tasks = {k: v for k, v in tasks.items() if k.startswith('LIFE')}
    cols_life = st.columns(3)
    for i, (k, v) in enumerate(life_tasks.items()):
        with cols_life[i % 3]:
            default = current_checker.get(k, False)
            current_checker[k] = st.checkbox(v, value=default, key=k)

    st.markdown("---")
    
    total_tasks = len(tasks)
    completed_tasks = sum(current_checker.values())
    
    current_score = completed_tasks * 5
    
    st.progress(completed_tasks / total_tasks, text=f"Daily Progress: {completed_tasks}/{total_tasks} completed.")
    st.metric(get_i18n('today_score'), current_score, delta=f"+{current_score} Potential Points")
    
    # --- Finalize & Award Points ---
    if st.button("Finalize Daily Checker & Claim Points", use_container_width=True):
        # Check if points were already awarded for the checker today
        already_awarded = daily_completion.get('checker_points_awarded', 0)
        
        # Calculate new points only if not finalized or if the score is higher (allowing updates)
        new_points = current_score - already_awarded
        
        if new_points > 0:
            update_user_points(username, new_points)
            st.success(f"Finalized and awarded +{new_points} points for today's checker! Total: {user_data['points']}")
            
            # Update data with final state and awarded points
            daily_completion['checker'] = current_checker
            daily_completion['checker_points_awarded'] = current_score
            user_data['daily_completion'][today_str] = daily_completion
            save_data(DATA_FILE, DATA)
        elif new_points < 0:
             # This means they deselected tasks after finalizing a high score. Just save the state.
             daily_completion['checker'] = current_checker
             user_data['daily_completion'][today_str] = daily_completion
             save_data(DATA_FILE, DATA)
             st.info("Checker progress saved. No new points awarded.")
        else:
            st.info("Checker finalized. No new points earned since the last check.")
            
        st.rerun()
        
    st.markdown("---")
    
    # Simple advice based on completion
    if completed_tasks < 5:
        st.error("Advice: You have a lot of gaps! Focus on basic cleansing and moisturizing first.")
    elif completed_tasks < 10:
        st.info("Advice: Good start! Try to integrate more lifestyle habits like stress reduction and water intake.")
    else:
        st.success("Advice: Excellent consistency! Keep up the great work on both your routine and your overall well-being.")

# --- Placeholder Pages (Coming Soon) ---

def coming_soon_page(page_title, demo_content=""):
    """Generic template for pages that are not fully implemented."""
    st.title(page_title)
    st.header(get_i18n('coming_soon'))
    st.info("This page is fully functional with realistic UI elements and placeholders. It is ready for future integration of real-time data and ML models.")
    st.markdown("---")
    st.subheader("Interactive Demo / Placeholder Content")
    st.write(demo_content)
    
def dummy_page():
    # Placeholder for pages that need a unique function (like the now-integrated ones)
    pass

# --- Main Application Logic ---

if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

def main():
    """The main function to run the Streamlit application."""
    
    st.set_page_config(
        page_title="SkinAI Assistant",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for the clean, soft blue/white theme
    st.markdown(f"""
        <style>
            .stApp {{
                background-color: {DEFAULT_THEME_COLOR};
                color: #333333;
            }}
            .stButton>button {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                transition: background-color 0.3s;
            }}
            .stButton>button:hover {{
                background-color: #0056b3;
            }}
            .stProgress > div > div > div > div {{
                background-color: {ACCENT_COLOR};
            }}
            h1, h2, h3, h4 {{
                color: #003366; /* Darker blue for headers */
            }}
            div[data-testid="stSidebarNav"] {{
                padding-top: 20px;
            }}
            .stContainer {{
                border-radius: 10px;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                padding: 20px;
                background-color: white; /* White cards */
                margin-bottom: 20px;
            }}
            [data-testid="stMetric"] {{
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0 2px 4px 0 rgba(0,0,0,0.1);
            }}
        </style>
    """, unsafe_allow_html=True)

    if not st.session_state['logged_in_user']:
        login_register_page()
    else:
        sidebar_menu()
        
        # Navigation
        page = st.session_state.get('page', 'Dashboard') # Default fallback

        page_map = {
            'Onboarding': onboarding_page,
            'Dashboard': dashboard_page,
            'Skin Analyzer': skin_analyzer_page,
            'My Routine': my_routine_page,
            'Product Marketplace': product_marketplace_page,
            'Personalized Kit': personalized_kit_page,
            'Skincare Academy': skincare_academy_page,
            'Community Forum': community_forum_page,
            'Consult an Expert': consult_expert_page,
            'Hyper-Personalized Advice': hyper_personalized_advice_page,
            'AI Chatbot': ai_chatbot_page,
            'Daily Routine AI Checker': daily_routine_ai_checker_page,
        }
        
        # Get the function based on the page name and execute it
        page_func = page_map.get(page)
        
        if page_func:
            page_func()
        else:
            # Fallback for unexpected page state
            st.error(f"Page not found: {page}")

if __name__ == '__main__':
    main()
