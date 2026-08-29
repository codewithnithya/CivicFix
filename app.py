import streamlit as st
from datetime import datetime
from PIL import Image, ExifTags
import random
import tempfile
import os
import hashlib
import math
import json
from difflib import SequenceMatcher

import folium
from streamlit_folium import st_folium


# =========================================================
# OPTIONAL PACKAGES
# =========================================================

try:
    from streamlit_geolocation import streamlit_geolocation
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False


try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False


try:
    from transformers import pipeline
    IMAGE_AI_AVAILABLE = True
except ImportError:
    IMAGE_AI_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CivicFix",
    page_icon="🏙️",
    layout="wide"
)


# =========================================================
# DATABASE FILE
# =========================================================

DATA_FILE = "complaints.json"


# =========================================================
# NORMALIZE OLD / INCOMPLETE REPORTS
# THIS FIXES KeyError: id, issue, worker, etc.
# =========================================================

def normalize_report(report, index=0):

    if not isinstance(report, dict):
        report = {}

    normalized = {
        "id": report.get(
            "id",
            f"OLD-{index + 1:04d}"
        ),

        "phone": report.get(
            "phone",
            "Not Available"
        ),

        "issue": report.get(
            "issue",
            "🏚️ Other Civic Issue"
        ),

        "description": report.get(
            "description",
            "No description provided"
        ),

        "voice_text": report.get(
            "voice_text",
            ""
        ),

        "department": report.get(
            "department",
            "🏛️ Municipal Corporation"
        ),

        "severity": report.get(
            "severity",
            "🟢 Low"
        ),

        "latitude": report.get(
            "latitude",
            None
        ),

        "longitude": report.get(
            "longitude",
            None
        ),

        "image_hash": report.get(
            "image_hash",
            ""
        ),

        "image_confidence": report.get(
            "image_confidence",
            0
        ),

        "verification_status": report.get(
            "verification_status",
            "Not Checked"
        ),

        "status": report.get(
            "status",
            "Submitted"
        ),

        "worker": report.get(
            "worker",
            "Not Assigned"
        ),

        "date": report.get(
            "date",
            "Unknown"
        )
    }

    return normalized


# =========================================================
# LOAD REPORTS
# =========================================================

def load_reports():

    if not os.path.exists(DATA_FILE):
        return []

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):
            return []

        normalized_reports = []

        for index, report in enumerate(data):

            normalized_reports.append(
                normalize_report(report, index)
            )

        return normalized_reports

    except Exception:

        return []


# =========================================================
# SAVE REPORTS
# =========================================================

def save_reports(reports):

    try:

        clean_reports = []

        for index, report in enumerate(reports):

            clean_reports.append(
                normalize_report(report, index)
            )

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                clean_reports,
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as e:

        st.error(
            f"Could not save complaint: {e}"
        )


# =========================================================
# SESSION STATE
# =========================================================

SESSION_DEFAULTS = {

    "reports": load_reports(),

    # GPS
    "latitude": None,
    "longitude": None,
    "gps_captured": False,

    # Voice
    "voice_text": "",

    # Image
    "image_hash": None,
    "uploaded_image_name": None,

    # AI
    "image_ai_issue": None,
    "image_confidence": 0,
    "image_ai_checked": False,

    # Security
    "image_security_checked": False,
    "image_security_status": "Not Checked",

    # Duplicate
    "duplicate_result": None,

    # Form
    "submission_success": False,
    "last_complaint_id": None
}


for key, value in SESSION_DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 2rem;
}

.info-box {
    background-color: #e8f1ff;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 15px;
}

.success-box {
    background-color: #e9f9ef;
    padding: 20px;
    border-radius: 15px;
    border-left: 6px solid #28a745;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LANGUAGES
# =========================================================

LANGUAGES = {

    "🇬🇧 English": "en-IN",
    "🇮🇳 తెలుగు (Telugu)": "te-IN",
    "🇮🇳 हिन्दी (Hindi)": "hi-IN"
}


# =========================================================
# TRANSLATIONS
# =========================================================

TRANSLATIONS = {

    "🇬🇧 English": {

        "app_title": "🏙️ CivicFix",
        "subtitle": "AI-Powered Civic Issue Reporting Platform",

        "navigation": "🧭 Navigation",

        "citizen": "📢 Citizen Portal",
        "track": "🔎 Track Complaint",
        "authority": "🏛️ Authority Dashboard",
        "worker": "👷 Worker Portal",
        "intelligence": "🧠 Civic Intelligence",

        "report_title": "📢 Report a Civic Issue",

        "phone": "📱 Phone Number",

        "issue": "🚨 Select Civic Issue",

        "voice": "🎤 Speak Your Complaint",
        "record": "🎤 Record Complaint",
        "convert": "📝 Convert Voice to Text",

        "description": "📝 Describe the Problem",

        "upload": "📸 Upload Evidence",

        "gps": "📍 Real GPS Location",

        "submit": "🚀 Submit Complaint"
    },


    "🇮🇳 తెలుగు (Telugu)": {

        "app_title": "🏙️ సివిక్‌ఫిక్స్",
        "subtitle": "AI ఆధారిత పౌర సమస్యల నివేదిక ప్లాట్‌ఫారమ్",

        "navigation": "🧭 నావిగేషన్",

        "citizen": "📢 పౌరుల పోర్టల్",
        "track": "🔎 ఫిర్యాదు ట్రాక్ చేయండి",
        "authority": "🏛️ అధికారుల డాష్‌బోర్డ్",
        "worker": "👷 కార్మికుల పోర్టల్",
        "intelligence": "🧠 సివిక్ ఇంటెలిజెన్స్",

        "report_title": "📢 పౌర సమస్యను నివేదించండి",

        "phone": "📱 ఫోన్ నంబర్",

        "issue": "🚨 సమస్యను ఎంచుకోండి",

        "voice": "🎤 మీ ఫిర్యాదును మాట్లాడండి",
        "record": "🎤 ఫిర్యాదు రికార్డ్ చేయండి",
        "convert": "📝 వాయిస్‌ను టెక్స్ట్‌గా మార్చండి",

        "description": "📝 సమస్యను వివరించండి",

        "upload": "📸 ఆధారాన్ని అప్‌లోడ్ చేయండి",

        "gps": "📍 నిజమైన GPS స్థానం",

        "submit": "🚀 ఫిర్యాదు సమర్పించండి"
    },


    "🇮🇳 हिन्दी (Hindi)": {

        "app_title": "🏙️ सिविकफिक्स",
        "subtitle": "AI आधारित नागरिक समस्या रिपोर्टिंग प्लेटफॉर्म",

        "navigation": "🧭 नेविगेशन",

        "citizen": "📢 नागरिक पोर्टल",
        "track": "🔎 शिकायत ट्रैक करें",
        "authority": "🏛️ अधिकारी डैशबोर्ड",
        "worker": "👷 कर्मचारी पोर्टल",
        "intelligence": "🧠 सिविक इंटेलिजेंस",

        "report_title": "📢 नागरिक समस्या रिपोर्ट करें",

        "phone": "📱 फोन नंबर",

        "issue": "🚨 समस्या चुनें",

        "voice": "🎤 अपनी शिकायत बोलें",
        "record": "🎤 शिकायत रिकॉर्ड करें",
        "convert": "📝 आवाज़ को टेक्स्ट में बदलें",

        "description": "📝 समस्या का वर्णन करें",

        "upload": "📸 सबूत अपलोड करें",

        "gps": "📍 वास्तविक GPS स्थान",

        "submit": "🚀 शिकायत जमा करें"
    }
}


# =========================================================
# CIVIC ISSUES
# =========================================================

ISSUES = [

    "💧 Water Leakage",
    "🚰 Drainage / Sewer Problem",
    "🗑️ Garbage / Waste Problem",
    "🕳️ Pothole / Road Damage",
    "💡 Street Light Problem",
    "🌊 Water Overflow / Flooding",
    "🚦 Traffic Signal Problem",
    "🌳 Tree / Public Space Problem",
    "🏚️ Other Civic Issue"
]


# =========================================================
# IMAGE HASH
# =========================================================

def get_image_hash(image_file):

    return hashlib.sha256(
        image_file.getvalue()
    ).hexdigest()


# =========================================================
# IMAGE METADATA
# =========================================================

def get_image_metadata(image):

    metadata = {}

    try:

        exif_data = image.getexif()

        if exif_data:

            for tag, value in exif_data.items():

                tag_name = ExifTags.TAGS.get(tag, tag)

                metadata[str(tag_name)] = str(value)

    except Exception:
        pass

    return metadata


# =========================================================
# IMAGE SECURITY
# =========================================================

def check_image_security(image, image_hash):

    result = {

        "status": "🟢 Normal",
        "risk_score": 0,
        "reasons": []
    }

    metadata = get_image_metadata(image)

    for report in st.session_state.reports:

        if report.get("image_hash") == image_hash and image_hash:

            result["risk_score"] += 100

            result["reasons"].append(
                f"Exact image already used in {report.get('id', 'Unknown')}"
            )

    software = metadata.get(
        "Software",
        ""
    ).lower()

    suspicious_words = [

        "stable diffusion",
        "midjourney",
        "dall-e",
        "generative",
        "photoshop generative"
    ]

    for word in suspicious_words:

        if word in software:

            result["risk_score"] += 60

            result["reasons"].append(
                f"Possible generated image software: {word}"
            )

    if result["risk_score"] >= 100:

        result["status"] = "🔴 Blocked"

    elif result["risk_score"] >= 60:

        result["status"] = "🔴 High Risk"

    elif result["risk_score"] >= 20:

        result["status"] = "🟡 Suspicious"

    return result


# =========================================================
# LOAD AI MODEL
# =========================================================

@st.cache_resource
def load_image_classifier():

    return pipeline(

        "zero-shot-image-classification",

        model="openai/clip-vit-base-patch32"
    )


# =========================================================
# AI IMAGE ANALYSIS
# =========================================================

def analyze_civic_image(image):

    if not IMAGE_AI_AVAILABLE:

        return None

    try:

        classifier = load_image_classifier()

        labels = [

            "water leakage or broken water pipe",
            "drainage or sewage problem",
            "garbage or waste on the street",
            "pothole or damaged road",
            "broken street light",
            "flooded street",
            "traffic signal problem",
            "tree problem",
            "other civic problem"
        ]

        return classifier(

            image,

            candidate_labels=labels
        )

    except Exception:

        return None


# =========================================================
# AI LABEL TO ISSUE
# =========================================================

def image_label_to_issue(label):

    label = label.lower()

    if "water leakage" in label or "water pipe" in label:

        return "💧 Water Leakage"

    elif "drainage" in label or "sewage" in label:

        return "🚰 Drainage / Sewer Problem"

    elif "garbage" in label or "waste" in label:

        return "🗑️ Garbage / Waste Problem"

    elif "pothole" in label or "damaged road" in label:

        return "🕳️ Pothole / Road Damage"

    elif "street light" in label:

        return "💡 Street Light Problem"

    elif "flooded" in label:

        return "🌊 Water Overflow / Flooding"

    elif "traffic signal" in label:

        return "🚦 Traffic Signal Problem"

    elif "tree" in label:

        return "🌳 Tree / Public Space Problem"

    return "🏚️ Other Civic Issue"


# =========================================================
# GPS DISTANCE
# =========================================================

def calculate_distance(lat1, lon1, lat2, lon2):

    radius = 6371000

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))

    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (

        math.sin(dlat / 2) ** 2

        +

        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radius * c


# =========================================================
# TEXT SIMILARITY
# =========================================================

def text_similarity(text1, text2):

    if not text1 or not text2:

        return 0

    return SequenceMatcher(

        None,

        text1.lower(),

        text2.lower()

    ).ratio()


# =========================================================
# DUPLICATE DETECTION
# =========================================================

def find_duplicate(
    issue,
    description,
    latitude,
    longitude,
    image_hash
):

    duplicates = []

    for report in st.session_state.reports:

        score = 0
        reasons = []

        if report.get("image_hash") == image_hash and image_hash:

            score += 100

            reasons.append("Same image")

        if report.get("issue") == issue:

            score += 25

            reasons.append("Same civic issue")

        try:

            report_lat = report.get("latitude")
            report_lon = report.get("longitude")

            if report_lat is not None and report_lon is not None:

                distance = calculate_distance(

                    latitude,
                    longitude,

                    report_lat,
                    report_lon
                )

                if distance <= 100:

                    score += 45

                    reasons.append(
                        f"Same location area ({round(distance)}m)"
                    )

                elif distance <= 300:

                    score += 25

                    reasons.append(
                        f"Nearby location ({round(distance)}m)"
                    )

        except Exception:

            pass

        similarity = text_similarity(

            description,

            report.get(
                "description",
                ""
            )
        )

        if similarity >= 0.80:

            score += 30

            reasons.append(
                f"Similar description ({round(similarity * 100)}%)"
            )

        if score >= 50:

            duplicates.append({

                "report": report,

                "score": score,

                "reasons": reasons
            })

    if duplicates:

        duplicates.sort(

            key=lambda x: x["score"],

            reverse=True
        )

        return duplicates[0]

    return None


# =========================================================
# DEPARTMENT
# =========================================================

def get_department(issue):

    if "Water Leakage" in issue:

        return "🚰 Water Supply Department"

    elif "Drainage" in issue:

        return "🚽 Drainage Department"

    elif "Garbage" in issue:

        return "🗑️ Sanitation Department"

    elif "Pothole" in issue:

        return "🛣️ Roads Department"

    elif "Street Light" in issue:

        return "💡 Electricity Department"

    elif "Flooding" in issue:

        return "🚨 Emergency Department"

    elif "Traffic Signal" in issue:

        return "🚦 Traffic Department"

    elif "Tree" in issue:

        return "🌳 Public Works Department"

    return "🏛️ Municipal Corporation"


# =========================================================
# WORKERS
# =========================================================

WORKERS = {

    "🚰 Water Supply Department": [
        "👷 Ravi",
        "👷 Anil"
    ],

    "🚽 Drainage Department": [
        "👷 Kumar",
        "👷 Imran"
    ],

    "🗑️ Sanitation Department": [
        "👷 Ahmed",
        "👷 Lakshmi"
    ],

    "🛣️ Roads Department": [
        "👷 Suresh",
        "👷 Ramesh"
    ],

    "💡 Electricity Department": [
        "👷 Priya",
        "👷 Deepak"
    ],

    "🚨 Emergency Department": [
        "👷 Emergency Team"
    ],

    "🚦 Traffic Department": [
        "👷 Kiran"
    ],

    "🌳 Public Works Department": [
        "👷 Naveen"
    ],

    "🏛️ Municipal Corporation": [
        "👷 Municipal Officer"
    ]
}


# =========================================================
# SEVERITY
# =========================================================

def get_severity(text, issue):

    text = text.lower()

    high_words = [

        "emergency",
        "danger",
        "dangerous",
        "accident",
        "flood",
        "injury",
        "urgent",
        "major"
    ]

    if any(word in text for word in high_words):

        return "🔴 High"

    elif "Flooding" in issue:

        return "🔴 High"

    elif issue != "🏚️ Other Civic Issue":

        return "🟠 Medium"

    return "🟢 Low"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    language = st.selectbox(

        "🌐 Language / भाषा",

        list(LANGUAGES.keys())
    )

    language_code = LANGUAGES[language]

    t = TRANSLATIONS.get(

        language,

        TRANSLATIONS["🇬🇧 English"]
    )

    st.title(t["app_title"])

    st.caption(t["subtitle"])

    st.divider()

    page_options = {

        t["citizen"]: "citizen",
        t["track"]: "track",
        t["authority"]: "authority",
        t["worker"]: "worker",
        t["intelligence"]: "intelligence"
    }

    page_label = st.radio(

        t["navigation"],

        list(page_options.keys())
    )

    page = page_options[page_label]


# =========================================================
# CITIZEN PORTAL
# =========================================================

if page == "citizen":

    st.title(t["report_title"])

    st.markdown("""
    <div class="info-box">
    📱 Details → 📸 Evidence → 🤖 AI Verification →
    📍 Real GPS → 🗺️ Map → 🔁 Duplicate Check → 🚀 Submit
    </div>
    """, unsafe_allow_html=True)


    # PHONE

    phone = st.text_input(

        t["phone"],

        placeholder="Enter 10 digit mobile number"
    )


    # ISSUE

    st.divider()

    issue_choice = st.selectbox(

        t["issue"],

        ISSUES
    )


    # VOICE

    st.divider()

    st.subheader(t["voice"])

    audio = st.audio_input(t["record"])

    if audio is not None:

        st.audio(audio)

        if VOICE_AVAILABLE:

            if st.button(t["convert"]):

                try:

                    recognizer = sr.Recognizer()

                    audio_bytes = audio.getvalue()

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".wav"
                    ) as temp_audio:

                        temp_audio.write(audio_bytes)

                        temp_path = temp_audio.name


                    with sr.AudioFile(temp_path) as source:

                        audio_data = recognizer.record(source)


                    result = recognizer.recognize_google(

                        audio_data,

                        language=language_code
                    )


                    st.session_state.voice_text = result


                    try:

                        os.remove(temp_path)

                    except:

                        pass


                    st.success(
                        "✅ Voice converted to text!"
                    )

                    st.rerun()


                except Exception:

                    st.error(
                        "❌ Voice conversion failed. Try speaking clearly."
                    )


        else:

            st.warning(
                "Install SpeechRecognition package."
            )


    # DESCRIPTION

    st.divider()

    description = st.text_area(

        t["description"],

        value=st.session_state.voice_text,

        height=150
    )


    # IMAGE

    st.divider()

    st.subheader(t["upload"])

    image_file = st.file_uploader(

        "Upload a real photo of the civic problem",

        type=["jpg", "jpeg", "png"]
    )


    if image_file is not None:

        current_hash = get_image_hash(image_file)


        if st.session_state.image_hash != current_hash:

            st.session_state.image_hash = current_hash

            st.session_state.image_ai_issue = None
            st.session_state.image_confidence = 0
            st.session_state.image_ai_checked = False

            st.session_state.image_security_checked = False

            st.session_state.image_security_status = "Not Checked"


        image = Image.open(image_file).convert("RGB")


        st.image(

            image,

            caption="📸 Uploaded Civic Evidence",

            width="stretch"
        )


        # SECURITY

        st.markdown("### 🛡️ Evidence Security")

        if st.button("🛡️ Check Evidence Security"):

            result = check_image_security(

                image,

                current_hash
            )

            st.session_state.image_security_checked = True

            st.session_state.image_security_status = result["status"]


            if "Blocked" in result["status"]:

                st.error(
                    "🔴 This exact image was already used!"
                )

            elif "High Risk" in result["status"]:

                st.error(
                    "🔴 Image is high risk."
                )

            elif "Suspicious" in result["status"]:

                st.warning(
                    "🟡 Image requires manual review."
                )

            else:

                st.success(
                    "🟢 Evidence security passed!"
                )


            for reason in result["reasons"]:

                st.write("•", reason)


        # AI IMAGE CHECK

        st.divider()

        st.markdown("### 🤖 AI Civic Image Verification")

        if IMAGE_AI_AVAILABLE:

            if st.button(
                "🤖 Check Image Matches Civic Problem"
            ):

                with st.spinner(
                    "🤖 AI is checking the image..."
                ):

                    results = analyze_civic_image(image)


                if results:

                    best = results[0]

                    detected_label = best["label"]

                    confidence = round(
                        best["score"] * 100,
                        2
                    )

                    detected_issue = image_label_to_issue(
                        detected_label
                    )


                    st.session_state.image_ai_issue = detected_issue

                    st.session_state.image_confidence = confidence

                    st.session_state.image_ai_checked = True


                    st.write(
                        "🤖 AI detected:",
                        detected_issue
                    )

                    st.write(
                        f"📊 Confidence: {confidence}%"
                    )


                    if detected_issue == issue_choice:

                        st.success(
                            "✅ AI confirms the image matches the selected civic problem!"
                        )

                    else:

                        st.error(
                            "❌ AI says the image does NOT match the selected civic problem."
                        )

                        st.write(
                            "Selected:",
                            issue_choice
                        )

                        st.write(
                            "AI detected:",
                            detected_issue
                        )

                else:

                    st.error(
                        "❌ AI could not analyze the image."
                    )

        else:

            st.warning(
                "⚠️ AI packages not installed."
            )


    # =====================================================
    # REAL GPS LOCATION
    # =====================================================

    st.divider()

    st.subheader(t["gps"])

    st.info(
        "👇 Use the location button below and allow location permission in your browser."
    )


    if GPS_AVAILABLE:

        location = streamlit_geolocation()


        if location == "No Location Info":

            st.warning(
                "📍 Click the location button above and allow browser location permission."
            )

        elif location:

            try:

                lat = location.get("latitude")

                lon = location.get("longitude")

                accuracy = location.get("accuracy")


                if lat is not None and lon is not None:

                    st.session_state.latitude = float(lat)

                    st.session_state.longitude = float(lon)

                    st.session_state.gps_captured = True


                    st.success(
                        "✅ Real GPS Location Captured!"
                    )


                    if accuracy is not None:

                        st.caption(
                            f"🎯 GPS Accuracy: approximately {round(float(accuracy))} meters"
                        )

            except Exception as e:

                st.error(
                    f"❌ Could not read GPS location: {e}"
                )

    else:

        st.error(
            "❌ streamlit-geolocation package is not available."
        )


    # =====================================================
    # GPS MAP
    # =====================================================

    if (

        st.session_state.gps_captured

        and

        st.session_state.latitude is not None

        and

        st.session_state.longitude is not None
    ):

        lat = st.session_state.latitude

        lon = st.session_state.longitude


        st.markdown(
            "### 🗺️ Your Exact Complaint Location"
        )


        c1, c2 = st.columns(2)


        c1.metric(
            "📍 Latitude",
            f"{lat:.6f}"
        )


        c2.metric(
            "📍 Longitude",
            f"{lon:.6f}"
        )


        civic_map = folium.Map(

            location=[lat, lon],

            zoom_start=18,

            control_scale=True
        )


        folium.Marker(

            [lat, lon],

            popup=f"""
            <b>📍 Real Civic Complaint Location</b><br>
            Latitude: {lat:.6f}<br>
            Longitude: {lon:.6f}
            """,

            tooltip="📍 Exact Complaint Location",

            icon=folium.Icon(
                icon="info-sign"
            )

        ).add_to(civic_map)


        folium.Circle(

            location=[lat, lon],

            radius=30,

            popup="GPS Location Area",

            fill=True,

            fill_opacity=0.15

        ).add_to(civic_map)


        st_folium(

            civic_map,

            width=None,

            height=500,

            key="citizen_real_gps_map",

            returned_objects=[]
        )


        maps_url = (

            "https://www.google.com/maps/search/"

            f"?api=1&query={lat},{lon}"
        )


        st.link_button(

            "📍 Open Exact Location in Google Maps",

            maps_url,

            width="stretch"
        )


    else:

        st.warning(
            "📍 GPS location not captured yet."
        )


    # =====================================================
    # SUBMIT
    # =====================================================

    st.divider()

    st.subheader("🚀 Submit Complaint")


    if st.button(

        t["submit"],

        type="primary",

        width="stretch"
    ):


        # PHONE

        if not phone.strip():

            st.error(
                "❌ Phone number is required."
            )

            st.stop()


        # IMAGE

        if image_file is None:

            st.error(
                "❌ Upload a civic problem image."
            )

            st.stop()


        # SECURITY

        if not st.session_state.image_security_checked:

            st.error(
                "❌ Complete Evidence Security Check first."
            )

            st.stop()


        if "Blocked" in st.session_state.image_security_status:

            st.error(
                "❌ This image was already submitted."
            )

            st.stop()


        # AI

        if not st.session_state.image_ai_checked:

            st.error(
                "❌ Complete AI Image Verification first."
            )

            st.stop()


        if st.session_state.image_ai_issue != issue_choice:

            st.error(
                "❌ Submission blocked because AI says the image does not match the selected civic issue."
            )

            st.stop()


        # GPS

        if (

            st.session_state.latitude is None

            or

            st.session_state.longitude is None
        ):

            st.error(
                "❌ Real GPS location is required."
            )

            st.stop()


        # DUPLICATE

        duplicate = find_duplicate(

            issue_choice,

            description,

            st.session_state.latitude,

            st.session_state.longitude,

            st.session_state.image_hash
        )


        if duplicate:

            existing = duplicate["report"]

            st.error(
                "❌ Possible duplicate complaint detected!"
            )

            st.write(
                "Existing Complaint:",
                existing.get("id", "Unknown")
            )

            st.write(
                "Duplicate Score:",
                duplicate["score"]
            )

            st.write("Reasons:")


            for reason in duplicate["reasons"]:

                st.write("•", reason)


            st.stop()


        # CREATE REPORT

        department = get_department(
            issue_choice
        )


        severity = get_severity(

            description + " " + st.session_state.voice_text,

            issue_choice
        )


        complaint_id = (

            "CF-"

            + datetime.now().strftime("%Y%m%d")

            + "-"

            + str(random.randint(1000, 9999))
        )


        report = {

            "id": complaint_id,

            "phone": phone,

            "issue": issue_choice,

            "description": description,

            "voice_text": st.session_state.voice_text,

            "department": department,

            "severity": severity,

            "latitude": st.session_state.latitude,

            "longitude": st.session_state.longitude,

            "image_hash": st.session_state.image_hash,

            "image_confidence":
            st.session_state.image_confidence,

            "verification_status":
            st.session_state.image_security_status,

            "status": "Submitted",

            "worker": "Not Assigned",

            "date":
            datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )
        }


        st.session_state.reports.append(report)

        save_reports(
            st.session_state.reports
        )


        st.success(
            "🎉 Complaint Submitted Successfully!"
        )

        st.balloons()


        st.markdown(f"""

        <div class="success-box">

        <h2>🆔 Complaint ID: {complaint_id}</h2>

        📢 <b>Issue:</b> {issue_choice}<br><br>

        📍 <b>GPS:</b> {st.session_state.latitude:.6f},
        {st.session_state.longitude:.6f}<br><br>

        🏛️ <b>Department:</b> {department}<br><br>

        🚨 <b>Severity:</b> {severity}

        </div>

        """, unsafe_allow_html=True)


# =========================================================
# TRACK COMPLAINT
# =========================================================

elif page == "track":

    st.title("🔎 Track Your Complaint")

    complaint_id = st.text_input(
        "Enter Complaint ID"
    )


    if st.button("🔎 Track Complaint"):

        found = None


        for report in st.session_state.reports:

            report_id = str(
                report.get("id", "")
            )

            if report_id.lower() == complaint_id.lower():

                found = report

                break


        if found:

            st.success(
                "✅ Complaint Found!"
            )

            st.write(
                "📢 Issue:",
                found.get("issue", "Not Available")
            )

            st.write(
                "📝 Description:",
                found.get("description", "Not Available")
            )

            st.write(
                "🏛️ Department:",
                found.get("department", "Not Available")
            )

            st.write(
                "🚨 Severity:",
                found.get("severity", "Not Available")
            )

            st.write(
                "📌 Status:",
                found.get("status", "Submitted")
            )

            st.write(
                "👷 Worker:",
                found.get("worker", "Not Assigned")
            )


            lat = found.get("latitude")

            lon = found.get("longitude")


            if lat is not None and lon is not None:

                track_map = folium.Map(

                    location=[
                        lat,
                        lon
                    ],

                    zoom_start=17
                )


                folium.Marker(

                    [
                        lat,
                        lon
                    ],

                    popup=found.get(
                        "id",
                        "Complaint"
                    ),

                    tooltip="Complaint Location"

                ).add_to(track_map)


                st_folium(

                    track_map,

                    height=450,

                    key="track_map",

                    returned_objects=[]
                )

            else:

                st.warning(
                    "📍 Location data is not available for this complaint."
                )


        else:

            st.error(
                "❌ Complaint ID not found."
            )


# =========================================================
# AUTHORITY DASHBOARD
# =========================================================

elif page == "authority":

    st.title("🏛️ Authority Dashboard")

    reports = st.session_state.reports


    if not reports:

        st.info(
            "No complaints yet."
        )


    else:

        for i, report in enumerate(reports):

            report_id = report.get(
                "id",
                f"Complaint-{i + 1}"
            )

            issue = report.get(
                "issue",
                "🏚️ Other Civic Issue"
            )


            with st.expander(

                f"{report_id} — {issue}"
            ):

                st.write(

                    "📝 Description:",

                    report.get(
                        "description",
                        "Not Available"
                    )
                )


                st.write(

                    "🚨 Severity:",

                    report.get(
                        "severity",
                        "🟢 Low"
                    )
                )


                st.write(

                    "📌 Status:",

                    report.get(
                        "status",
                        "Submitted"
                    )
                )


                lat = report.get("latitude")

                lon = report.get("longitude")


                if lat is not None and lon is not None:

                    authority_map = folium.Map(

                        location=[
                            lat,
                            lon
                        ],

                        zoom_start=16
                    )


                    folium.Marker(

                        [
                            lat,
                            lon
                        ],

                        popup=report_id

                    ).add_to(authority_map)


                    st_folium(

                        authority_map,

                        height=350,

                        key=f"authority_map_{i}",

                        returned_objects=[]
                    )


                department = report.get(
                    "department",
                    "🏛️ Municipal Corporation"
                )


                workers = [

                    "Not Assigned"

                ] + WORKERS.get(
                    department,
                    []
                )


                current = report.get(
                    "worker",
                    "Not Assigned"
                )


                index = (

                    workers.index(current)

                    if current in workers

                    else 0
                )


                worker = st.selectbox(

                    "👷 Assign Worker",

                    workers,

                    index=index,

                    key=f"worker_{i}"
                )


                if st.button(

                    "Assign Worker",

                    key=f"assign_{i}"
                ):

                    report["worker"] = worker


                    if worker != "Not Assigned":

                        report["status"] = "Assigned"


                    save_reports(
                        st.session_state.reports
                    )


                    st.success(
                        "✅ Worker Assigned!"
                    )


                    st.rerun()


# =========================================================
# WORKER PORTAL
# =========================================================

elif page == "worker":

    st.title("👷 Worker Portal")


    assigned_reports = [

        report

        for report in st.session_state.reports

        if report.get(
            "worker",
            "Not Assigned"
        ) != "Not Assigned"
    ]


    if not assigned_reports:

        st.info(
            "No complaints assigned."
        )


    else:

        for i, report in enumerate(assigned_reports):

            st.divider()


            st.subheader(

                f"🆔 {report.get('id', 'Unknown Complaint')}"
            )


            st.write(

                "👷 Assigned Worker:",

                report.get(
                    "worker",
                    "Not Assigned"
                )
            )


            st.write(

                "📢 Issue:",

                report.get(
                    "issue",
                    "Not Available"
                )
            )


            st.write(

                "📝 Description:",

                report.get(
                    "description",
                    "Not Available"
                )
            )


            lat = report.get("latitude")

            lon = report.get("longitude")


            if lat is not None and lon is not None:

                worker_map = folium.Map(

                    location=[
                        lat,
                        lon
                    ],

                    zoom_start=17
                )


                folium.Marker(

                    [
                        lat,
                        lon
                    ],

                    popup="Work Location"

                ).add_to(worker_map)


                st_folium(

                    worker_map,

                    height=400,

                    key=f"worker_map_{i}",

                    returned_objects=[]
                )


                maps_url = (

                    "https://www.google.com/maps/dir/"

                    f"?api=1&destination="

                    f"{lat},"

                    f"{lon}"
                )


                st.link_button(

                    "🗺️ Navigate Using Google Maps",

                    maps_url,

                    width="stretch"
                )


            else:

                st.warning(
                    "📍 GPS location is not available."
                )


            status_options = [

                "Assigned",

                "🚗 On The Way",

                "🔧 Work In Progress",

                "✅ Completed"
            ]


            current = report.get(
                "status",
                "Assigned"
            )


            index = (

                status_options.index(current)

                if current in status_options

                else 0
            )


            status = st.selectbox(

                "Update Status",

                status_options,

                index=index,

                key=f"status_{i}"
            )


            if st.button(

                "Update Status",

                key=f"update_{i}"
            ):

                report["status"] = status


                save_reports(
                    st.session_state.reports
                )


                st.success(
                    "✅ Status Updated!"
                )


                st.rerun()


# =========================================================
# CIVIC INTELLIGENCE
# =========================================================

elif page == "intelligence":

    st.title("🧠 Civic Intelligence")

    reports = st.session_state.reports


    if not reports:

        st.info(
            "📊 Submit complaints first."
        )


    else:

        issue_count = {}


        for report in reports:

            issue = report.get(

                "issue",

                "🏚️ Other Civic Issue"
            )


            issue_count[issue] = (

                issue_count.get(issue, 0)

                + 1
            )


        st.subheader(
            "📊 Complaint Analysis"
        )


        st.bar_chart(
            issue_count
        )


        st.divider()


        st.subheader(
            "🔥 Civic Complaint Map"
        )


        valid_location_reports = [

            report

            for report in reports

            if report.get("latitude") is not None

            and report.get("longitude") is not None
        ]


        if valid_location_reports:

            first = valid_location_reports[0]


            intelligence_map = folium.Map(

                location=[

                    first.get("latitude"),

                    first.get("longitude")
                ],

                zoom_start=13
            )


            for report in valid_location_reports:


                popup = f"""

                <b>{report.get('id', 'Unknown')}</b><br>

                {report.get('issue', 'Other Civic Issue')}<br>

                Status: {report.get('status', 'Submitted')}
                """


                folium.Marker(

                    [

                        report.get("latitude"),

                        report.get("longitude")
                    ],

                    popup=popup,

                    tooltip=report.get(
                        "issue",
                        "Civic Complaint"
                    )

                ).add_to(
                    intelligence_map
                )


            st_folium(

                intelligence_map,

                height=550,

                key="intelligence_map",

                returned_objects=[]
            )


            st.success(
                "🧠 Civic intelligence map generated successfully!"
            )


        else:

            st.warning(
                "📍 No valid GPS locations are available for the intelligence map."
            )
