from badgeware import run, screen, brushes, shapes, io, PixelFont
import random

# Load a readable font if available
try:
    font = PixelFont.load("/system/assets/fonts/nope.ppf")
except Exception:
    font = None

# Colors
BG = brushes.color(0, 0, 0)
FG = brushes.color(255, 255, 255)
ACCENT = brushes.color(80, 200, 120)

# Game states
STATE_START = 0
STATE_SELECT = 1
STATE_SHOWDOWN = 2

# Moves
MOVE_ROCK = 0
MOVE_PAPER = 1
MOVE_SCISSORS = 2
MOVE_NAMES = {MOVE_ROCK: "Rock", MOVE_PAPER: "Paper", MOVE_SCISSORS: "Scissors"}


def draw_text_center(text, y, brush=FG):
    screen.brush = brush
    if font:
        screen.font = font
    w, h = screen.measure_text(text)
    screen.text(text, 80 - (w / 2), y - (h / 2))


def draw_question_mark():
    # Draw a question mark as a fixed-grid text to ensure proper alignment.
    screen.brush = FG
    # Use a small monospace-like rendering: 7 columns x 7 rows
    pattern = [
        "  ###  ",
        " #   # ",
        "     # ",
        "   ##  ",
        "   #   ",
        "       ",
        "   #   ",
    ]

    x0 = 8
    y0 = 18

    # If a pixel font is loaded and provides consistent character width, use
    # that to space characters. Otherwise fall back to a fixed column width.
    if font:
        char_w, char_h = screen.measure_text("M")
        col_w = int(char_w)
        row_h = int(char_h + 2)
    else:
        col_w = 8
        row_h = 10

    for row_idx, row in enumerate(pattern):
        y = y0 + row_idx * row_h
        # draw each character in the row so spacing is precise
        for col_idx, ch in enumerate(row):
            if ch != " ":
                x = x0 + col_idx * col_w
                screen.text(ch, x, y)


def draw_move_big(move, x):
    screen.brush = FG
    label = MOVE_NAMES.get(move, "?")
    # draw a simple boxed label
    screen.draw(shapes.rounded_rectangle(x, 30, 60, 60, 6))
    screen.brush = BG
    screen.text(label, x + 30 - (screen.measure_text(label)[0] / 2), 60 - 6)


class RPS:
    def __init__(self):
        self.state = STATE_START
        self.badge_move = random.randint(0, 2)
        self.player_move = None
        self.show_anim = 0

    def init(self):
        random.seed(io.ticks)

    def update(self):
        # clear
        screen.brush = BG
        screen.draw(shapes.rectangle(0, 0, 160, 120))

        # common header
        screen.brush = ACCENT
        screen.draw(shapes.rectangle(0, 0, 160, 14))
        screen.brush = FG
        screen.text("Rock Paper Scissors", 4, 2)

        if self.state == STATE_START:
            draw_text_center("Press A to begin", 64)
            if io.BUTTON_A in io.pressed:
                self._enter_select()

        elif self.state == STATE_SELECT:
            # left half: question mark (badge move hidden)
            draw_question_mark()
            # right half: instructions and choices
            draw_text_center("Choose:", 10)
            # show mapping for buttons
            screen.text("A: Rock", 100, 40)
            screen.text("B: Paper", 100, 60)
            screen.text("C: Scissors", 100, 80)

            # allow selection
            if io.BUTTON_A in io.pressed:
                self.player_move = MOVE_ROCK
                self._enter_showdown()
            elif io.BUTTON_B in io.pressed:
                self.player_move = MOVE_PAPER
                self._enter_showdown()
            elif io.BUTTON_C in io.pressed:
                self.player_move = MOVE_SCISSORS
                self._enter_showdown()

        elif self.state == STATE_SHOWDOWN:
            # simple reveal animation: slide badge move in from left
            progress = min(1.0, self.show_anim / 10.0)
            # background areas
            screen.brush = FG
            # draw badge move box sliding from -60 to 10
            x = int((-60) + (70 * progress))
            draw_move_big(self.badge_move, x)
            # draw player move on right
            draw_move_big(self.player_move, 90)

            if self.show_anim < 11:
                self.show_anim += 1
            else:
                # determine result and show text
                result = self._determine_result()
                if result == 0:
                    draw_text_center("Draw", 100, brush=ACCENT)
                elif result == 1:
                    draw_text_center("You Win!", 100, brush=ACCENT)
                else:
                    draw_text_center("You Lose", 100, brush=ACCENT)

                draw_text_center("Press A to play again", 112)
                if io.BUTTON_A in io.pressed:
                    self._reset()

        return None

    def _enter_select(self):
        self.state = STATE_SELECT
        self.badge_move = random.randint(0, 2)
        self.player_move = None

    def _enter_showdown(self):
        self.state = STATE_SHOWDOWN
        self.show_anim = 0

    def _determine_result(self):
        # 0 = draw, 1 = player win, 2 = player lose
        if self.player_move == self.badge_move:
            return 0
        # rock beats scissors, scissors beats paper, paper beats rock
        wins = {
            MOVE_ROCK: MOVE_SCISSORS,
            MOVE_SCISSORS: MOVE_PAPER,
            MOVE_PAPER: MOVE_ROCK,
        }
        if wins[self.player_move] == self.badge_move:
            return 1
        return 2

    def _reset(self):
        self.state = STATE_SELECT
        self.badge_move = random.randint(0, 2)
        self.player_move = None


app = RPS()

def init():
    app.init()


def update():
    return app.update()


if __name__ == "__main__":
    run(update)
