import tkinter as tk

def say_hello():
    label.config(text="안녕하세요!")

root = tk.Tk()
root.title("인사 프로그램")

label = tk.Label(root, text="버튼을 눌러보세요")
label.pack()

btn = tk.Button(root, text="인사", command=say_hello)
btn.pack()

root.mainloop()
