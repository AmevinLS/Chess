# Chess

A personal project: fully implementing the game of chess from the ground-up in Python (also with some basic "bots").

## How to use

If you want to play a ready GUI implementation, you can use `GraphicGame(p1, p2)` which accepts two `Player`s in the following way:
```
import chess
import chessbots

game = chess.GraphicGame(chessbots.Human(), chessbots.Human())
game.main()
```

In `chessbots` module, there are the following types of `Players`:
 - `Human()` - a person has to make the moves using computer mouse
 - `RandomBot()` - selects a random legal move and plays it
 - `MinMaxBot(max_depth)` - selects the best among legal move according to [MiniMax algorithm](https://en.wikipedia.org/wiki/Minimax) for given `max_depth` <br> *(side-note): the MinMaxBot is very slow, so setting the max_depth to a high value can lead to long processing times for the bot*


### How to use GUI

To make a move in the GUI, you should **click** the piece you want to move and **drag** it to desired position (without releasing mouse) <br> *(side-note): the animation for the moving pieces is not yet implemented*

![](/images/amevin_chess_demo.gif)


## How to extend
If you wish to extend and create a different implementation of the `Game`, you can create a `class YourGame(Game):` inheriting from the original class and use the implemented methods to make moves and extract info about the game state