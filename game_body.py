print('#### 띄어쓰기 사용 금지 ###')
pro = input('닉네임을 입력해주세요! >>> ')
global money
money = 50000
while True:
    print('='*40)
    game = input('메뉴를 선택하세요.(1.프로필 확인/ 2.게임_1 / 3.게임_2 / 4.저장 / 5.종료) >>>')
    if game not in ['1','2','3','4','5']:
        print('숫자 하나만 입력해 주세요!! :)')
    if game == '1':
        print(pro)
        print('돈:',money)
    if game == '2':
        print('='*40)
        game_1 = input('1.싱글 게임 // 2.멀티 게임 // 3.취소 >>>')
        if game_1 not in ['1','2','3']:
            print('숫자 하나만 입력해 주세요!! :)')
        if game_1 == '1':
            print('='*40)
            game_list1 = input('1.Up-down // 2.가위-바위-보 // 3.주사위 게임 룰 // 4. 취소 >>>')
            if game_list1 not in ['1','2','3','4']:
                print('숫자 하나만 입력해 주세요!! :)')
            if game_list1 == '1':
                sg_game_1()                    ##up-down 게임 함수
            if game_list1 == '2': 
                sg_game_2()                    ##가위 바위 보 게임 함수
            if game_list1 == '3':
                sg_game_3()                    ##주사위 게임 함수
            if game_list1 == '4':
                continue
        if game_1 == '2':
            print('='*40)
            game_list2 = input('1. 랜덤 숫자 게임 // 2. 추가 예정 // 3. 취소 >>>')
            if game_list2 not in ['1','2','3']:
                print('숫자 하나만 입력해 주세요!! :)')
            if game_list2 == '1':
                mt_game_1()                     #랜덤 숫자 게임 함수
            if game_list2 == '2':
                print('추가예정')
            if game_list2 == '3':
                continue
    if game == '3':
        print('='*40)
        kim_game_1 = input('도박을 선택하세요!! (1. 도박, // 2. 숫자 맞추기, // 3, 취소) >>> ')
        if kim_game_1 == '1':
            kim_game()                          ##도박 함수
        if kim_game_1 == '2':
            kim_game_2()                       #숫자 맞추기 함수
        if kim_game_1 == '3':
            continue
        if kim_game_1 not in ['1','2','3']:
            print('숫자 하나만 입력해 주세요!! :)')
    if game == '4':
        print('저장합니다.')
        with open("save.txt", "w", encoding="UTF-8") as save_file:       #encoding = 'UTF-8'은 없어도 되지만, 한글인 경우에 오류가 날수 있다. 'W'는 쓰기 전용
            save_file.write(pro)
            save_file.write(str(money))       #int형은 오류가 나기 때문에, str 문자열로 변환
    if game == '5':
        print('종료합니다 :)')
        break
