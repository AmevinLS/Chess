import chessbots
import chess


game = chess.GraphicGame(chessbots.Human(), chessbots.MinMaxBot(max_depth=2))
game.main()
