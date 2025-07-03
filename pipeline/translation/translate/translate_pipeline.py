import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from pipeline.translation.preprocess.preprocess_terms import load_ko_glossary, build_automaton, replace_terms
from pipeline.translation.postprocess.postprocess_terms import load_en_glossary, restore_terms
from pipeline.translation.utils.path_utils import get_glossary_csv_path

# 모의 번역 함수 (실제 번역 API 연동 전용)
def mock_translate(text):
    # 실제로는 NMT/LLM 번역 API 연동 필요
    # 여기서는 예시로 한글을 그대로 영어로 복사(실전에서는 번역 결과가 들어감)
    print(f"[MOCK TRANSLATE] (실제 번역 API 연동 필요)")
    return text.replace('목록을 보여줘', 'Show me the list of')


def main():
    glossary_csv_path = get_glossary_csv_path()
    ko_glossary = load_ko_glossary(glossary_csv_path)
    en_glossary = load_en_glossary(glossary_csv_path)
    if not ko_glossary or not en_glossary:
        print("[ERROR] Glossary 로딩 실패. 종료합니다.")
        return
    automaton = build_automaton(ko_glossary)

    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
    else:
        print("한글 입력 문장을 입력하세요 (Ctrl+D로 종료):")
        input_text = sys.stdin.read().strip()

    if not input_text:
        print("[ERROR] 입력 문장이 없습니다.")
        return

    # 1. 전처리: 특수토큰 치환
    preprocessed = replace_terms(input_text, automaton)
    print(f"[PREPROCESS] {preprocessed}")

    # 2. (모의)번역
    translated = mock_translate(preprocessed)
    print(f"[TRANSLATE] {translated}")

    # 3. 후처리: 특수토큰 복원
    postprocessed = restore_terms(translated, en_glossary)
    print(f"[POSTPROCESS] {postprocessed}")

if __name__ == "__main__":
    main() 