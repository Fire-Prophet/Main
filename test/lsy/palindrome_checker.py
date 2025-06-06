def is_palindrome(word):
    return word == word[::-1]

word = input("단어를 입력하세요: ")
print("회문입니다." if is_palindrome(word) else "회문이 아닙니다.")
