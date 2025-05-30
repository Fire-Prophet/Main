def sg_game_2():
    import random as rd
    global money
    print('주의사항'.center(40, '='))
    print('본 게임은 정상적인 작동이 안될 수 있습니다.')
    print('가끔 오락가락? 합니다.')
    print('='*40)
    
    while True:
        game_2 = input("다음에서 선택하세요{0: '종료' // 1: '가위' // 2: '바위' // 3: '보'} >>>")
        if game_2 == '1':
            if rd.choice(['가위','바위','보']) == '가위':
                print('===> [사람]: 가위, [컴퓨터]: 가위, [결과]: 무승부')
                print(money)
            if rd.choice(['가위','바위','보']) == '바위':
                print('===> [사람]: 가위, [컴퓨터]: 주먹, [결과]: 패배')
                print('money - 500원')
                money -= 500
                print(money)
            if rd.choice(['가위','바위','보']) == '보':
                print('===> [사람]: 가위, [컴퓨터]: 보, [결과]: 승리')
                print('money + 500원')
                money += 500
                print(money)
        if game_2 == '2':
            if rd.choice(['가위','바위','보']) == '가위':
                print('===> [사람]: 바위, [컴퓨터]: 가위, [결과]: 승리')
                print('money + 500원')
                money += 500
                print(money)
            if rd.choice(['가위','바위','보']) == '바위':
                print('===> [사람]: 바위, [컴퓨터]: 주먹, [결과]: 무승부')
                print(money)
            if rd.choice(['가위','바위','보']) == '보':
                print('===> [사람]: 바위, [컴퓨터]: 보, [결과]: 패배')
                print('money - 500원')
                money -= 500
                print(money)
        if game_2 == '3':
            if  rd.choice(['가위','바위','보']) == '가위':
                print('===> [사람]: 보, [컴퓨터]: 가위, [결과]: 패배')
                print('money - 500원')
                money -= 500
                print(money)
            if  rd.choice(['가위','바위','보']) == '바위':
                print('===> [사람]: 보, [컴퓨터]: 주먹, [결과]: 승리')
                print('money + 500원')
                money += 500
                print(money)
            if  rd.choice(['가위','바위','보']) == '보':
                print('===> [사람]: 보, [컴퓨터]: 보, [결과]: 무승부')
                print(money)
        if game_2 == '0':
            print(' 게임종료 '.center(50,'='))
            break
