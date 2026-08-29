"""
Multilingual Router for AYUSH FHIR Terminology Portal
Handles language detection and translation of medical terms
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from multilingual_support import (
    normalize_disease, 
    translate_symptoms_to_english,
    get_supported_languages,
    detect_language,
    SYMPTOM_TRANSLATIONS
)
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/multilingual",
    tags=["Multilingual Support"]
)

# Load the FHIR codesystem JSON
codesystem_file = Path("data/processed/namaste_codesystem_v2.json")
codesystem = None

try:
    if codesystem_file.exists():
        with open(codesystem_file, 'r', encoding='utf-8') as f:
            codesystem = json.load(f)
        logger.info(f" Loaded codesystem with {len(codesystem.get('concept', []))} concepts")
    else:
        logger.warning(f" Codesystem file not found: {codesystem_file}")
except Exception as e:
    logger.error(f" Error loading codesystem: {e}")


@router.get("/normalize")
async def normalize_endpoint(
    disease: str = Query(..., description="Disease/symptom name to normalize"),
    language: str = Query("en", description="Input language code (e.g., 'hi', 'ta', 'gu')")
):
    """
    Normalize a disease/symptom name from any supported language to English.
    
    Example:
        GET /api/multilingual/normalize?disease=सिरदर्द&language=hi
        Returns: {"normalized": "headache", "language": "hi", "input": "सिरदर्द"}
    """
    try:
        language = language.lower()
        english_disease = normalize_disease(disease, language, codesystem)
        
        return {
            "success": True,
            "input": disease,
            "language": language,
            "normalized": english_disease,
            "detected_language": detect_language(disease) if language == "auto" else language
        }
    except Exception as e:
        logger.error(f"Error normalizing disease: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translate_symptoms")
async def translate_symptoms_endpoint(
    text: str = Query(..., description="Full symptom description to translate"),
    language: str = Query("auto", description="Source language code or 'auto' for detection")
):
    """
    Translate a full symptom description to English.
    
    Example:
        GET /api/multilingual/translate_symptoms?text=मुझे सिरदर्द और बुखार है&language=hi
        Returns: {"translated": "I have headache and fever", ...}
    """
    try:
        # Detect language if auto
        if language == "auto":
            language = detect_language(text)
        
        language = language.lower()
        translated = translate_symptoms_to_english(text, language)
        
        return {
            "success": True,
            "original": text,
            "translated": translated,
            "detected_language": language
        }
    except Exception as e:
        logger.error(f"Error translating symptoms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_languages():
    """
    Get list of all supported languages.
    
    Returns:
        List of language codes and names
    """
    return {
        "success": True,
        "languages": get_supported_languages(),
        "total": len(get_supported_languages())
    }


@router.get("/detect_language")
async def detect_language_endpoint(
    text: str = Query(..., description="Text to detect language from")
):
    """
    Detect the language of input text.
    
    Example:
        GET /api/multilingual/detect_language?text=मुझे सिरदर्द है
        Returns: {"language": "hi", "name": "Hindi"}
    """
    try:
        detected = detect_language(text)
        languages = get_supported_languages()
        
        return {
            "success": True,
            "text": text,
            "language": detected,
            "language_name": languages.get(detected, "Unknown")
        }
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symptom_dictionary")
async def get_symptom_dictionary():
    """
    Get the complete symptom translation dictionary.
    Useful for frontend caching.
    """
    return {
        "success": True,
        "dictionary": SYMPTOM_TRANSLATIONS,
        "total_translations": len(SYMPTOM_TRANSLATIONS)
    }