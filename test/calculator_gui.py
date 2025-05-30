import tkinter as tk

def on_click(key):
    """버튼 클릭 시 호출되는 함수"""
    current_text = entry.get()
    
    if key == 'C':
        # 'C' 버튼: 입력 필드 초기화
        entry.delete(0, tk.END)
    elif key == '=':
        # '=' 버튼: 입력된 수식 계산
        try:
            # eval()을 사용하여 수식 계산 (보안상 주의 필요)
            result = eval(current_text)
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
        except Exception:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Error")
    else:
        # 숫자 또는 연산자 버튼: 입력 필드에 추가
        entry.insert(tk.END, key)

# 메인 윈도우 생성
window = tk.Tk()
window.title("간단 계산기")

# 입력 필드 (Entry 위젯)
entry = tk.Entry(window, width=35, borderwidth=5, justify='right', font=('Arial', 14))
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

# 버튼 레이아웃 정의
buttons = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', 'C', '=', '+'
]

# 버튼 생성 및 배치
row_val = 1
col_val = 0
for button_text in buttons:
    # 각 버튼에 on_click 함수 연결 (lambda 사용)
    action = lambda x=button_text: on_click(x)
    tk.Button(window, text=button_text, padx=40, pady=20, font=('Arial', 12), command=action).grid(row=row_val, column=col_val, sticky='nsew')
    col_val += 1
    if col_val > 3:
        col_val = 0
        row_val += 1

# 창 크기 조절 설정
for i in range(5): window.grid_rowconfigure(i, weight=1)
for i in range(4): window.grid_columnconfigure(i, weight=1)

# 이벤트 루프 시작
window.mainloop()
