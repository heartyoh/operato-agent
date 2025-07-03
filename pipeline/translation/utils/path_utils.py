from pathlib import Path

def get_project_root():
    # 이 파일이 pipeline/translation/utils/path_utils.py에 위치한다고 가정
    return Path(__file__).resolve().parents[3]

def get_glossary_csv_path():
    return get_project_root() / 'pipeline' / 'translation' / 'glossary' / 'glossary_table.csv' 