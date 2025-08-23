import os
import polib
from deep_translator import GoogleTranslator

INDIAN_LANGUAGES = [
    "as", "bn", "gu", "hi", "kn", "kok", "ml", "mr", "ne", "or",
    "pa", "sa", "ta", "te", "ur"
]
LANG_CODE_MAP = {
    "kok": "mr",
    "sa": "hi",
}
BASE_LOCALE_PATH = os.path.join(os.getcwd(), "locale")
DOMAIN = "django"

def ensure_po_exists(lang_code):
    """Create .po file if missing"""
    po_path = os.path.join(BASE_LOCALE_PATH, lang_code, "LC_MESSAGES", f"{DOMAIN}.po")
    if not os.path.exists(po_path):
        print(f"📁 Creating .po file for {lang_code}")
        os.system(f"django-admin makemessages -l {lang_code}")
    return po_path

def translate_po_file(po_path, lang_code):
    """Translate all empty msgstr entries using deep-translator."""
    actual_lang = LANG_CODE_MAP.get(lang_code, lang_code)

    po = polib.pofile(po_path)
    entries = [entry for entry in po if not entry.translated() and entry.msgid.strip()]
    print(f"🔄 Translating {len(entries)} entries into '{lang_code}'...")

    for entry in entries:
        try:
            translated = GoogleTranslator(source="en", target=actual_lang).translate(entry.msgid)
            entry.msgstr = translated
        except Exception as e:
            print(f"❌ Error translating '{entry.msgid}': {e}")
            continue

    po.save()
    print(f"✅ Translated and saved: {po_path}")

def compile_messages():
    print("🔨 Compiling .mo files...")
    os.system("django-admin compilemessages")
    print("✅ Done.")

if __name__ == "__main__":
    for lang in INDIAN_LANGUAGES:
        try:
            po_file = ensure_po_exists(lang)
            translate_po_file(po_file, lang)
        except Exception as ex:
            print(f"⚠️ Skipped {lang}: {ex}")

    compile_messages()
