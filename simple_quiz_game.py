# simple_quiz_game.py
import random

def run_quiz(questions_data):
    """
    퀴즈를 실행하고 점수를 반환합니다.
    questions_data는 각 항목이 {'question': '질문 내용', 'options': ['A', 'B', 'C'], 'answer': 'A'} 형태인 리스트입니다.
    """
    score = 0
    total_questions = len(questions_data)
    
    if total_questions == 0:
        print("퀴즈 문항이 없습니다.")
        return 0

    print("퀴즈를 시작합니다! 각 질문에 대해 보기 중 하나를 선택하세요.")
    random.shuffle(questions_data) # 문제 순서 섞기

    for i, q_data in enumerate(questions_data):
        print(f"\n질문 {i + 1}/{total_questions}: {q_data['question']}")
        options = q_data['options']
        # 보기 순서도 섞을 수 있지만, 여기서는 고정된 순서로 표시
        # random.shuffle(options) # 필요하다면 보기 순서도 섞기
        for idx, option in enumerate(options):
            print(f"  {chr(ord('A') + idx)}. {option}")
        
        while True:
            user_answer_char = input("답변을 선택하세요 (A, B, C 등): ").upper()
            if user_answer_char and 'A' <= user_answer_char < chr(ord('A') + len(options)):
                break
            else:
                print(f"잘못된 입력입니다. A부터 {chr(ord('A') + len(options) -1)} 사이의 문자를 입력하세요.")
        
        correct_answer_char = q_data['answer'].upper() # 정답은 대문자로 통일
        
        if user_answer_char == correct_answer_char:
            print("정답입니다!")
            score += 1
        else:
            # 정답에 해당하는 보기 내용 출력
            correct_option_index = ord(correct_answer_char) - ord('A')
            correct_option_text = options[correct_option_index]
            print(f"오답입니다. 정답은 {correct_answer_char} ({correct_option_text}) 입니다.")
            
    print(f"\n퀴즈 종료! 총 {total_questions}문제 중 {score}문제를 맞추셨습니다.")
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    print(f"정답률: {percentage:.2f}%")
    return score

def main():
    """퀴즈 게임 메인 함수"""
    # 퀴즈 데이터 (질문, 보기, 정답)
    # 정답은 보기의 알파벳 (A, B, C, ...)
    quiz_questions = [
        {
            "question": "파이썬에서 리스트의 모든 항목을 제거하는 메서드는 무엇인가요?",
            "options": ["delete()", "remove_all()", "clear()", "empty()"],
            "answer": "C"
        },
        {
            "question": "HTML은 무엇의 약자인가요?",
            "options": ["Hyperlinks and Text Markup Language", "Hyper Text Markup Language", "Home Tool Markup Language", "Hyperlinking Text Marking Language"],
            "answer": "B"
        },
        {
            "question": "파이썬의 창시자는 누구인가요?",
            "options": ["제임스 고슬링", "귀도 반 로썸", "데니스 리치", "리누스 토르발스"],
            "answer": "B"
        },
        {
            "question": "지구에서 가장 높은 산은 무엇인가요?",
            "options": ["K2", "칸첸중가", "에베레스트 산", "로체 산"],
            "answer": "C"
        },
        {
            "question": "1 킬로바이트(KB)는 몇 바이트(Byte)인가요?",
            "options": ["1000 바이트", "1024 바이트", "2048 바이트", "512 바이트"],
            "answer": "B" # 일반적으로 컴퓨터 과학에서는 2^10
        }
    ]
    
    run_quiz(quiz_questions)
    
    while True:
        play_again = input("\n다시 플레이하시겠습니까? (yes/no): ").lower()
        if play_again == 'yes':
            run_quiz(quiz_questions)
        elif play_again == 'no':
            print("게임을 종료합니다. 즐거웠습니다!")
            break
        else:
            print("yes 또는 no로 입력해주세요.")


if __name__ == "__main__":
    main()
