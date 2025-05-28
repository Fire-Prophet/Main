def mt_game_1():
    import random as rd
    global money
    com_1 = rd.randint(20,40)
    print(' 랜덤 숫자 게임 룰 '.center(30, '='))
    print('1, 컴퓨터가 임의 숫자를 정합니다!')
    print('2, 이 게임은 최소 2명의 플레이어가 필요합니다.!')
    print('3, 여러분들은 숫자 1~3사이를 선택하여 숫자이동을 해주세요!')
    print('4, 프로필 생성하신 분이 이기면 money + 2500, 지면 - 2500 입니다!')
    print('='*40)
    print(com_1)

    while True:
        aa = input('플레이어!! 1~3까지의 원하는 숫자를 정하세요! :) >>>')
        if aa not in ['1','2','3']:
            print('다시 선택!! :(')

        if com_1 > 0:
            if aa == '1':
                com_1 -= int(aa)
                print(com_1)
                if com_1 <= 0:
                    print('*'*30)
                    print('lose')
                    money -= 2500
                    print('돈:',money)
                    break

                if com_1 > 0:
                    bb = input('방해 플레이어!! 1~3까지의 원하는 숫자를 정하세요! :) >>>')
                    if bb == '1':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈:',money)
                            break
                        continue
                    if bb == '2':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈:',money)
                            break
                        continue
                    if bb == '3':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈:',money)
                            break
                        continue

            if aa == '2':
                com_1 -= int(aa)
                print(com_1)
                if com_1 <= 0:
                    print('*'*30)
                    print('lose')
                    money -= 2500
                    print('돈',money)
                    break

                if com_1 > 0:
                    bb = input('방해 플레이어!! 1~3까지의 원하는 숫자를 정하세요! :) >>>')
                    if bb == '1':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈:',money)
                            break
                        continue
                    if bb == '2':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈:',money)
                            break
                        continue
                    if bb == '3':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈',money)
                            break
                        continue

            if aa == '3':
                com_1 -= int(aa)
                print(com_1)
                if com_1 <= 0:
                    print('*'*30)
                    print('lose')
                    money -= 2500
                    print('돈:',money)
                    break

                if com_1 > 0:
                    bb = input('방해 플레이어!! 1~3까지의 원하는 숫자를 정하세요! :) >>>')
                    if bb == '1':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈:',money)
                            break
                        continue
                    if bb == '2':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈',money)
                            break
                        continue
                    if bb == '3':
                        com_1 -= int(bb)
                        print(com_1)
                        if com_1 <= 0:
                            print('*'*30)
                            print('win')
                            money += 2500
                            print('돈',money)
                            break
                        continue
