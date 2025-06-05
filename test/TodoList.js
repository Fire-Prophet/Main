import React, { useState } from 'react';

// ToDoItem 컴포넌트: 각 할 일 항목을 표시합니다.
const ToDoItem = ({ todo, onToggle, onRemove }) => {
    return (
        <li style={{ 
            textDecoration: todo.completed ? 'line-through' : 'none',
            margin: '8px 0',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: todo.completed ? '#e0ffe0' : '#fff'
        }}>
            <span onClick={() => onToggle(todo.id)} style={{ cursor: 'pointer', flexGrow: 1 }}>
                {todo.text}
            </span>
            <button 
                onClick={() => onRemove(todo.id)}
                style={{
                    marginLeft: '10px',
                    padding: '5px 10px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }}
            >
                삭제
            </button>
        </li>
    );
};

// TodoList 컴포넌트: 전체 할 일 목록을 관리합니다.
const TodoList = () => {
    const [todos, setTodos] = useState([]); // 할 일 목록 상태
    const [newTodoText, setNewTodoText] = useState(''); // 새 할 일 입력 텍스트 상태

    // 새 할 일 추가 함수
    const handleAddTodo = () => {
        if (newTodoText.trim() === '') {
            alert('할 일 내용을 입력해주세요!');
            return;
        }
        const newTodo = {
            id: Date.now(), // 고유 ID 생성 (간단한 예시용)
            text: newTodoText,
            completed: false,
        };
        setTodos([...todos, newTodo]); // 기존 목록에 새 할 일 추가
        setNewTodoText(''); // 입력 필드 초기화
        console.log(`할 일 추가됨: "${newTodo.text}"`);
    };

    // 할 일 완료/미완료 토글 함수
    const handleToggleComplete = (id) => {
        setTodos(todos.map(todo => 
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        ));
        console.log(`할 일 ID ${id} 상태 변경됨.`);
    };

    // 할 일 제거 함수
    const handleRemoveTodo = (id) => {
        setTodos(todos.filter(todo => todo.id !== id));
        console.log(`할 일 ID ${id} 제거됨.`);
    };

    return (
        <div style={{ maxWidth: '500px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h2>나의 할 일 목록</h2>
            <div style={{ display: 'flex', marginBottom: '20px' }}>
                <input
                    type="text"
                    value={newTodoText}
                    onChange={(e) => setNewTodoText(e.target.value)}
                    placeholder="새 할 일을 입력하세요..."
                    style={{ flexGrow: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
                    onKeyPress={(e) => { // 엔터 키로도 추가 가능하게
                        if (e.key === 'Enter') {
                            handleAddTodo();
                        }
                    }}
                />
                <button 
                    onClick={handleAddTodo}
                    style={{
                        marginLeft: '10px',
                        padding: '10px 15px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    추가
                </button>
            </div>
            <ul>
                {todos.length === 0 ? (
                    <p style={{ textAlign: 'center', color: '#666' }}>아직 할 일이 없습니다. 추가해보세요!</p>
                ) : (
                    todos.map(todo => (
                        <ToDoItem 
                            key={todo.id} 
                            todo={todo} 
                            onToggle={handleToggleComplete} 
                            onRemove={handleRemoveTodo} 
                        />
                    ))
                )}
            </ul>
        </div>
    );
};

export default TodoList;
