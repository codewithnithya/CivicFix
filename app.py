import streamlit as st
from datetime import datetime
from PIL import Image
import random
import tempfile
import os

# =========================================================
# GPS
# =========================================================

try:
    from streamlit_geolocation import streamlit_geolocation
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False


# =========================================================
# VOICE RECOGNITION
# =========================================================

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False


# =========================================================
# IMAGE AI
# =========================================================

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
# SESSION STATE
# =========================================================

if "reports" not in st.session_state:
    st.session_state.reports = []

if "latitude" not in st.session_state:
    st.session_state.latitude = None

if "longitude" not in st.session_state:
    st.session_state.longitude = None

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if "image_ai_issue" not in st.session_state:
    st.session_state.image_ai_issue = None

if "image_confidence" not in st.session_state:
    st.session_state.image_confidence = 0

if "checked_image_name" not in st.session_state:
    st.session_state.checked_image_name = None


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

</style>
""", unsafe_allow_html=True)


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
# LOAD IMAGE AI
# =========================================================

@st.cache_resource
def load_image_classifier():

    return pipeline(
        "zero-shot-image-classification",
        model="openai/clip-vit-base-patch32"
    )


# =========================================================
# IMAGE ANALYSIS
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

    except Exception as e:
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
        "👷 Ravi | 🚰 Water Department | 📱 9876543210",
        "👷 Anil | 🚰 Water Department | 📱 9876543220"
    ],

    "🚽 Drainage & Sewer Department": [
        "👷 Kumar | 🚽 Drainage Department | 📱 9876543214",
        "👷 Imran | 🚽 Drainage Department | 📱 9876543224"
    ],

    "🗑️ Sanitation Department": [
        "👷 Ahmed | 🗑️ Sanitation Department | 📱 9876543212",
        "👷 Lakshmi | 🗑️ Sanitation Department | 📱 9876543222"
    ],

    "🛣️ Roads & Infrastructure Department": [
        "👷 Suresh | 🛣️ Roads Department | 📱 9876543211",
        "👷 Ramesh | 🛣️ Roads Department | 📱 9876543221"
    ],

    "💡 Electricity Department": [
        "👷 Priya | 💡 Electricity Department | 📱 9876543213",
        "👷 Deepak | 💡 Electricity Department | 📱 9876543223"
    ],

    "🚰 Water & Emergency Department": [
        "👷 Emergency Water Team | 📱 9876543210"
    ],

    "🚦 Traffic Department": [
        "👷 Kiran | 🚦 Traffic Department | 📱 9876543230"
    ],

    "🌳 Parks & Public Works Department": [
        "👷 Naveen | 🌳 Public Works | 📱 9876543240"
    ],

    "🏛️ Municipal Corporation": [
        "👷 Municipal Officer | 🏛️ Corporation | 📱 9876543250"
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

    st.title("🏙️ CivicFix")

    st.caption("Predictive Civic Intelligence Platform")

    st.divider()

    language = st.selectbox(
        "🌐 Language / భాష / भाषा / زبان",
        list(LANGUAGES.keys())
    )

    language_code = LANGUAGES[language]

    st.divider()

    st.subheader("Navigate")

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

    st.title("📢 Report a Civic Issue")

    st.markdown("""
    <div class="info-box">
    📱 Select the problem → 📸 Upload photo → 📍 Capture GPS → Submit
    </div>
    """, unsafe_allow_html=True)


    # PHONE

    st.subheader("📱 Citizen Details")

    phone = st.text_input(
        "Your Phone Number",
        placeholder="Enter your 10 digit mobile number"
    )


    # ISSUE

    st.divider()

    st.subheader("🚨 What is the Civic Problem?")

    issue_choice = st.selectbox(
        "Select Civic Issue",
        ISSUES
    )


    # VOICE - OPTIONAL

    st.divider()

    st.subheader("🎤 Speak Your Complaint")

    st.markdown("""
    <div class="voice-box">
    🎤 Voice recording is optional. You can record if you want.
    </div>
    """, unsafe_allow_html=True)

    audio = st.audio_input(
        "🎤 Record your complaint (Optional)"
    )

    if audio is not None:

        st.success("🎙️ Voice recorded successfully!")

        st.audio(audio)

        if VOICE_AVAILABLE:

            if st.button("📝 Convert Voice to Text"):

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

                    st.success("✅ Voice converted to text!")

                    st.rerun()

                except Exception:

                    st.warning(
                        "⚠️ Voice was recorded but could not be converted to text."
                    )


    # DESCRIPTION - OPTIONAL

    st.divider()

    st.subheader("📝 Additional Details")

    description = st.text_area(
        "Describe the problem (Optional)",
        value=st.session_state.voice_text,
        placeholder="You can leave this empty.",
        height=120
    )


    # IMAGE - REQUIRED

    st.divider()

    st.subheader("📸 Upload Evidence")

    image_file = st.file_uploader(
        "Upload a photo of the civic problem",
        type=["jpg", "jpeg", "png"]
    )

    if image_file is not None:

        if st.session_state.checked_image_name != image_file.name:

            st.session_state.image_ai_issue = None
            st.session_state.image_confidence = 0

        image = Image.open(image_file).convert("RGB")

        st.image(
            image,
            caption="📸 Uploaded Evidence",
            width="stretch"
        )

        if IMAGE_AI_AVAILABLE:

            if st.button("🤖 Check Image Matches Issue"):

                with st.spinner(
                    "🤖 AI is checking the image..."
                ):

                    results = analyze_civic_image(image)

                if results:

                    best_result = results[0]

                    image_label = best_result["label"]

                    image_confidence = round(
                        best_result["score"] * 100,
                        2
                    )

                    image_ai_issue = image_label_to_issue(
                        image_label
                    )

                    st.session_state.image_ai_issue = image_ai_issue

                    st.session_state.image_confidence = image_confidence

                    st.session_state.checked_image_name = image_file.name

                    if image_ai_issue == issue_choice:

                        st.success(
                            "✅ Image matches the selected issue!"
                        )

                    else:

                        st.error(
                            "❌ Image does not match the selected issue!"
                        )

                        st.write(
                            "Selected:",
                            issue_choice
                        )

                        st.write(
                            "AI Detected:",
                            image_ai_issue
                        )

                    st.caption(
                        f"AI Confidence: {image_confidence}%"
                    )

        else:

            st.error(
                "❌ Image AI package is missing."
            )


    # GPS - REQUIRED

    st.divider()

    st.subheader("📍 Mandatory GPS Location")

    st.warning(
        "⚠️ GPS is required so the worker can reach the exact location."
    )

    if GPS_AVAILABLE:

        location = streamlit_geolocation()

        if location and location != "No Location Info":

            try:

                lat = location.get("latitude")
                lon = location.get("longitude")

                if lat is not None and lon is not None:

                    st.session_state.latitude = float(lat)

                    st.session_state.longitude = float(lon)

            except Exception:

                st.warning(
                    "⚠️ GPS could not be processed."
                )

    else:

        st.error(
            "❌ GPS package missing."
        )


    # GPS RESULTS + GOOGLE MAP

    if (
        st.session_state.latitude is not None
        and st.session_state.longitude is not None
    ):

        lat = st.session_state.latitude

        lon = st.session_state.longitude

        st.success("✅ GPS Location Captured!")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "📍 Latitude",
                f"{lat:.6f}"
            )

        with col2:

            st.metric(
                "📍 Longitude",
                f"{lon:.6f}"
            )


        st.subheader("🗺️ Complaint Location")

        google_map_url = (
            f"https://www.google.com/maps?q="
            f"{lat},{lon}&z=17&output=embed"
        )

        st.components.v1.iframe(
            google_map_url,
            height=450,
            scrolling=False
        )

        st.link_button(
            "🗺️ Open Location in Google Maps",
            f"https://www.google.com/maps?q={lat},{lon}",
            width="stretch"
        )

    else:

        st.info(
            "📍 Please allow browser location permission."
        )


    # SUBMIT

    st.divider()

    st.subheader("🚀 Submit Complaint")

    if st.button(
        "🚨 Submit Civic Complaint",
        type="primary",
        width="stretch"
    ):

        if not phone.strip():

            st.error("❌ Phone number is required.")

            st.stop()

        elif len(phone.strip()) < 10:

            st.error("❌ Enter a valid phone number.")

            st.stop()


        # IMAGE REQUIRED

        elif image_file is None:

            st.error(
                "❌ Please upload an image."
            )

            st.stop()


        # IMAGE MUST BE CHECKED

        elif st.session_state.image_ai_issue is None:

            st.error(
                "❌ Please click 'Check Image Matches Issue' first."
            )

            st.stop()


        # IMAGE MUST MATCH SELECTED ISSUE

        elif st.session_state.image_ai_issue != issue_choice:

            st.error(
                "❌ Submission blocked! Image does not match the selected issue."
            )

            st.write(
                "Selected Issue:",
                issue_choice
            )

            st.write(
                "AI Detected:",
                st.session_state.image_ai_issue
            )

            st.stop()


        # GPS REQUIRED

        elif (
            st.session_state.latitude is None
            or st.session_state.longitude is None
        ):

            st.error(
                "❌ GPS location is required."
            )

            st.stop()


        # SAVE REPORT

        issue = issue_choice

        department = get_department(issue)

        combined_text = (
            description + " " +
            st.session_state.voice_text
        )

        severity = get_severity(
            combined_text,
            issue
        )

        complaint_id = (
            "HACF-" +
            str(random.randint(1000, 9999))
        )

        report = {

            "id": complaint_id,

            "phone": phone,

            "description": (
                description
                if description.strip()
                else "No additional description."
            ),

            "voice_text": (
                st.session_state.voice_text
                if st.session_state.voice_text
                else "No voice text provided."
            ),

            "issue": issue,

            "department": department,

            "severity": severity,

            "latitude": st.session_state.latitude,

            "longitude": st.session_state.longitude,

            "status": "Submitted",

            "worker": "Not Assigned",

            "date": datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )
        }

        st.session_state.reports.append(report)

        st.success(
            "🎉 Complaint Submitted Successfully!"
        )

        st.balloons()

        st.markdown(
            f"""
            <div class="success-box">

            <h2>🆔 Complaint ID: {complaint_id}</h2>

            📅 <b>Date & Time:</b> {report['date']}<br><br>

            📢 <b>Issue:</b> {issue}<br><br>

            🏛️ <b>Department:</b> {department}<br><br>

            🚨 <b>Severity:</b> {severity}<br><br>

            📍 <b>Latitude:</b> {report['latitude']}<br><br>

            📍 <b>Longitude:</b> {report['longitude']}

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# TRACK COMPLAINT
# =========================================================

elif page == "🔎 Track Complaint":

    st.title("🔎 Track Your Complaint")

    complaint_id = st.text_input(
        "Enter Complaint ID",
        placeholder="Example: HACF-1003"
    )

    if st.button("🔎 Track Complaint"):

        found = None

        for report in st.session_state.reports:

            if report["id"].lower() == complaint_id.lower():

                found = report

                break

        if found:

            st.success("✅ Complaint Found!")

            st.write("📢 Issue:", found["issue"])

            st.write("🏛️ Department:", found["department"])

            st.write("🚨 Severity:", found["severity"])

            st.write("📌 Status:", found["status"])

            st.write("👷 Worker:", found["worker"])

            st.write("📅 Date:", found["date"])

            st.write("📍 Latitude:", found["latitude"])

            st.write("📍 Longitude:", found["longitude"])

            st.link_button(
                "🗺️ View Location in Google Maps",
                f"https://www.google.com/maps?q="
                f"{found['latitude']},{found['longitude']}",
                width="stretch"
            )

        else:

            st.error("❌ Complaint ID not found.")


# =========================================================
# AUTHORITY DASHBOARD
# =========================================================

elif page == "🏛️ Authority Dashboard":

    st.title("🏛️ Authority Dashboard")

    reports = st.session_state.reports

    col1, col2, col3 = st.columns(3)

    total = len(reports)

    pending = len([
        r for r in reports
        if r["status"] == "Submitted"
    ])

    assigned = len([
        r for r in reports
        if r["worker"] != "Not Assigned"
    ])

    col1.metric("📢 Total Complaints", total)

    col2.metric("⏳ Pending", pending)

    col3.metric("👷 Assigned", assigned)

    st.divider()

    if not reports:

        st.info("No complaints submitted yet.")

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
                    "🏛️ Department:",
                    report["department"]
                )

                st.write(
                    "🚨 Severity:",
                    report["severity"]
                )

                st.write(
                    "📍 Latitude:",
                    report["latitude"]
                )

                st.write(
                    "📍 Longitude:",
                    report["longitude"]
                )

                department_workers = WORKERS.get(
                    report["department"],
                    []
                )

                worker_options = (
                    ["Not Assigned"] +
                    department_workers
                )

                worker = st.selectbox(
                    "👷 Assign Related Department Worker",
                    worker_options,
                    key=f"worker_{i}"
                )

                if st.button(
                    "✅ Assign Worker",
                    key=f"assign_{i}"
                ):

                    report["worker"] = worker

                    if worker != "Not Assigned":

                        report["status"] = "Assigned"

                    st.success(
                        "✅ Correct department worker assigned!"
                    )

                    st.rerun()


# =========================================================
# WORKER PORTAL
# =========================================================

elif page == "👷 Worker Portal":

    st.title("👷 Worker Portal")

    st.info(
        "👷 Workers can see assigned complaints and navigate to the exact location."
    )

    assigned_reports = [

        report for report in st.session_state.reports

        if report["worker"] != "Not Assigned"
    ]

    if not assigned_reports:

        st.warning(
            "⚠️ No complaints assigned yet."
        )

    else:

        for i, report in enumerate(assigned_reports):

            st.divider()

            st.subheader(
                f"🆔 {report['id']}"
            )

            st.write(
                "📢 Issue:",
                report["issue"]
            )

            st.write(
                "🏛️ Department:",
                report["department"]
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
                "👷 Assigned Worker:",
                report["worker"]
            )

            st.write(
                "📍 Latitude:",
                report["latitude"]
            )

            st.write(
                "📍 Longitude:",
                report["longitude"]
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

            status = st.selectbox(

                "Update Work Status",

                [
                    "Assigned",
                    "🚗 On The Way",
                    "🔧 Work In Progress",
                    "✅ Completed"
                ],

                key=f"status_{i}"
            )

            if st.button(
                "Update Status",
                key=f"update_{i}"
            ):

                report["status"] = status

                st.success(
                    "✅ Status Updated Successfully!"
                )

                st.rerun()


# =========================================================
# CIVIC INTELLIGENCE
# =========================================================

elif page == "🧠 Civic Intelligence":

    st.title("🧠 Civic Intelligence")

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

        st.subheader("📊 Complaint Analysis")

        st.bar_chart(issue_count)

        st.divider()

        most_common = max(
            issue_count,
            key=issue_count.get
        )

        high_priority = len([

            r for r in reports

            if "High" in r["severity"]

        ])

        st.subheader("🧠 AI Civic Insight")

        st.info(
            f"📊 Total complaints: {len(reports)}"
        )

        st.warning(
            f"🔍 Most common issue: {most_common}"
        )

        if high_priority > 0:

            st.error(
                f"🚨 High priority issues: {high_priority}"
            )

        else:

            st.success(
                "🟢 No high-priority emergencies detected."
            )

        st.markdown("""
### 🔮 Future Predictive Features

- 🔁 Duplicate complaint detection
- 📍 Civic hotspot detection
- 🔮 Recurring problem prediction
- ❤️ Civic Health Score
- 📊 Department performance analysis
""")
