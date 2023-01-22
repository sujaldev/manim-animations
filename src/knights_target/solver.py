from manim import (
    Square,
    Text,
    Dot,
    Line,
    Cross,
    Scene,
    VGroup,
    Write,
    Unwrite,
    FadeIn,
    ShowPassingFlash,
    ORIGIN,
    GREEN,
    GOLD,
    TEAL
)
from typing import Tuple, Dict
from vector import Vector

Point = Tuple[int, int]


class Board:
    COLORS = ("#444", "#FFF")
    TARGET_COLOR = GREEN

    def __init__(self, scene: Scene, obstacles: Tuple[Point, ...], target: Point, rows: int = 8, columns: int = 8):
        self.rows = rows
        self.columns = columns
        self.obstacles = obstacles
        self.target = target
        self.scene = scene

        self.cells: Dict[Point, Cell] = {}
        self.vgroup = VGroup()  # contains Cells
        self.gen_cells()

    def gen_cells(self):
        for y in range(self.rows):
            for x in range(self.columns):
                point = (x, y)
                cell = Cell(self.COLORS[(x + y) % 2])
                self.vgroup.add(cell)
                self.cells[point] = cell
        self.vgroup.set_x(0).arrange_in_grid(rows=self.rows, cols=self.columns, buff=0)

    def paint_board(self):
        self.scene.play(Write(self.vgroup))

    def paint_obstacles(self):
        group = VGroup(*(
            Cross(scale_factor=0.2).next_to(self.cells[obstacle], ORIGIN) for obstacle in self.obstacles
        ))
        self.scene.play(FadeIn(group))

    def paint_target(self):
        target = self.cells[self.target]
        self.scene.play(target.animate.set_fill(self.TARGET_COLOR))

    def paint(self):
        self.paint_board()
        self.paint_obstacles()
        self.paint_target()

    @property
    def available_cells(self):
        cells = self.cells.copy()
        for obstacle in self.obstacles:
            del cells[obstacle]
        return cells


# noinspection PyAbstractClass
class Cell(Square):
    SIDE_LENGTH = 0.9
    FONT_SIZE = 25

    FONT_COLOR = "#FFF"
    DOT_COLOR = GOLD
    LINE_COLOR = GOLD

    LINE_WIDTH = 3

    def __init__(self, fill: str):
        super().__init__(self.SIDE_LENGTH, fill_color=fill, fill_opacity=1, stroke_width=0)

        self.dot = Dot(fill_color=self.DOT_COLOR, radius=0.2)

        self.count = None  # Minimum number of moves required by the knight to reach this cell
        self.prev = None  # From which cell did the knight jump to this cell. (forming a tree)
        self.planted = False  # Whether this cell knows the minimum moves to get here (and how)

    def plant(self, count: int, prev: "Cell"):
        if not self.planted:
            self.count = count
            self.prev = prev
            self.planted = True
        else:
            raise Exception("Plant Conflict!")

    def gen_text(self, text, next_to: "Cell" = None):
        if next_to is None:
            next_to = self
        return Text(
            str(text), font_size=self.FONT_SIZE, color=self.FONT_COLOR
        ).next_to(next_to, ORIGIN).set_z_index(10)

    def paint_dots(self, buffer: Dict[str, VGroup]):
        self.dot.next_to(self, ORIGIN)
        self.prev.dot.next_to(self.prev, ORIGIN)
        if self.prev.count is None:
            buffer["dots"].add(self.prev.dot)
            self.prev.count = 0
        buffer["dots"].add(self.dot)

    def paint_lines(self, buffer: Dict[str, VGroup]):
        line = Line(
            start=self.prev.dot.get_center(),
            end=self.dot.get_center(),
            color=self.LINE_COLOR,
            stroke_width=self.LINE_WIDTH,
        )
        buffer["lines_swoosh"].add(line)
        buffer["lines"].add(line)

    def paint_text(self, buffer: Dict[str, VGroup]):
        if self.prev.count == 0:
            buffer["text"].add(self.gen_text(0, self.prev))
        buffer["text"].add(self.gen_text(self.count))

    def paint(self, buffer: Dict[str, VGroup]):
        self.paint_dots(buffer)
        self.paint_lines(buffer)
        self.paint_text(buffer)

    def paint_backwards(self, scene: Scene):
        current_cell = self
        # group = VGroup()
        scene.play(Write(VGroup(
            Dot(fill_color=self.DOT_COLOR, radius=0.2).next_to(current_cell, ORIGIN),
            self.gen_text(self.count)
        )))
        while current_cell.count != 0:
            prev_cell: Cell = current_cell.prev
            group = VGroup(
                Dot(fill_color=self.DOT_COLOR, radius=0.2).next_to(prev_cell, ORIGIN),
                self.gen_text(prev_cell.count, prev_cell),
                Line(
                    start=current_cell.get_center(),
                    end=prev_cell.get_center(),
                    color=self.LINE_COLOR,
                    stroke_width=self.LINE_WIDTH
                )
            )
            current_cell = prev_cell
            scene.play(Write(group))


class Knight:
    ALLOWED_MOVES = [
        Vector(1, 2),
        Vector(-1, 2),
        Vector(2, 1),
        Vector(-2, 1),
        Vector(1, -2),
        Vector(-1, -2),
        Vector(2, -1),
        Vector(-2, -1),
    ]

    COLOR = TEAL

    def __init__(self, position: Point, board: "Board"):
        self.position = Vector(*position)
        self.board = board
        self.scene = board.scene

        self.unplanted_cells = board.available_cells
        del self.unplanted_cells[position]

        self.animation_buffer = []

    def out_of_bounds(self, point: Vector):
        return not ((0 <= point.x < self.board.columns) and (0 <= point.y < self.board.rows))

    def next_moves(self, start: Vector, count: int, prev: Cell):
        moves = []

        for move in self.ALLOWED_MOVES:
            end = start + move
            end_xy = end.xy
            is_invalid_move = (
                    self.out_of_bounds(end) or
                    end_xy in self.board.obstacles or
                    end_xy not in self.unplanted_cells
            )
            if is_invalid_move:
                continue

            moves.append(end)

            # Plant Cell
            self.unplanted_cells[end_xy].plant(count, prev)
            del self.unplanted_cells[end_xy]

            # Draw Count
            self.board.cells[end_xy].paint(self.animation_buffer[-1])

        return moves

    def paint_knight(self):
        knight = self.board.cells[self.position.xy]
        self.scene.play(knight.animate.set_fill(self.COLOR))

    def paint_tree(self):
        last_moves = [self.position]

        count = 1
        while self.board.target in self.unplanted_cells:
            moves = []
            self.animation_buffer.append({
                "dots": VGroup(),
                "lines_swoosh": VGroup(),
                "lines": VGroup(),
                "text": VGroup(),
            })

            for move in last_moves:
                move_xy = move.xy
                moves += self.next_moves(move, count, self.board.cells[move_xy])

            self.paint_next_moves()

            last_moves = moves
            count += 1

    def paint_next_moves(self):
        buffer = self.animation_buffer[-1]
        self.scene.play(FadeIn(buffer["dots"]))
        self.scene.play(ShowPassingFlash(buffer["lines_swoosh"]))
        self.scene.play(Write(buffer["lines"]))
        self.scene.play(FadeIn(buffer["text"]))

    def remove_tree(self):
        tree = VGroup()
        for animations in self.animation_buffer:
            del animations["lines_swoosh"]
            for animation in animations.values():
                tree += animation

        self.scene.play(Unwrite(tree))

    def paint_solution(self):
        self.board.cells[self.board.target].paint_backwards(self.scene)

    def paint(self):
        self.paint_knight()
        self.paint_tree()
        self.scene.wait(2)
        self.remove_tree()
