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
# TRANSLATIONS
# =========================================================

TRANSLATIONS = {

    "🇬🇧 English": {
        "report_title": "📢 Report a Civic Issue",
        "citizen_details": "📱 Citizen Details",
        "phone": "Your Phone Number",
        "phone_placeholder": "Enter your 10 digit mobile number",
        "problem": "🚨 What is the Civic Problem?",
        "select_issue": "Select Civic Issue",
        "voice": "🎤 Speak Your Complaint",
        "voice_info": "🎤 Voice recording is optional. You can record if you want.",
        "record_voice": "🎤 Record your complaint (Optional)",
        "convert_voice": "📝 Convert Voice to Text",
        "details": "📝 Additional Details",
        "description": "Describe the problem (Optional)",
        "description_placeholder": "You can leave this empty.",
        "upload": "📸 Upload Evidence",
        "upload_image": "Upload a photo of the civic problem",
        "check_image": "🤖 Check Image Matches Issue",
        "gps": "📍 Mandatory GPS Location",
        "gps_warning": "⚠️ GPS is required so the worker can reach the exact location.",
        "submit_section": "🚀 Submit Complaint",
        "submit": "🚨 Submit Civic Complaint",
        "navigate": "Navigate"
    },

    "🇮🇳 తెలుగు (Telugu)": {
        "report_title": "📢 పౌర సమస్యను నివేదించండి",
        "citizen_details": "📱 పౌరుల వివరాలు",
        "phone": "మీ ఫోన్ నంబర్",
        "phone_placeholder": "మీ 10 అంకెల మొబైల్ నంబర్ నమోదు చేయండి",
        "problem": "🚨 పౌర సమస్య ఏమిటి?",
        "select_issue": "సమస్యను ఎంచుకోండి",
        "voice": "🎤 మీ ఫిర్యాదును చెప్పండి",
        "voice_info": "🎤 వాయిస్ రికార్డింగ్ ఐచ్చికం.",
        "record_voice": "🎤 మీ ఫిర్యాదును రికార్డ్ చేయండి",
        "convert_voice": "📝 వాయిస్‌ను టెక్స్ట్‌గా మార్చండి",
        "details": "📝 అదనపు వివరాలు",
        "description": "సమస్యను వివరించండి",
        "description_placeholder": "ఖాళీగా వదిలివేయవచ్చు.",
        "upload": "📸 ఆధారాన్ని అప్లోడ్ చేయండి",
        "upload_image": "సమస్య యొక్క ఫోటోను అప్లోడ్ చేయండి",
        "check_image": "🤖 చిత్రం సమస్యను తనిఖీ చేయండి",
        "gps": "📍 GPS స్థానం తప్పనిసరి",
        "gps_warning": "⚠️ కార్మికుడు ఖచ్చితమైన స్థలానికి చేరుకోవడానికి GPS అవసరం.",
        "submit_section": "🚀 ఫిర్యాదు సమర్పించండి",
        "submit": "🚨 ఫిర్యాదు సమర్పించండి",
        "navigate": "నావిగేషన్"
    },

    "🇮🇳 हिन्दी (Hindi)": {
        "report_title": "📢 नागरिक समस्या दर्ज करें",
        "citizen_details": "📱 नागरिक विवरण",
        "phone": "आपका फोन नंबर",
        "phone_placeholder": "अपना 10 अंकों का मोबाइल नंबर दर्ज करें",
        "problem": "🚨 नागरिक समस्या क्या है?",
        "select_issue": "समस्या चुनें",
        "voice": "🎤 अपनी शिकायत बोलें",
        "voice_info": "🎤 वॉयस रिकॉर्डिंग वैकल्पिक है।",
        "record_voice": "🎤 अपनी शिकायत रिकॉर्ड करें",
        "convert_voice": "📝 आवाज़ को टेक्स्ट में बदलें",
        "details": "📝 अतिरिक्त जानकारी",
        "description": "समस्या का विवरण दें",
        "description_placeholder": "इसे खाली छोड़ सकते हैं।",
        "upload": "📸 प्रमाण अपलोड करें",
        "upload_image": "समस्या की फोटो अपलोड करें",
        "check_image": "🤖 फोटो जांचें",
        "gps": "📍 GPS स्थान आवश्यक है",
        "gps_warning": "⚠️ कर्मचारी को सही स्थान तक पहुंचने के लिए GPS आवश्यक है।",
        "submit_section": "🚀 शिकायत जमा करें",
        "submit": "🚨 शिकायत जमा करें",
        "navigate": "नेविगेशन"
    },

    "🇮🇳 اردو (Urdu)": {
        "report_title": "📢 شہری مسئلہ رپورٹ کریں",
        "citizen_details": "📱 شہری تفصیلات",
        "phone": "آپ کا فون نمبر",
        "phone_placeholder": "اپنا 10 ہندسوں کا موبائل نمبر درج کریں",
        "problem": "🚨 شہری مسئلہ کیا ہے؟",
        "select_issue": "مسئلہ منتخب کریں",
        "voice": "🎤 اپنی شکایت بولیں",
        "voice_info": "🎤 وائس ریکارڈنگ اختیاری ہے۔",
        "record_voice": "🎤 شکایت ریکارڈ کریں",
        "convert_voice": "📝 آواز کو متن میں تبدیل کریں",
        "details": "📝 اضافی تفصیلات",
        "description": "مسئلہ بیان کریں",
        "description_placeholder": "خالی چھوڑ سکتے ہیں۔",
        "upload": "📸 ثبوت اپ لوڈ کریں",
        "upload_image": "مسئلے کی تصویر اپ لوڈ کریں",
        "check_image": "🤖 تصویر چیک کریں",
        "gps": "📍 GPS مقام ضروری ہے",
        "gps_warning": "⚠️ کارکن کو صحیح جگہ تک پہنچنے کے لیے GPS ضروری ہے۔",
        "submit_section": "🚀 شکایت جمع کریں",
        "submit": "🚨 شکایت جمع کریں",
        "navigate": "نیویگیٹ"
    },

    "🇮🇳 தமிழ் (Tamil)": {
        "report_title": "📢 குடிமக்கள் பிரச்சினையை புகாரளிக்கவும்",
        "citizen_details": "📱 குடிமக்கள் விவரங்கள்",
        "phone": "உங்கள் தொலைபேசி எண்",
        "phone_placeholder": "10 இலக்க மொபைல் எண்ணை உள்ளிடவும்",
        "problem": "🚨 குடிமக்கள் பிரச்சினை என்ன?",
        "select_issue": "பிரச்சினையை தேர்ந்தெடுக்கவும்",
        "voice": "🎤 உங்கள் புகாரை கூறுங்கள்",
        "voice_info": "🎤 குரல் பதிவு விருப்பமானது.",
        "record_voice": "🎤 புகாரை பதிவு செய்யவும்",
        "convert_voice": "📝 குரலை உரையாக மாற்றவும்",
        "details": "📝 கூடுதல் விவரங்கள்",
        "description": "பிரச்சினையை விவரிக்கவும்",
        "description_placeholder": "காலியாக விடலாம்.",
        "upload": "📸 ஆதாரத்தை பதிவேற்றவும்",
        "upload_image": "பிரச்சினையின் புகைப்படத்தை பதிவேற்றவும்",
        "check_image": "🤖 படத்தை சரிபார்க்கவும்",
        "gps": "📍 GPS இடம் அவசியம்",
        "gps_warning": "⚠️ பணியாளர் சரியான இடத்தை அடைய GPS தேவை.",
        "submit_section": "🚀 புகாரை சமர்ப்பிக்கவும்",
        "submit": "🚨 புகாரை சமர்ப்பிக்கவும்",
        "navigate": "வழிசெலுத்தல்"
    },

    "🇮🇳 ಕನ್ನಡ (Kannada)": {
        "report_title": "📢 ನಾಗರಿಕ ಸಮಸ್ಯೆಯನ್ನು ವರದಿ ಮಾಡಿ",
        "citizen_details": "📱 ನಾಗರಿಕರ ವಿವರಗಳು",
        "phone": "ನಿಮ್ಮ ಫೋನ್ ಸಂಖ್ಯೆ",
        "phone_placeholder": "ನಿಮ್ಮ 10 ಅಂಕಿಯ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ",
        "problem": "🚨 ನಾಗರಿಕ ಸಮಸ್ಯೆ ಏನು?",
        "select_issue": "ಸಮಸ್ಯೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "voice": "🎤 ನಿಮ್ಮ ದೂರನ್ನು ಹೇಳಿ",
        "voice_info": "🎤 ಧ್ವನಿ ರೆಕಾರ್ಡಿಂಗ್ ಐಚ್ಛಿಕವಾಗಿದೆ.",
        "record_voice": "🎤 ದೂರನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ",
        "convert_voice": "📝 ಧ್ವನಿಯನ್ನು ಪಠ್ಯಕ್ಕೆ ಪರಿವರ್ತಿಸಿ",
        "details": "📝 ಹೆಚ್ಚುವರಿ ವಿವರಗಳು",
        "description": "ಸಮಸ್ಯೆಯನ್ನು ವಿವರಿಸಿ",
        "description_placeholder": "ಖಾಲಿ ಬಿಡಬಹುದು.",
        "upload": "📸 ಸಾಕ್ಷ್ಯವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ",
        "upload_image": "ಸಮಸ್ಯೆಯ ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಿ",
        "check_image": "🤖 ಚಿತ್ರವನ್ನು ಪರಿಶೀಲಿಸಿ",
        "gps": "📍 GPS ಸ್ಥಳ ಕಡ್ಡಾಯ",
        "gps_warning": "⚠️ ಕೆಲಸಗಾರನು ಸರಿಯಾದ ಸ್ಥಳವನ್ನು ತಲುಪಲು GPS ಅಗತ್ಯ.",
        "submit_section": "🚀 ದೂರನ್ನು ಸಲ್ಲಿಸಿ",
        "submit": "🚨 ದೂರನ್ನು ಸಲ್ಲಿಸಿ",
        "navigate": "ನ್ಯಾವಿಗೇಟ್"
    },

    "🇮🇳 മലയാളം (Malayalam)": {
        "report_title": "📢 പൗര പ്രശ്നം റിപ്പോർട്ട് ചെയ്യുക",
        "citizen_details": "📱 പൗരന്റെ വിവരങ്ങൾ",
        "phone": "നിങ്ങളുടെ ഫോൺ നമ്പർ",
        "phone_placeholder": "10 അക്ക മൊബൈൽ നമ്പർ നൽകുക",
        "problem": "🚨 പൗര പ്രശ്നം എന്താണ്?",
        "select_issue": "പ്രശ്നം തിരഞ്ഞെടുക്കുക",
        "voice": "🎤 നിങ്ങളുടെ പരാതി പറയുക",
        "voice_info": "🎤 വോയ്സ് റെക്കോർഡിംഗ് ഐച്ഛികമാണ്.",
        "record_voice": "🎤 പരാതി റെക്കോർഡ് ചെയ്യുക",
        "convert_voice": "📝 ശബ്ദം ടെക്സ്റ്റാക്കി മാറ്റുക",
        "details": "📝 അധിക വിവരങ്ങൾ",
        "description": "പ്രശ്നം വിവരിക്കുക",
        "description_placeholder": "ശൂന്യമായി വിടാം.",
        "upload": "📸 തെളിവ് അപ്ലോഡ് ചെയ്യുക",
        "upload_image": "പ്രശ്നത്തിന്റെ ചിത്രം അപ്ലോഡ് ചെയ്യുക",
        "check_image": "🤖 ചിത്രം പരിശോധിക്കുക",
        "gps": "📍 GPS സ്ഥലം നിർബന്ധമാണ്",
        "gps_warning": "⚠️ തൊഴിലാളിക്ക് ശരിയായ സ്ഥലത്തെത്താൻ GPS ആവശ്യമാണ്.",
        "submit_section": "🚀 പരാതി സമർപ്പിക്കുക",
        "submit": "🚨 പരാതി സമർപ്പിക്കുക",
        "navigate": "നാവിഗേറ്റ്"
    },

    "🇮🇳 বাংলা (Bengali)": {
        "report_title": "📢 নাগরিক সমস্যা রিপোর্ট করুন",
        "citizen_details": "📱 নাগরিকের বিবরণ",
        "phone": "আপনার ফোন নম্বর",
        "phone_placeholder": "আপনার 10 সংখ্যার মোবাইল নম্বর লিখুন",
        "problem": "🚨 নাগরিক সমস্যা কী?",
        "select_issue": "সমস্যা নির্বাচন করুন",
        "voice": "🎤 আপনার অভিযোগ বলুন",
        "voice_info": "🎤 ভয়েস রেকর্ডিং ঐচ্ছিক।",
        "record_voice": "🎤 অভিযোগ রেকর্ড করুন",
        "convert_voice": "📝 ভয়েসকে টেক্সটে পরিবর্তন করুন",
        "details": "📝 অতিরিক্ত তথ্য",
        "description": "সমস্যা বর্ণনা করুন",
        "description_placeholder": "খালি রাখতে পারেন।",
        "upload": "📸 প্রমাণ আপলোড করুন",
        "upload_image": "সমস্যার ছবি আপলোড করুন",
        "check_image": "🤖 ছবি পরীক্ষা করুন",
        "gps": "📍 GPS অবস্থান প্রয়োজন",
        "gps_warning": "⚠️ কর্মীকে সঠিক স্থানে পৌঁছাতে GPS প্রয়োজন।",
        "submit_section": "🚀 অভিযোগ জমা দিন",
        "submit": "🚨 অভিযোগ জমা দিন",
        "navigate": "নেভিগেট"
    },

    "🇮🇳 मराठी (Marathi)": {
        "report_title": "📢 नागरी समस्या नोंदवा",
        "citizen_details": "📱 नागरिक तपशील",
        "phone": "तुमचा फोन नंबर",
        "phone_placeholder": "तुमचा 10 अंकी मोबाईल नंबर टाका",
        "problem": "🚨 नागरी समस्या काय आहे?",
        "select_issue": "समस्या निवडा",
        "voice": "🎤 तुमची तक्रार सांगा",
        "voice_info": "🎤 व्हॉइस रेकॉर्डिंग पर्यायी आहे.",
        "record_voice": "🎤 तक्रार रेकॉर्ड करा",
        "convert_voice": "📝 आवाज मजकुरात बदला",
        "details": "📝 अतिरिक्त तपशील",
        "description": "समस्येचे वर्णन करा",
        "description_placeholder": "रिकामे ठेवू शकता.",
        "upload": "📸 पुरावा अपलोड करा",
        "upload_image": "समस्येचा फोटो अपलोड करा",
        "check_image": "🤖 फोटो तपासा",
        "gps": "📍 GPS स्थान आवश्यक आहे",
        "gps_warning": "⚠️ कर्मचाऱ्याला योग्य ठिकाणी पोहोचण्यासाठी GPS आवश्यक आहे.",
        "submit_section": "🚀 तक्रार सबमिट करा",
        "submit": "🚨 तक्रार सबमिट करा",
        "navigate": "नेव्हिगेट"
    },

    "🇮🇳 ગુજરાતી (Gujarati)": {
        "report_title": "📢 નાગરિક સમસ્યાની જાણ કરો",
        "citizen_details": "📱 નાગરિક વિગતો",
        "phone": "તમારો ફોન નંબર",
        "phone_placeholder": "તમારો 10 અંકનો મોબાઇલ નંબર દાખલ કરો",
        "problem": "🚨 નાગરિક સમસ્યા શું છે?",
        "select_issue": "સમસ્યા પસંદ કરો",
        "voice": "🎤 તમારી ફરિયાદ કહો",
        "voice_info": "🎤 વોઇસ રેકોર્ડિંગ વૈકલ્પિક છે.",
        "record_voice": "🎤 ફરિયાદ રેકોર્ડ કરો",
        "convert_voice": "📝 અવાજને ટેક્સ્ટમાં બદલો",
        "details": "📝 વધારાની વિગતો",
        "description": "સમસ્યાનું વર્ણન કરો",
        "description_placeholder": "ખાલી રાખી શકો છો.",
        "upload": "📸 પુરાવો અપલોડ કરો",
        "upload_image": "સમસ્યાનો ફોટો અપલોડ કરો",
        "check_image": "🤖 ફોટો તપાસો",
        "gps": "📍 GPS સ્થાન જરૂરી છે",
        "gps_warning": "⚠️ કર્મચારીને યોગ્ય સ્થળે પહોંચવા GPS જરૂરી છે.",
        "submit_section": "🚀 ફરિયાદ સબમિટ કરો",
        "submit": "🚨 ફરિયાદ સબમિટ કરો",
        "navigate": "નેવિગેટ"
    },

    "🇮🇳 ਪੰਜਾਬੀ (Punjabi)": {
        "report_title": "📢 ਨਾਗਰਿਕ ਸਮੱਸਿਆ ਦੀ ਰਿਪੋਰਟ ਕਰੋ",
        "citizen_details": "📱 ਨਾਗਰਿਕ ਵੇਰਵੇ",
        "phone": "ਤੁਹਾਡਾ ਫੋਨ ਨੰਬਰ",
        "phone_placeholder": "ਆਪਣਾ 10 ਅੰਕਾਂ ਦਾ ਮੋਬਾਈਲ ਨੰਬਰ ਦਰਜ ਕਰੋ",
        "problem": "🚨 ਨਾਗਰਿਕ ਸਮੱਸਿਆ ਕੀ ਹੈ?",
        "select_issue": "ਸਮੱਸਿਆ ਚੁਣੋ",
        "voice": "🎤 ਆਪਣੀ ਸ਼ਿਕਾਇਤ ਬੋਲੋ",
        "voice_info": "🎤 ਵੌਇਸ ਰਿਕਾਰਡਿੰਗ ਵਿਕਲਪਿਕ ਹੈ।",
        "record_voice": "🎤 ਸ਼ਿਕਾਇਤ ਰਿਕਾਰਡ ਕਰੋ",
        "convert_voice": "📝 ਆਵਾਜ਼ ਨੂੰ ਟੈਕਸਟ ਵਿੱਚ ਬਦਲੋ",
        "details": "📝 ਵਾਧੂ ਵੇਰਵੇ",
        "description": "ਸਮੱਸਿਆ ਦਾ ਵੇਰਵਾ ਦਿਓ",
        "description_placeholder": "ਖਾਲੀ ਛੱਡ ਸਕਦੇ ਹੋ।",
        "upload": "📸 ਸਬੂਤ ਅਪਲੋਡ ਕਰੋ",
        "upload_image": "ਸਮੱਸਿਆ ਦੀ ਫੋਟੋ ਅਪਲੋਡ ਕਰੋ",
        "check_image": "🤖 ਫੋਟੋ ਚੈੱਕ ਕਰੋ",
        "gps": "📍 GPS ਸਥਾਨ ਲਾਜ਼ਮੀ ਹੈ",
        "gps_warning": "⚠️ ਕਰਮਚਾਰੀ ਨੂੰ ਸਹੀ ਸਥਾਨ ਤੱਕ ਪਹੁੰਚਣ ਲਈ GPS ਲਾਜ਼ਮੀ ਹੈ।",
        "submit_section": "🚀 ਸ਼ਿਕਾਇਤ ਜਮ੍ਹਾਂ ਕਰੋ",
        "submit": "🚨 ਸ਼ਿਕਾਇਤ ਜਮ੍ਹਾਂ ਕਰੋ",
        "navigate": "ਨੇਵੀਗੇਟ"
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

    t = TRANSLATIONS.get(
        language,
        TRANSLATIONS["🇬🇧 English"]
    )

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

    st.title(t["report_title"])

    st.markdown("""
    <div class="info-box">
    📱 Select the problem → 📸 Upload photo → 📍 Capture GPS → Submit
    </div>
    """, unsafe_allow_html=True)

    # PHONE

    st.subheader(t["citizen_details"])

    phone = st.text_input(
        t["phone"],
        placeholder=t["phone_placeholder"]
    )

    # ISSUE

    st.divider()

    st.subheader(t["problem"])

    issue_choice = st.selectbox(
        t["select_issue"],
        ISSUES
    )

    # VOICE

    st.divider()

    st.subheader(t["voice"])

    st.markdown(
        f"""
        <div class="voice-box">
        {t["voice_info"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    audio = st.audio_input(
        t["record_voice"]
    )

    if audio is not None:

        st.success("🎙️ Voice recorded successfully!")

        st.audio(audio)

        if VOICE_AVAILABLE:

            if st.button(t["convert_voice"]):

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

        else:

            st.warning(
                "⚠️ Voice recognition package is missing."
            )

    # DESCRIPTION

    st.divider()

    st.subheader(t["details"])

    description = st.text_area(
        t["description"],
        value=st.session_state.voice_text,
        placeholder=t["description_placeholder"],
        height=120
    )

    # IMAGE

    st.divider()

    st.subheader(t["upload"])

    image_file = st.file_uploader(
        t["upload_image"],
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

            if st.button(t["check_image"]):

                with st.spinner("🤖 AI is checking the image..."):

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

                    st.warning(
                        "⚠️ AI could not analyze this image."
                    )

        else:

            st.error(
                "❌ Image AI package is missing."
            )

    # GPS

    st.divider()

    st.subheader(t["gps"])

    st.warning(t["gps_warning"])

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

    # GPS RESULTS

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

    st.subheader(t["submit_section"])

    if st.button(
        t["submit"],
        type="primary",
        width="stretch"
    ):

        if not phone.strip():

            st.error("❌ Phone number is required.")
            st.stop()

        elif len(phone.strip()) < 10:

            st.error("❌ Enter a valid phone number.")
            st.stop()

        elif image_file is None:

            st.error("❌ Please upload an image.")
            st.stop()

        elif st.session_state.image_ai_issue is None:

            st.error(
                "❌ Please click 'Check Image Matches Issue' first."
            )
            st.stop()

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

        elif (
            st.session_state.latitude is None
            or st.session_state.longitude is None
        ):

            st.error("❌ GPS location is required.")
            st.stop()

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

            st.write("📢 Issue:", report["issue"])
            st.write("🏛️ Department:", report["department"])
            st.write("📝 Description:", report["description"])
            st.write("🚨 Severity:", report["severity"])
            st.write("👷 Assigned Worker:", report["worker"])

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
