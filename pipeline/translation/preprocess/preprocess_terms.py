import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import pandas as pd
import ahocorasick
from pipeline.translation.utils.path_utils import get_glossary_csv_path

def load_ko_glossary(glossary_csv_path):
    try:
        df = pd.read_csv(glossary_csv_path)
        ko_glossary = {row['key']: row['ko'] for _, row in df.iterrows() if pd.notnull(row['ko']) and row['ko']}
        print(f"[INFO] Loaded glossary_table.csv ({len(ko_glossary)} ko terms)")
        return ko_glossary
    except Exception as e:
        print(f"[ERROR] Failed to load glossary_table.csv: {e}")
        return {}

def build_automaton(ko_glossary):
    A = ahocorasick.Automaton()
    for key, value in ko_glossary.items():
        if value:
            A.add_word(value, (key, value))
    A.make_automaton()
    return A

def replace_terms(text, automaton):
    result = []
    last_idx = 0
    for end_idx, (key, value) in automaton.iter(text):
        start_idx = end_idx - len(value) + 1
        result.append(text[last_idx:start_idx])
        result.append(f"__TERM_{key}__")
        last_idx = end_idx + 1
    result.append(text[last_idx:])
    return ''.join(result)

def main():
    glossary_csv_path = get_glossary_csv_path()
    ko_glossary = load_ko_glossary(glossary_csv_path)
    if not ko_glossary:
        print("[ERROR] No ko glossary loaded. Exiting.")
        return
    automaton = build_automaton(ko_glossary)

    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
    else:
        print("문장을 입력하세요 (Ctrl+D로 종료):")
        input_text = sys.stdin.read().strip()

    if not input_text:
        print("[ERROR] 입력 문장이 없습니다.")
        return

    replaced = replace_terms(input_text, automaton)
    print(f"[RESULT] {replaced}")

if __name__ == "__main__":
    main() 