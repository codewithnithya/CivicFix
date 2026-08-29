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


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CivicFix",
    page_icon="🏙️",
    layout="wide"
)


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
# FILE SETTINGS
# =========================================================

DATA_FILE = "complaints.json"


# =========================================================
# LOAD COMPLAINTS
# =========================================================

def load_reports():

    if os.path.exists(DATA_FILE):

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, list):

                    return data

        except Exception:

            return []

    return []


# =========================================================
# SAVE COMPLAINTS
# =========================================================

def save_reports(reports):

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                reports,
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as error:

        st.error(
            f"Could not save complaint data: {error}"
        )


# =========================================================
# SESSION STATE
# =========================================================

SESSION_DEFAULTS = {

    "reports": load_reports(),

    "latitude": None,

    "longitude": None,

    "voice_text": "",

    "image_ai_issue": None,

    "image_confidence": 0,

    "image_hash": None,

    "image_security_checked": False,

    "image_security_status": "Not Checked",

    "image_metadata": {},

    "duplicate_result": None,

}


for key, value in SESSION_DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# CSS
# =========================================================

st.markdown(
    """

<style>

.stApp {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 2rem;
}

.info-box {
    background-color: #e8f1ff;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.success-box {
    background-color: #e9f9ef;
    padding: 20px;
    border-radius: 15px;
    border-left: 6px solid #28a745;
}

.voice-box {
    background-color: #f4edff;
    padding: 15px;
    border-radius: 10px;
}

.security-box {
    background-color: #fff4e5;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid orange;
}

</style>

""",
    unsafe_allow_html=True
)


# =========================================================
# LANGUAGES
# =========================================================

LANGUAGES = {

    "🇬🇧 English": "en-IN",

    "🇮🇳 తెలుగు (Telugu)": "te-IN",

    "🇮🇳 हिन्दी (Hindi)": "hi-IN",

    "🇮🇳 اردو (Urdu)": "ur-IN",

    "🇮🇳 தமிழ் (Tamil)": "ta-IN",

    "🇮🇳 ಕನ್ನಡ (Kannada)": "kn-IN",

    "🇮🇳 മലയാളം (Malayalam)": "ml-IN",

    "🇮🇳 বাংলা (Bengali)": "bn-IN",

    "🇮🇳 मराठी (Marathi)": "mr-IN",

    "🇮🇳 ગુજરાતી (Gujarati)": "gu-IN",

    "🇮🇳 ਪੰਜਾਬੀ (Punjabi)": "pa-IN"

}


# =========================================================
# TRANSLATIONS
# =========================================================

TRANSLATIONS = {


    # =====================================================
    # ENGLISH
    # =====================================================

    "🇬🇧 English": {

        "report_title": "📢 Report a Civic Issue",

        "citizen_details": "📱 Citizen Details",

        "phone": "Your Phone Number",

        "phone_placeholder":
        "Enter your 10 digit mobile number",

        "problem":
        "🚨 What is the Civic Problem?",

        "select_issue":
        "Select Civic Issue",

        "voice":
        "🎤 Speak Your Complaint",

        "voice_info":
        "🎤 Voice recording is optional.",

        "record_voice":
        "🎤 Record your complaint (Optional)",

        "convert_voice":
        "📝 Convert Voice to Text",

        "details":
        "📝 Additional Details",

        "description":
        "Describe the problem (Optional)",

        "description_placeholder":
        "You can leave this empty.",

        "upload":
        "📸 Upload Evidence",

        "upload_image":
        "Upload a photo of the civic problem",

        "check_image":
        "🤖 Check Image Matches Issue",

        "gps":
        "📍 Mandatory GPS Location",

        "gps_warning":
        "⚠️ GPS is required so the worker can reach the exact location.",

        "submit_section":
        "🚀 Submit Complaint",

        "submit":
        "🚨 Submit Civic Complaint",

        "navigate":
        "Navigate"

    },


    # =====================================================
    # TELUGU
    # =====================================================

    "🇮🇳 తెలుగు (Telugu)": {

        "report_title":
        "📢 పౌర సమస్యను నివేదించండి",

        "citizen_details":
        "📱 పౌరుల వివరాలు",

        "phone":
        "మీ ఫోన్ నంబర్",

        "phone_placeholder":
        "మీ 10 అంకెల మొబైల్ నంబర్ నమోదు చేయండి",

        "problem":
        "🚨 పౌర సమస్య ఏమిటి?",

        "select_issue":
        "సమస్యను ఎంచుకోండి",

        "voice":
        "🎤 మీ ఫిర్యాదును మాట్లాడండి",

        "voice_info":
        "🎤 వాయిస్ రికార్డింగ్ ఐచ్చికం.",

        "record_voice":
        "🎤 మీ ఫిర్యాదును రికార్డ్ చేయండి",

        "convert_voice":
        "📝 వాయిస్‌ను టెక్స్ట్‌గా మార్చండి",

        "details":
        "📝 అదనపు వివరాలు",

        "description":
        "సమస్యను వివరించండి",

        "description_placeholder":
        "ఖాళీగా ఉంచవచ్చు.",

        "upload":
        "📸 ఆధారాన్ని అప్‌లోడ్ చేయండి",

        "upload_image":
        "సమస్యకు సంబంధించిన ఫోటో అప్‌లోడ్ చేయండి",

        "check_image":
        "🤖 చిత్రం సమస్యతో సరిపోతుందా చూడండి",

        "gps":
        "📍 తప్పనిసరి GPS స్థానం",

        "gps_warning":
        "⚠️ సరైన ప్రదేశానికి చేరుకోవడానికి GPS అవసరం.",

        "submit_section":
        "🚀 ఫిర్యాదు సమర్పించండి",

        "submit":
        "🚨 పౌర ఫిర్యాదును సమర్పించండి",

        "navigate":
        "నావిగేట్ చేయండి"

    },


    # =====================================================
    # HINDI
    # =====================================================

    "🇮🇳 हिन्दी (Hindi)": {

        "report_title":
        "📢 नागरिक समस्या दर्ज करें",

        "citizen_details":
        "📱 नागरिक विवरण",

        "phone":
        "आपका फोन नंबर",

        "phone_placeholder":
        "अपना 10 अंकों का मोबाइल नंबर दर्ज करें",

        "problem":
        "🚨 नागरिक समस्या क्या है?",

        "select_issue":
        "समस्या चुनें",

        "voice":
        "🎤 अपनी शिकायत बोलें",

        "voice_info":
        "🎤 वॉयस रिकॉर्डिंग वैकल्पिक है।",

        "record_voice":
        "🎤 अपनी शिकायत रिकॉर्ड करें",

        "convert_voice":
        "📝 आवाज़ को टेक्स्ट में बदलें",

        "details":
        "📝 अतिरिक्त विवरण",

        "description":
        "समस्या का विवरण दें",

        "description_placeholder":
        "इसे खाली छोड़ सकते हैं।",

        "upload":
        "📸 प्रमाण अपलोड करें",

        "upload_image":
        "समस्या की फोटो अपलोड करें",

        "check_image":
        "🤖 जांचें कि फोटो समस्या से मेल खाती है",

        "gps":
        "📍 अनिवार्य GPS स्थान",

        "gps_warning":
        "⚠️ कर्मचारी को सही स्थान तक पहुंचने के लिए GPS आवश्यक है।",

        "submit_section":
        "🚀 शिकायत जमा करें",

        "submit":
        "🚨 नागरिक शिकायत जमा करें",

        "navigate":
        "नेविगेट करें"

    }

}


# =========================================================
# GET TRANSLATION
# =========================================================

def get_translation(language):

    return TRANSLATIONS.get(
        language,
        TRANSLATIONS["🇬🇧 English"]
    )


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

    image_bytes = image_file.getvalue()

    return hashlib.sha256(
        image_bytes
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

                tag_name = ExifTags.TAGS.get(
                    tag,
                    tag
                )

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


    # EXACT DUPLICATE IMAGE

    for report in st.session_state.reports:

        if report.get("image_hash") == image_hash:

            result["risk_score"] += 100

            result["reasons"].append(

                f"Exact same image already used in complaint "
                f"{report.get('id')}"

            )


    # NO METADATA

    if not metadata:

        result["risk_score"] += 10

        result["reasons"].append(

            "No EXIF metadata found."

        )


    # SOFTWARE CHECK

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

                f"Suspicious generation software detected: {word}"

            )


    # FINAL STATUS

    if result["risk_score"] >= 100:

        result["status"] = "🔴 Blocked"


    elif result["risk_score"] >= 60:

        result["status"] = "🔴 High Risk"


    elif result["risk_score"] >= 20:

        result["status"] = "🟡 Suspicious"


    return result


# =========================================================
# IMAGE AI
# =========================================================

@st.cache_resource
def load_image_classifier():

    return pipeline(

        "zero-shot-image-classification",

        model="openai/clip-vit-base-patch32"

    )


# =========================================================
# ANALYZE IMAGE
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
# IMAGE LABEL TO ISSUE
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


    lat1 = math.radians(lat1)

    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)

    lon2 = math.radians(lon2)


    dlat = lat2 - lat1

    dlon = lon2 - lon1


    a = (

        math.sin(dlat / 2) ** 2

        +

        math.cos(lat1)

        *

        math.cos(lat2)

        *

        math.sin(dlon / 2) ** 2

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

    possible_duplicates = []


    for report in st.session_state.reports:

        score = 0

        reasons = []


        distance = 999999


        # EXACT IMAGE

        if report.get("image_hash") == image_hash:

            score += 100

            reasons.append(
                "Same image already submitted"
            )


        # SAME ISSUE

        if report.get("issue") == issue:

            score += 25

            reasons.append(
                "Same civic issue"
            )


        # LOCATION

        try:

            distance = calculate_distance(

                latitude,

                longitude,

                float(report["latitude"]),

                float(report["longitude"])

            )


            if distance <= 100:

                score += 45

                reasons.append(

                    f"Very close location "
                    f"({round(distance)} meters)"

                )


            elif distance <= 300:

                score += 25

                reasons.append(

                    f"Nearby location "
                    f"({round(distance)} meters)"

                )

        except Exception:

            pass


        # DESCRIPTION

        similarity = text_similarity(

            description,

            report.get("description", "")

        )


        if similarity >= 0.80:

            score += 30

            reasons.append(

                f"Similar description "
                f"({round(similarity * 100)}%)"

            )


        if score >= 50:

            possible_duplicates.append({

                "report": report,

                "score": score,

                "reasons": reasons,

                "distance": distance

            })


    if possible_duplicates:

        possible_duplicates.sort(

            key=lambda x: x["score"],

            reverse=True

        )


        return possible_duplicates[0]


    return None


# =========================================================
# DEPARTMENT
# =========================================================

def get_department(issue):

    if "Water Leakage" in issue:

        return "🚰 Water Supply Department"


    elif "Drainage" in issue:

        return "🚽 Drainage & Sewer Department"


    elif "Garbage" in issue:

        return "🗑️ Sanitation Department"


    elif "Pothole" in issue:

        return "🛣️ Roads & Infrastructure Department"


    elif "Street Light" in issue:

        return "💡 Electricity Department"


    elif "Flooding" in issue:

        return "🚰 Water & Emergency Department"


    elif "Traffic Signal" in issue:

        return "🚦 Traffic Department"


    elif "Tree" in issue:

        return "🌳 Parks & Public Works Department"


    return "🏛️ Municipal Corporation"


# =========================================================
# WORKERS
# =========================================================

WORKERS = {

    "🚰 Water Supply Department": [

        "👷 Ravi | Water Department",

        "👷 Anil | Water Department"

    ],

    "🚽 Drainage & Sewer Department": [

        "👷 Kumar | Drainage Department",

        "👷 Imran | Drainage Department"

    ],

    "🗑️ Sanitation Department": [

        "👷 Ahmed | Sanitation Department",

        "👷 Lakshmi | Sanitation Department"

    ],

    "🛣️ Roads & Infrastructure Department": [

        "👷 Suresh | Roads Department",

        "👷 Ramesh | Roads Department"

    ],

    "💡 Electricity Department": [

        "👷 Priya | Electricity Department",

        "👷 Deepak | Electricity Department"

    ],

    "🚰 Water & Emergency Department": [

        "👷 Emergency Water Team"

    ],

    "🚦 Traffic Department": [

        "👷 Kiran | Traffic Department"

    ],

    "🌳 Parks & Public Works Department": [

        "👷 Naveen | Public Works"

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

        "major",

        "serious"

    ]


    if any(

        word in text

        for word in high_words

    ):

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

    st.title("🏙️ CivicFix")

    st.caption(
        "Predictive Civic Intelligence Platform"
    )


    st.divider()


    language = st.selectbox(

        "🌐 Language",

        list(LANGUAGES.keys())

    )


    language_code = LANGUAGES[language]


    t = get_translation(language)


    st.divider()


    st.subheader(t["navigate"])


    page = st.radio(

        "",

        [

            "📢 Citizen Portal",

            "🔎 Track Complaint",

            "🏛️ Authority Dashboard",

            "👷 Worker Portal",

            "🧠 Civic Intelligence"

        ]

    )


# =========================================================
# CITIZEN PORTAL
# =========================================================

if page == "📢 Citizen Portal":


    st.title(
        t["report_title"]
    )


    st.markdown(

        """

<div class="info-box">

📱 Select problem → 📸 Upload photo →
🤖 Verify image → 📍 Capture GPS →
🔁 Check duplicates → Submit

</div>

""",

        unsafe_allow_html=True

    )


    # PHONE

    st.subheader(
        t["citizen_details"]
    )


    phone = st.text_input(

        t["phone"],

        placeholder=t["phone_placeholder"]

    )


    # ISSUE

    st.divider()


    st.subheader(
        t["problem"]
    )


    issue_choice = st.selectbox(

        t["select_issue"],

        ISSUES

    )


    # VOICE

    st.divider()


    st.subheader(
        t["voice"]
    )


    audio = st.audio_input(

        t["record_voice"]

    )


    if audio is not None:


        st.audio(audio)


        if VOICE_AVAILABLE:


            if st.button(

                t["convert_voice"]

            ):


                try:


                    recognizer = sr.Recognizer()


                    audio_bytes = audio.getvalue()


                    with tempfile.NamedTemporaryFile(

                        delete=False,

                        suffix=".wav"

                    ) as temp_audio:


                        temp_audio.write(

                            audio_bytes

                        )


                        temp_path = temp_audio.name


                    with sr.AudioFile(

                        temp_path

                    ) as source:


                        audio_data = recognizer.record(

                            source

                        )


                    result = recognizer.recognize_google(

                        audio_data,

                        language=language_code

                    )


                    st.session_state.voice_text = result


                    try:

                        os.remove(temp_path)

                    except Exception:

                        pass


                    st.success(

                        "✅ Voice converted successfully!"

                    )


                    st.rerun()


                except Exception:


                    st.warning(

                        "⚠️ Voice could not be converted."

                    )


    # DESCRIPTION

    st.divider()


    st.subheader(
        t["details"]
    )


    description = st.text_area(

        t["description"],

        value=st.session_state.voice_text,

        placeholder=t["description_placeholder"],

        height=120

    )


    # IMAGE

    st.divider()


    st.subheader(
        t["upload"]
    )


    image_file = st.file_uploader(

        t["upload_image"],

        type=[

            "jpg",

            "jpeg",

            "png"

        ]

    )


    if image_file is not None:


        current_hash = get_image_hash(

            image_file

        )


        # RESET NEW IMAGE

        if st.session_state.image_hash != current_hash:


            st.session_state.image_ai_issue = None

            st.session_state.image_confidence = 0

            st.session_state.image_security_checked = False

            st.session_state.image_security_status = "Not Checked"

            st.session_state.image_hash = current_hash


        image = Image.open(

            image_file

        ).convert("RGB")


        st.image(

            image,

            caption="📸 Uploaded Evidence",

            width="stretch"

        )


        # SECURITY CHECK

        st.markdown(

            "### 🛡️ Evidence Security Check"

        )


        if st.button(

            "🛡️ Check Evidence Security"

        ):


            security_result = check_image_security(

                image,

                current_hash

            )


            st.session_state.image_security_checked = True


            st.session_state.image_security_status = (

                security_result["status"]

            )


            if "Blocked" in security_result["status"]:


                st.error(

                    "🔴 Exact duplicate image detected!"

                )


            elif "High Risk" in security_result["status"]:


                st.error(

                    "🔴 Evidence flagged as high risk."

                )


            elif "Suspicious" in security_result["status"]:


                st.warning(

                    "🟡 Evidence requires manual review."

                )


            else:


                st.success(

                    "🟢 Basic security checks passed."

                )


            if security_result["reasons"]:


                st.markdown(

                    "#### Security Findings"

                )


                for reason in security_result["reasons"]:

                    st.write(
                        f"• {reason}"
                    )


        # IMAGE AI

        st.divider()


        if IMAGE_AI_AVAILABLE:


            if st.button(

                t["check_image"]

            ):


                with st.spinner(

                    "🤖 AI is checking the image..."

                ):


                    results = analyze_civic_image(

                        image

                    )


                if results:


                    best_result = results[0]


                    image_label = (

                        best_result["label"]

                    )


                    confidence = round(

                        best_result["score"] * 100,

                        2

                    )


                    detected_issue = (

                        image_label_to_issue(

                            image_label

                        )

                    )


                    st.session_state.image_ai_issue = (

                        detected_issue

                    )


                    st.session_state.image_confidence = (

                        confidence

                    )


                    if detected_issue == issue_choice:


                        st.success(

                            "✅ Image matches the selected issue!"

                        )


                    else:


                        st.error(

                            "❌ Image does not match selected issue!"

                        )


                        st.write(

                            "Selected:",

                            issue_choice

                        )


                        st.write(

                            "AI Detected:",

                            detected_issue

                        )


                    st.caption(

                        f"AI Confidence: {confidence}%"

                    )


                else:


                    st.warning(

                        "⚠️ AI could not analyze image."

                    )


        else:


            st.warning(

                "⚠️ Image AI package is not available."

            )


    # =====================================================
    # GPS
    # =====================================================

    st.divider()


    st.subheader(
        t["gps"]
    )


    st.warning(
        t["gps_warning"]
    )


    if GPS_AVAILABLE:


        location = streamlit_geolocation()


        if (

            location

            and

            location != "No Location Info"

        ):


            try:


                lat = location.get(

                    "latitude"

                )


                lon = location.get(

                    "longitude"

                )


                if (

                    lat is not None

                    and

                    lon is not None

                ):


                    st.session_state.latitude = (

                        float(lat)

                    )


                    st.session_state.longitude = (

                        float(lon)

                    )


            except Exception:


                st.warning(

                    "⚠️ GPS could not be processed."

                )


    else:


        st.error(

            "❌ GPS package missing."

        )


    # =====================================================
    # GPS RESULTS + MAP
    # =====================================================

    if (

        st.session_state.latitude is not None

        and

        st.session_state.longitude is not None

    ):


        lat = st.session_state.latitude

        lon = st.session_state.longitude


        st.success(

            "✅ GPS Location Captured Successfully!"

        )


        col1, col2 = st.columns(2)


        col1.metric(

            "📍 Latitude",

            f"{lat:.6f}"

        )


        col2.metric(

            "📍 Longitude",

            f"{lon:.6f}"

        )


        st.markdown(

            "### 🗺️ Complaint Location"

        )


        map_data = {

            "lat": [lat],

            "lon": [lon]

        }


        st.map(

            map_data,

            zoom=17

        )


        maps_url = (

            f"https://www.google.com/maps/"

            f"search/?api=1&query={lat},{lon}"

        )


        st.link_button(

            "📍 Open Exact Location in Google Maps",

            maps_url,

            width="stretch"

        )


    # =====================================================
    # SUBMIT
    # =====================================================

    st.divider()


    st.subheader(
        t["submit_section"]
    )


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

        elif image_file is None:


            st.error(

                "❌ Please upload an image."

            )

            st.stop()


        # SECURITY

        elif not st.session_state.image_security_checked:


            st.error(

                "❌ Please complete Evidence Security Check first."

            )

            st.stop()


        # BLOCKED

        elif "Blocked" in (

            st.session_state.image_security_status

        ):


            st.error(

                "❌ Submission blocked because this image was already used."

            )

            st.stop()


        # AI CHECK

        elif (

            st.session_state.image_ai_issue is None

        ):


            st.error(

                "❌ Please run Image AI Check first."

            )

            st.stop()


        elif (

            st.session_state.image_ai_issue

            !=

            issue_choice

        ):


            st.error(

                "❌ Submission blocked! Image does not match issue."

            )

            st.stop()


        # GPS

        elif (

            st.session_state.latitude is None

            or

            st.session_state.longitude is None

        ):


            st.error(

                "❌ GPS location is required."

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


            st.warning(

                f"""

⚠️ Possible duplicate complaint detected!

Existing Complaint: {existing['id']}

Issue: {existing['issue']}

Duplicate Score: {duplicate['score']}

"""

            )


            st.markdown(

                "### Why it may be a duplicate:"

            )


            for reason in duplicate["reasons"]:

                st.write(

                    f"• {reason}"

                )


            st.error(

                "❌ Duplicate complaint submission blocked."

            )


            st.stop()


        # CREATE COMPLAINT

        department = get_department(

            issue_choice

        )


        combined_text = (

            description

            + " "

            + st.session_state.voice_text

        )


        severity = get_severity(

            combined_text,

            issue_choice

        )


        complaint_id = (

            "HACF-"

            +

            str(

                random.randint(

                    100000,

                    999999

                )

            )

        )


        verification_status = (

            "🟢 Basic Verification Passed"

        )


        if "Suspicious" in (

            st.session_state.image_security_status

        ):

            verification_status = (

                "🟡 Manual Review Required"

            )


        report = {


            "id": complaint_id,


            "phone": phone,


            "description":

                description

                if description.strip()

                else "No additional description.",


            "voice_text":

                st.session_state.voice_text

                if st.session_state.voice_text

                else "No voice text provided.",


            "issue": issue_choice,


            "department": department,


            "severity": severity,


            "latitude":

                st.session_state.latitude,


            "longitude":

                st.session_state.longitude,


            "image_hash":

                st.session_state.image_hash,


            "image_confidence":

                st.session_state.image_confidence,


            "verification_status":

                verification_status,


            "status":

                "Submitted",


            "worker":

                "Not Assigned",


            "date":

                datetime.now().strftime(

                    "%d-%m-%Y %I:%M %p"

                )

        }


        # ADD REPORT

        st.session_state.reports.append(

            report

        )


        # SAVE PERMANENTLY

        save_reports(

            st.session_state.reports

        )


        st.success(

            "🎉 Complaint Submitted Successfully!"

        )


        st.balloons()


        st.markdown(

            f"""

<div class="success-box">

<h2>🆔 Complaint ID: {complaint_id}</h2>

📅 <b>Date:</b> {report['date']}<br><br>

📢 <b>Issue:</b> {report['issue']}<br><br>

🏛️ <b>Department:</b> {report['department']}<br><br>

🚨 <b>Severity:</b> {report['severity']}<br><br>

🛡️ <b>Verification:</b>
{report['verification_status']}

</div>

""",

            unsafe_allow_html=True

        )


# =========================================================
# TRACK COMPLAINT
# =========================================================

elif page == "🔎 Track Complaint":


    st.title(
        "🔎 Track Your Complaint"
    )


    complaint_id = st.text_input(

        "Enter Complaint ID"

    )


    if st.button(

        "🔎 Track Complaint"

    ):


        found = None


        for report in st.session_state.reports:


            if (

                report["id"].lower()

                ==

                complaint_id.lower()

            ):


                found = report

                break


        if found:


            st.success(

                "✅ Complaint Found!"

            )


            st.write(
                "📢 Issue:",
                found["issue"]
            )


            st.write(
                "🏛️ Department:",
                found["department"]
            )


            st.write(
                "🚨 Severity:",
                found["severity"]
            )


            st.write(
                "📌 Status:",
                found["status"]
            )


            st.write(
                "👷 Worker:",
                found["worker"]
            )


            st.write(
                "📅 Date:",
                found["date"]
            )


            maps_url = (

                f"https://www.google.com/maps/"

                f"search/?api=1&query="

                f"{found['latitude']},"

                f"{found['longitude']}"

            )


            st.link_button(

                "🗺️ View Complaint Location",

                maps_url,

                width="stretch"

            )


        else:


            st.error(

                "❌ Complaint ID not found."

            )


# =========================================================
# AUTHORITY DASHBOARD
# =========================================================

elif page == "🏛️ Authority Dashboard":


    st.title(
        "🏛️ Authority Dashboard"
    )


    reports = st.session_state.reports


    col1, col2, col3, col4 = st.columns(4)


    total = len(reports)


    pending = len([

        r

        for r in reports

        if r["status"] == "Submitted"

    ])


    assigned = len([

        r

        for r in reports

        if r["worker"] != "Not Assigned"

    ])


    suspicious = len([

        r

        for r in reports

        if "Review" in r.get(

            "verification_status",

            ""

        )

    ])


    col1.metric(
        "📢 Total",
        total
    )


    col2.metric(
        "⏳ Pending",
        pending
    )


    col3.metric(
        "👷 Assigned",
        assigned
    )


    col4.metric(
        "🛡️ Review Required",
        suspicious
    )


    st.divider()


    if not reports:


        st.info(
            "No complaints submitted yet."
        )


    else:


        for i, report in enumerate(reports):


            with st.expander(

                f"🆔 {report['id']} — {report['issue']}"

            ):


                st.write(

                    "📝 Description:",

                    report["description"]

                )


                st.write(

                    "🎤 Voice:",

                    report["voice_text"]

                )


                st.write(

                    "🚨 Severity:",

                    report["severity"]

                )


                st.write(

                    "📌 Status:",

                    report["status"]

                )


                st.write(

                    "📍 Location:",

                    f"{report['latitude']}, "

                    f"{report['longitude']}"

                )


                maps_url = (

                    f"https://www.google.com/maps/"

                    f"search/?api=1&query="

                    f"{report['latitude']},"

                    f"{report['longitude']}"

                )


                st.link_button(

                    "🗺️ View on Google Maps",

                    maps_url

                )


                department_workers = WORKERS.get(

                    report["department"],

                    []

                )


                worker_options = (

                    ["Not Assigned"]

                    +

                    department_workers

                )


                current_worker = report.get(

                    "worker",

                    "Not Assigned"

                )


                index = 0


                if current_worker in worker_options:

                    index = worker_options.index(

                        current_worker

                    )


                worker = st.selectbox(

                    "👷 Assign Worker",

                    worker_options,

                    index=index,

                    key=f"worker_{i}"

                )


                if st.button(

                    "✅ Save Worker Assignment",

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

elif page == "👷 Worker Portal":


    st.title(
        "👷 Worker Portal"
    )


    assigned_reports = [

        report

        for report in st.session_state.reports

        if report["worker"] != "Not Assigned"

    ]


    if not assigned_reports:


        st.warning(

            "⚠️ No complaints assigned yet."

        )


    else:


        for i, report in enumerate(

            assigned_reports

        ):


            st.divider()


            st.subheader(

                f"🆔 {report['id']}"

            )


            st.write(

                "📢 Issue:",

                report["issue"]

            )


            st.write(

                "📝 Description:",

                report["description"]

            )


            st.write(

                "🚨 Severity:",

                report["severity"]

            )


            st.write(

                "👷 Worker:",

                report["worker"]

            )


            maps_url = (

                "https://www.google.com/maps/dir/?api=1"

                f"&destination={report['latitude']},"

                f"{report['longitude']}"

            )


            st.link_button(

                "🗺️ Navigate Using Google Maps",

                maps_url,

                width="stretch"

            )


            status_options = [

                "Assigned",

                "🚗 On The Way",

                "🔧 Work In Progress",

                "✅ Completed"

            ]


            current_status = report.get(

                "status",

                "Assigned"

            )


            status_index = 0


            if current_status in status_options:

                status_index = status_options.index(

                    current_status

                )


            status = st.selectbox(

                "Update Work Status",

                status_options,

                index=status_index,

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

elif page == "🧠 Civic Intelligence":


    st.title(
        "🧠 Civic Intelligence"
    )


    reports = st.session_state.reports


    if not reports:


        st.info(

            "📊 Submit complaints first."

        )


    else:


        issue_count = {}


        for report in reports:


            issue = report["issue"]


            if issue not in issue_count:

                issue_count[issue] = 0


            issue_count[issue] += 1


        st.subheader(

            "📊 Complaint Analysis"

        )


        st.bar_chart(

            issue_count

        )


        most_common = max(

            issue_count,

            key=issue_count.get

        )


        high_priority = len([

            r

            for r in reports

            if "High" in r["severity"]

        ])


        completed = len([

            r

            for r in reports

            if "Completed" in r["status"]

        ])


        pending = len([

            r

            for r in reports

            if r["status"] == "Submitted"

        ])


        st.divider()


        st.subheader(

            "🧠 Civic Intelligence Insights"

        )


        col1, col2, col3, col4 = st.columns(4)


        col1.metric(

            "📢 Total Complaints",

            len(reports)

        )


        col2.metric(

            "🚨 High Priority",

            high_priority

        )


        col3.metric(

            "⏳ Pending",

            pending

        )


        col4.metric(

            "✅ Completed",

            completed

        )


        st.warning(

            f"🔍 Most common issue: {most_common}"

        )


        st.markdown(

            """

### 🔮 Future Predictive Features

- 🔁 Advanced duplicate complaint detection
- 📍 Civic hotspot detection
- 🔮 Recurring problem prediction
- ❤️ Civic Health Score
- 📊 Department performance analysis
- 🤖 Advanced AI-generated image detection

"""

        )
