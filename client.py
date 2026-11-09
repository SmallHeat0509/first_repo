import sys
import pygame
import requests

# FastAPI Server 網址
API_BASE_URL = "https://first-repo-1-mw92.onrender.com"

# 顏色設定
COLOR_BG = (18, 18, 19)
COLOR_TEXT = (255, 255, 255)
COLOR_EMPTY = (58, 58, 60)
COLOR_CORRECT = (83, 141, 78)
COLOR_PRESENT = (181, 159, 59)
COLOR_ABSENT = (58, 58, 60)

# 初始化 Pygame
pygame.init()

WIDTH, HEIGHT = 500, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Pygame Wordle")

font = pygame.font.SysFont("Arial", 36, bold=True)
small_font = pygame.font.SysFont("Arial", 18)

class WordleGame:

    def __init__(self):

        self.game_id = None

        # 建立 6 行 5 列的遊戲格子
        self.grid = [
            ["" for _ in range(5)]
            for _ in range(6)
        ]

        # 預設全部為灰色
        self.colors = [
            [COLOR_EMPTY for _ in range(5)]
            for _ in range(6)
        ]

        self.row = 0
        self.col = 0

        self.game_over = False

        self.message = "Press ENTER to submit, ESC to restart"

        self.start_new_game()

    def start_new_game(self):

        try:

            res = requests.post(
                f"{API_BASE_URL}/api/new-game",
                json={"hard_mode": False},
                timeout=60
            )

            if res.status_code == 200:

                self.game_id = res.json()["game_id"]

                self.grid = [
                    ["" for _ in range(5)]
                    for _ in range(6)
                ]

                self.colors = [
                    [COLOR_EMPTY for _ in range(5)]
                    for _ in range(6)
                ]

                self.row = 0
                self.col = 0
                self.game_over = False

                self.message = "New game started!"

            else:

                self.message = "Server error!"

        except requests.exceptions.RequestException:

            self.message = "Cannot connect to server!"

    def submit_guess(self):

        if self.col < 5:

            self.message = "Not enough letters!"
            return

        guess_word = "".join(self.grid[self.row])

        try:

            payload = {
                "game_id": self.game_id,
                "guess": guess_word
            }

            res = requests.post(
                f"{API_BASE_URL}/api/guess",
                json=payload,
                timeout=60
            )

            if res.status_code == 200:

                data = res.json()

                feedback = data["feedback"]

                # 根據 Server 回傳結果改變顏色
                for i in range(5):

                    if feedback[i] == "correct":

                        self.colors[self.row][i] = COLOR_CORRECT

                    elif feedback[i] == "present":

                        self.colors[self.row][i] = COLOR_PRESENT

                    else:

                        self.colors[self.row][i] = COLOR_ABSENT

                if data["is_correct"]:

                    self.message = "You won! Press ESC to restart."
                    self.game_over = True

                elif data.get("game_over", False):

                    self.message = (
                        "Game Over! Answer: "
                        + str(data.get("target_word"))
                        + " Press ESC to restart."
                    )

                    self.game_over = True

                else:

                    self.row += 1
                    self.col = 0

                    self.message = "Keep guessing!"

            else:

                self.message = res.json().get(
                    "detail",
                    "Error processing guess"
                )

        except requests.exceptions.RequestException:

            self.message = "Network error during guess!"

    def handle_keydown(self, event):

        # R 鍵重新開始
        if event.key == pygame.K_ESCAPE:

            self.start_new_game()
            return

        if self.game_over:
            return

        # Backspace 刪除字母
        if event.key == pygame.K_BACKSPACE:

            if self.col > 0:

                self.col -= 1
                self.grid[self.row][self.col] = ""

        # Enter 提交答案
        elif event.key == pygame.K_RETURN:

            self.submit_guess()

        # 輸入英文字母
        elif event.unicode.isalpha() and len(event.unicode) == 1:

            if self.col < 5:

                self.grid[self.row][self.col] = event.unicode.upper()
                self.col += 1

    def draw(self, surface):

        surface.fill(COLOR_BG)

        margin_x = 75
        margin_y = 50

        box_size = 60
        gap = 10

        # 繪製 6 × 5 格子
        for r in range(6):

            for c in range(5):

                x = margin_x + c * (box_size + gap)
                y = margin_y + r * (box_size + gap)

                rect = pygame.Rect(
                    x, y,
                    box_size, box_size
                )

                pygame.draw.rect(
                    surface,
                    self.colors[r][c],
                    rect,
                    border_radius=4
                )

                if self.colors[r][c] == COLOR_EMPTY:

                    pygame.draw.rect(
                        surface,
                        (80, 80, 80),
                        rect,
                        width=2,
                        border_radius=4
                    )

                char = self.grid[r][c]

                if char:

                    text_surface = font.render(
                        char,
                        True,
                        COLOR_TEXT
                    )

                    text_rect = text_surface.get_rect(
                        center=rect.center
                    )

                    surface.blit(text_surface, text_rect)

        # 底部提示訊息
        msg_surface = small_font.render(
            self.message,
            True,
            COLOR_TEXT
        )

        msg_rect = msg_surface.get_rect(
            center=(WIDTH // 2, HEIGHT - 40)
        )

        surface.blit(msg_surface, msg_rect)


def main():

    clock = pygame.time.Clock()

    game = WordleGame()

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:

                game.handle_keydown(event)

        game.draw(screen)

        pygame.display.flip()

        clock.tick(30)


if __name__ == "__main__":

    main()
