def sg_game_1():
    import random as rd
    com = rd.randint(1,100)
    print('게임 Up-down 룰'.center(30, '='))
    print('1, 기회는 5번 입니다.')
    print('2, 랜덤하게 정해진 숫자를 Up-down을 통해 맞추세요!')
    print('='*40)

    life = 5
    global money                    # money라는 변수를 전역변수로 지정한다.
    while True:
        go = input('숫자(1~100) >>>')
        if int(go) == com:
            print('*'*30)
            print('정답입니다!!')
            print('목숨:',life)
            if life < 0:
                print('다시 도전해보세요!!! :>')
                money -= 2000
                print(money)
                break
            if life >= 0:
                print('와우 똑똑하신걸요!! :)')
                money += 2000
                print('돈:',money)
                break
        if int(go) != com:
            if int(go) <= com:
                print('up')
                life -= 1
            if int(go) >= com:
                print('down')
                life -= 1
