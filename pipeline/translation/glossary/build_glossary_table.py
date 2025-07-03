import os
import json
import pandas as pd

from pathlib import Path

def main():
    # 현재 스크립트 위치 기준으로 terminology 폴더 경로 계산
    base_dir = Path(__file__).resolve().parent  # build_glossary_table.py가 있는 폴더
    terminology_dir = base_dir.parent.parent.parent / 'data' / 'terminology'
    output_path = base_dir / 'glossary_table.csv'

    langs = []
    data = {}

    # 언어별 json 파일 자동 탐색
    for file in terminology_dir.glob('*.json'):
        lang = file.stem
        langs.append(lang)
        try:
            with open(file, encoding='utf-8') as f:
                data[lang] = json.load(f)
            print(f"[INFO] Loaded {file.name} ({len(data[lang])} terms)")
        except Exception as e:
            print(f"[ERROR] Failed to load {file.name}: {e}")
            data[lang] = {}

    if not langs:
        print("[ERROR] No terminology JSON files found.")
        return

    # 모든 key의 합집합
    all_keys = set()
    for d in data.values():
        all_keys.update(d.keys())

    if not all_keys:
        print("[ERROR] No terms found in terminology files.")
        return

    # Glossary 테이블 생성
    rows = []
    for key in sorted(all_keys):
        row = {'key': key}
        for lang in langs:
            row[lang] = data[lang].get(key, "")
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"[SUCCESS] Glossary table saved to {output_path} ({len(df)} rows, {len(langs)} languages)")

if __name__ == "__main__":
    main() 