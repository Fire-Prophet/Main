board = [["⬜"] * 5 for _ in range(5)]

def print_board():
    for row in board:
        print(" ".join(row))

while True:
    print_board()
    x = int(input("x 좌표 (0~4): "))
    y = int(input("y 좌표 (0~4): "))
    board[y][x] = "🟪"
