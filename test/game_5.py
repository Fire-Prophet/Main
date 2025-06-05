def kim_game():
    import random as rd
    global money
    print('게임 도박 룰'.center(30, '='))
    print('1, 코인을 배팅해 도박할 수 있습니다.')
    print('2, 일정 확률로 성공하며, 2배,3배,5배 중 하나의 보상을 지급합니다')
    print('3, 한번에 1000원의 배팅과 올인을 할 수 있습니다')
    print('='*40)
    while True:
        start_3 = input('시작하겠습니까? (1. Yes // 2. No) >>>')
        if start_3 == '1':
            game_3 = input("돈을 걸까요? { 1,1000 2.올인 } >>>")
            if game_3 == '1':
                com_2 = rd.randint(1,100)                 #100가지의 숫자를 랜덤으로 입력
                if money <= 1000:
                    print('1000원 이상의 돈이 없습니다.')
                    break                    
                    money -= 1000

                if com_2 > 50:
                    com_3 = rd.randint(1,10)          #2배,3배,5배를 정하기 위해서 10가지의 숫자를 랜덤으로 입력
                    if com_3 <= 5:
                        print('우와 축하해요! 2배로 성공했어요.')
                        money += 3000
                        print(money)
                        continue
 
                    if com_3 <= 9:
                        print('3배라니.. 운이 좋은데요?')
                        money += 4000
                        print(money)
                        continue
 
                    if com_3 == 10:
                        print('우와 5배라니.. 운이 좋으신데요?')
                        money += 6000
                        print(money)
                        continue
 
                if com_2 < 50:
                    print('다음에는 성공할 수 있을 거예요.. 화이팅!')
                    print(money)
                    continue
 
                if com_2 == 50:
                    print('777 잭팟')
                    money += 10000
                    print(money)
                    continue 
 
            if game_3 == '2':
                com_4 = rd.randint(1,100)
                if com_4 > 50:
                    print('떡상의 축제를 열어라!!!')
                    money = money*2
                    print(money)
                    continue
 
                if com_4 < 50:
                    print('저런.. 돈을 다 날리셨어요..')
                    money -= money
                    print(money)
                    continue
 
                if com_4 == 50:
                    print('올인 잭팟')
                    money = money*money
                    print(money)
                    continue
 
        if start_3 == '2':
            print('취소합니다')
            break
