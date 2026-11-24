from taximetro import main
board = []
EMPTY = "."
for i in range(8):
    row = [EMPTY for i in range(8)]
    board.append(row)
    if i % 2 == 0:
        board[i][0] = "R"
        board[i][7] = "R"
print(board)
main()