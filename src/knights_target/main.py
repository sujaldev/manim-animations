from manim import *

import params
from solver import Board, Knight

# config.background_color = "#1A191A"
config.background_color = "#F2E1C6"


class Main(Scene):
    def construct(self):
        self.intro()
        self.wait(1)
        self.scene2()

    def intro(self):
        bg = Square(20, fill_color="#1A191A", fill_opacity=1)
        text = Text("Hello, world!")
        self.add(bg)
        self.play(Write(text))
        self.wait(10)
        self.play(Unwrite(text))
        self.play(FadeOut(bg))

    def scene2(self):
        board = Board(self, params.obstacles, params.target)
        knight = Knight(params.knight, board)
        board.paint()
        self.wait(15)
        knight.paint_knight()
        self.wait(10)
        knight.paint_tree()
        self.wait(5)
        knight.remove_tree()
        self.wait(5)
        knight.paint_solution()
        self.wait(10)


if __name__ == "__main__":
    import subprocess

    subprocess.run(["manim", "-pqh", __file__, "Main"])
