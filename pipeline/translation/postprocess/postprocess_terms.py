import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import pandas as pd
import re
from pipeline.translation.utils.path_utils import get_glossary_csv_path

def load_en_glossary(glossary_csv_path):
    try:
        df = pd.read_csv(glossary_csv_path)
        en_glossary = {row['key']: row['en'] for _, row in df.iterrows() if pd.notnull(row['en']) and row['en']}
        print(f"[INFO] Loaded glossary_table.csv ({len(en_glossary)} en terms)")
        return en_glossary
    except Exception as e:
        print(f"[ERROR] Failed to load glossary_table.csv: {e}")
        return {}

def restore_terms(text, en_glossary):
    def replacer(match):
        key = match.group(1)
        return en_glossary.get(key, f"__TERM_{key}__")
    return re.sub(r"__TERM_([a-zA-Z0-9_.]+)__", replacer, text)

def main():
    glossary_csv_path = get_glossary_csv_path()
    en_glossary = load_en_glossary(glossary_csv_path)
    if not en_glossary:
        print("[ERROR] No en glossary loaded. Exiting.")
        return

    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
    else:
        print("번역 결과 문장을 입력하세요 (Ctrl+D로 종료):")
        input_text = sys.stdin.read().strip()

    if not input_text:
        print("[ERROR] 입력 문장이 없습니다.")
        return

    restored = restore_terms(input_text, en_glossary)
    print(f"[RESULT] {restored}")

if __name__ == "__main__":
    main() 