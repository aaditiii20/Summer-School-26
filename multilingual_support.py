"""
Multilingual Support for AYUSH FHIR Terminology Portal
Enhanced version with better language detection and normalization
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Define all 22 official Indian language codes
LANGUAGE_CODES = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati", 
    "ta": "Tamil",
    "ur": "Urdu",
    "bn": "Bengali",
    "ml": "Malayalam",
    "kn": "Kannada",
    "mr": "Marathi",
    "pa": "Punjabi",
    "or": "Odia",
    "te": "Telugu",
    "as": "Assamese",
    "sd": "Sindhi",
    "ne": "Nepali",
    "si": "Sinhala",
    "ks": "Kashmiri",
    "mai": "Maithili",
    "kok": "Konkani",
    "sa": "Sanskrit",
    "brx": "Bodo",
    "doi": "Dogri"
}

# Common symptom translations for quick matching
SYMPTOM_TRANSLATIONS = {
    # Headache
    "सिरदर्द": "headache",
    "सिर": "head",
    "शिरः": "head",
    "தலைவலி": "headache",
    "తలనొప్పి": "headache",
    "ಶಿರಃಶೂಲೆ": "headache",
    "মাথাব্যথা": "headache",
    "માથાનો દુખાવો": "headache",
    "डोकेदुखी": "headache",
    "തലവേദന": "headache",
    "ਸਿਰ ਦਰਦ": "headache",
    "سر درد": "headache",
    
    # Fever
    "बुखार": "fever",
    "ज्वर": "fever",
    "காய்ச்சல்": "fever",
    "జ్వరము": "fever",
    "ಜ್ವರ": "fever",
    "জ্বর": "fever",
    "તાવ": "fever",
    "ताप": "fever",
    "പനി": "fever",
    "ਬੁਖਾਰ": "fever",
    "بخار": "fever",
    
    # Pain
    "दर्द": "pain",
    "पीड़ा": "pain",
    "शूल": "pain",
    "வலி": "pain",
    "నొప్పి": "pain",
    "ನೋವು": "pain",
    "ব্যথা": "pain",
    "દુખાવો": "pain",
    "वेदना": "pain",
    "വേദന": "pain",
    "ਦਰਦ": "pain",
    "درد": "pain",
    
    # Cough
    "खांसी": "cough",
    "कास": "cough",
    "இருமல்": "cough",
    "దగ్గు": "cough",
    "ಕೆಮ್ಮು": "cough",
    "কাশি": "cough",
    "ઉધરસ": "cough",
    "खोकला": "cough",
    "ചുമ": "cough",
    "ਖੰਘ": "cough",
    "کھانسی": "cough",
    
    # Vomiting/Nausea
    "उल्टी": "vomiting",
    "वमन": "vomiting",
    "குமட்டல்": "nausea",
    "వాంతులు": "vomiting",
    "ವಾಂತಿ": "vomiting",
    "বমি": "vomiting",
    "ઉલટી": "vomiting",
    "उलटी": "vomiting",
    "ഓക്കാനം": "nausea",
    "ਉਲਟੀ": "vomiting",
    "الٹی": "vomiting"
}

def normalize_disease(disease_name: str, language: str, codesystem: Optional[Dict[str, Any]] = None) -> str:
    """
    Normalize a disease name from any supported language to English.
    
    Args:
        disease_name: The disease name to normalize
        language: Language code of the input (e.g., 'hi', 'gu')
        codesystem: Loaded NAMASTE FHIR codesystem JSON (optional)
    
    Returns:
        str: Normalized English disease name
    """
    language = language.lower()
    disease_lower = disease_name.strip().lower()
    
    logger.info(f"Normalizing disease: '{disease_name}' from language: '{language}'")
    
    # If already English, return as-is
    if language == "en":
        return disease_name
    
    # Check if language is supported
    if language not in LANGUAGE_CODES:
        logger.warning(f"Unsupported language: {language}")
        return disease_name
    
    # First, try quick translation from symptom dictionary
    if disease_lower in SYMPTOM_TRANSLATIONS:
        translated = SYMPTOM_TRANSLATIONS[disease_lower]
        logger.info(f"Found quick translation: '{disease_name}' -> '{translated}'")
        return translated
    
    # If codesystem provided, search in it
    if codesystem:
        try:
            for concept in codesystem.get("concept", []):
                # Get display name (English)
                english_display = concept.get("display", "")
                
                # Check properties for traditional names
                properties = concept.get("property", [])
                for prop in properties:
                    prop_code = prop.get("code", "")
                    prop_value = prop.get("valueString", "").lower()
                    
                    # Match against the input language
                    if f"traditional_name_{language}" in prop_code or f"name_{language}" in prop_code:
                        if prop_value == disease_lower or disease_lower in prop_value:
                            logger.info(f"Found in codesystem: '{disease_name}' -> '{english_display}'")
                            return english_display
                    
                    # Also check all traditional names for partial match
                    if "traditional_name" in prop_code and disease_lower in prop_value:
                        logger.info(f"Found partial match in codesystem: '{disease_name}' -> '{english_display}'")
                        return english_display
        except Exception as e:
            logger.error(f"Error searching codesystem: {e}")
    
    # If no match found, return original
    logger.warning(f"No translation found for '{disease_name}' in language '{language}'")
    return disease_name


def translate_symptoms_to_english(text: str, language: str) -> str:
    """
    Translate a full symptom description from any language to English.
    
    Args:
        text: Full symptom description
        language: Source language code
    
    Returns:
        str: Text with key medical terms translated to English
    """
    if language == "en":
        return text
    
    result = text
    words = text.split()
    
    # Translate each word if found in dictionary
    translated_words = []
    for word in words:
        word_lower = word.lower().strip('.,!?;:')
        if word_lower in SYMPTOM_TRANSLATIONS:
            translated_words.append(SYMPTOM_TRANSLATIONS[word_lower])
        else:
            translated_words.append(word)
    
    return ' '.join(translated_words)


def get_supported_languages() -> Dict[str, str]:
    """Get list of all supported languages."""
    return LANGUAGE_CODES.copy()


def detect_language(text: str) -> str:
    """
    Attempt to detect the language of input text.
    
    Args:
        text: Input text
    
    Returns:
        str: Detected language code (defaults to 'en')
    """
    text_lower = text.lower()
    
    # Check for common words in each language
    for word, english in SYMPTOM_TRANSLATIONS.items():
        if word in text_lower:
            # Determine language from Unicode range (basic heuristic)
            if any('\u0900' <= c <= '\u097F' for c in word):  # Devanagari
                return 'hi'
            elif any('\u0B80' <= c <= '\u0BFF' for c in word):  # Tamil
                return 'ta'
            elif any('\u0C00' <= c <= '\u0C7F' for c in word):  # Telugu
                return 'te'
            elif any('\u0C80' <= c <= '\u0CFF' for c in word):  # Kannada
                return 'kn'
            elif any('\u0980' <= c <= '\u09FF' for c in word):  # Bengali
                return 'bn'
            elif any('\u0A80' <= c <= '\u0AFF' for c in word):  # Gujarati
                return 'gu'
            elif any('\u0D00' <= c <= '\u0D7F' for c in word):  # Malayalam
                return 'ml'
            elif any('\u0600' <= c <= '\u06FF' for c in word):  # Arabic/Urdu
                return 'ur'
            elif any('\u0A00' <= c <= '\u0A7F' for c in word):  # Punjabi
                return 'pa'
    
    return 'en'  # Default to English