from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 데이터는 간단히 리스트로 메모리에 저장합니다.
todos = []

@app.route('/')
def index():
    # templates/index.html 파일을 렌더링합니다.
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    todo_task = request.form.get('todo')
    if todo_task:
        todos.append({'task': todo_task, 'done': False})
    return redirect(url_for('index'))

@app.route('/toggle/<int:index>')
def toggle_todo(index):
    if 0 <= index < len(todos):
        todos[index]['done'] = not todos[index]['done']
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_todo(index):
    if 0 <= index < len(todos):
        del todos[index]
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 디버그 모드로 실행합니다.
    app.run(debug=True)
