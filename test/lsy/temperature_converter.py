def c_to_f(c):
    return (c * 9/5) + 32

def f_to_c(f):
    return (f - 32) * 5/9

choice = input("변환할 방향을 선택하세요 (C->F / F->C): ").upper()
temp = float(input("온도 입력: "))

if choice == "C->F":
    print(f"화씨: {c_to_f(temp):.2f}°F")
elif choice == "F->C":
    print(f"섭씨: {f_to_c(temp):.2f}°C")
else:
    print("잘못된 입력입니다.")
