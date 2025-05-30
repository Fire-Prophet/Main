def sg_game_3():
    global money
    import random as rd
    print('주사위 게임 룰 '.center(30, '='))
    print('랜덤으로 주사위 2개를 던진후, 그 값이 컴퓨터보다 크면 배팅 금액을 획득 \n 컴퓨터 보다 작으면 배팅 금액 감소')
    print('주의사항'.center(30, '*'))
    print('절대로 숫자만 입력하세요!!')
    print('='*40)
    while True:
        start_rd = input('게임을 시작하시겠습니까? (1. YES, // 2. NO) >>> ')
        print('='*40)
        if start_rd == '1':
            abc = int(input('얼마를 배팅하시겠습니까? (1 ~ 10000) >>> '))
            print('='*40)
            if abc >= 1 and abc <= 10000:
                print(abc,'의 값을 배팅하셨습니다!!')
                print('='*40)
                Sum()
                print('플레이어:',a1,'+',a2,'=',player_1)
                print('  컴퓨터:',a3,'+',a4,'=',player_2)
                print('='*40)
                if player_1 > player_2:
                    print('승리하셨습니다!!')
                    money = money + abc
                    print('금액:',abc,'추가!!!')
                    print('지갑:',money)
                    print('='*40)
                if player_1 < player_2:
                    print('패배')
                    money = money - abc
                    print('금액',abc,'감소!!!')
                    print('지갑:',money)
                    print('='*40)
                if player_1 == player_2:
                    print('무승부')

            else:
                print('1~10000 사이의 숫자만 입력해주세요!')
        if start_rd == '2':
            print('게임을 종료합니다.')
            break
        if start_rd not in ['1','2']:
            print('잘못 입력했습니다!!')
