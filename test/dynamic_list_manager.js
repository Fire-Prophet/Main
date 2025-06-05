document.addEventListener('DOMContentLoaded', () => {
    // DOM이 완전히 로드된 후에 스크립트를 실행합니다.
    const addButton = document.getElementById('add-item-button');
    const itemList = document.getElementById('item-list');
    const newItemInput = document.getElementById('new-item-input');

    if (addButton && itemList && newItemInput) {
        let itemCount = 0; // 항목 수를 추적하여 고유한 레이블을 제공합니다.
        console.log('DOM 요소들이 성공적으로 로드되었습니다. 이벤트 리스너를 설정합니다.');

        // "추가" 버튼 클릭 이벤트 리스너
        addButton.addEventListener('click', () => {
            const newItemText = newItemInput.value.trim(); // 입력 필드의 공백 제거
            if (newItemText) {
                // 새로운 리스트 아이템(<li>) 요소 생성
                const listItem = document.createElement('li');
                listItem.textContent = `${newItemText} (항목 #${++itemCount})`;
                listItem.className = 'list-item'; // CSS 스타일링을 위한 클래스 추가

                // 삭제 버튼 생성 및 이벤트 리스너 추가
                const removeButton = document.createElement('button');
                removeButton.textContent = '삭제';
                removeButton.className = 'remove-button'; // CSS 스타일링을 위한 클래스 추가
                removeButton.addEventListener('click', () => {
                    itemList.removeChild(listItem); // 해당 리스트 아이템 제거
                    console.log(`항목 "${newItemText}" 삭제됨.`);
                    // 선택적으로 itemCount를 감소시키거나 다시 정렬할 수 있습니다.
                });

                listItem.appendChild(removeButton); // 리스트 아이템에 삭제 버튼 추가
                itemList.appendChild(listItem);     // 목록에 리스트 아이템 추가
                newItemInput.value = '';            // 입력 필드 초기화
                newItemInput.focus();               // 다음 입력을 위해 포커스 설정
                console.log(`새 항목 "${newItemText}" 추가됨. 현재 항목 수: ${itemCount}`);
            } else {
                alert('추가할 항목 내용을 입력해주세요!'); // 내용이 없을 경우 사용자에게 알림
                newItemInput.focus();
            }
        });

        // 엔터 키 입력 시 항목 추가 기능 (선택 사항)
        newItemInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                addButton.click(); // 버튼 클릭 이벤트 트리거
            }
        });

    } else {
        console.error('필요한 DOM 요소들을 찾을 수 없습니다 (add-item-button, item-list, new-item-input). HTML 구조를 확인하세요.');
    }
});
