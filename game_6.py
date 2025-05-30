#숫자 맞추기
def kim_game_2():
    import random as rd
    global money


    print('숫자 맞추기 룰'.center(40, '='))
    print('1, 자신이 고른 숫자를 맞추면 성공 (1 ~ 20) ')
    print('2. 성공시 5만원')
    print('='*40)

    while True:
        start_5 = input('숫자를 선택해주세요 (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20): ')    
        money -= 1000
        cc = rd.randint(1,20)
        print(cc)
        

        if cc == int(start_5):
            print('성공')
            money += 50000
            print(money)
            break
        else:
            print('틀렸습니다 ^^7')
            print(money)

