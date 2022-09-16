import chessbots
import chess
import cProfile, pstats

game = chess.Game()
bot = chessbots.MinMaxBot(max_depth=2)

profiler = cProfile.Profile()
profiler.enable()
bot._find_move(game.get_state())
profiler.disable()

stream = open("test.txt", "w")
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats("cumtime")
stats.print_stats()

# game = chess.GraphicGame(chessbots.Human(), chessbots.Human())
# game.main()
