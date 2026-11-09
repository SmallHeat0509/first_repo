import os
import random
import uuid

from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# 建立 FastAPI
app = FastAPI(title="Wordle API Server")


# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Wordle 單字字典
WORD_BANK = [
    "APPLE", "TRAIN", "HOUSE", "PLANT", "SMART",
    "WORLD", "LIGHT", "BRAIN", "CLOUD", "WATER",
    "ABOUT", "ABOVE", "ACTOR", "ACUTE", "ADMIT",
    "ADOPT", "ADULT", "AFTER", "AGAIN", "AGENT",
    "AGREE", "AHEAD", "ALARM", "ALBUM", "ALERT",
    "ALIEN", "ALIKE", "ALIVE", "ALLOW", "ALONE",
    "ALONG", "ALTER", "AMONG", "ANGER", "ANGLE",
    "ANGRY", "APART", "APPLY", "ARGUE", "ARISE",
    "ARRAY", "ARROW", "ASIDE", "ASSET", "AUDIO",
    "AUDIT", "AVOID", "AWAKE", "AWARE", "BADGE",
    "BAKER", "BASIC", "BASIS", "BEACH", "BEGIN",
    "BEING", "BELOW", "BENCH", "BLACK", "BLAME",
    "BLANK", "BLAST", "BLEED", "BLEND", "BLOCK",
    "BLOOD", "BOARD", "BOAST", "BONUS", "BOOST",
    "BOUND", "BREAD", "BREAK", "BRICK", "BRIEF",
    "BRING", "BROAD", "BROWN", "BRUSH", "BUILD",
    "BUNCH", "BUYER", "CABLE", "CANDY", "CARGO",
    "CARRY", "CATCH", "CAUSE", "CHAIN", "CHAIR",
    "CHALK", "CHARM", "CHART", "CHASE", "CHEAP",
    "CHECK", "CHEST", "CHIEF", "CHILD", "CHOSE",
    "CIVIL", "CLAIM", "CLASS", "CLEAN", "CLEAR",
    "CLIMB", "CLOCK", "CLOSE", "COACH", "COAST",
    "COUNT", "COURT", "COVER", "CRASH", "CREAM",
    "CRIME", "CROSS", "CROWD", "CROWN", "CURVE",
    "CYCLE", "DAILY", "DANCE", "DEATH", "DELAY",
    "DEPTH", "DRAFT", "DRAMA", "DREAM", "DRIVE",
    "EAGLE", "EARLY", "EARTH", "EIGHT", "EMPTY",
    "ENEMY", "ENJOY", "ENTER", "EQUAL", "ERROR",
    "EVENT", "EVERY", "EXACT", "EXIST", "FAITH",
    "FALSE", "FAULT", "FIELD", "FIGHT", "FINAL",
    "FIRST", "FLAME", "FLASH", "FLOAT", "FLOOR",
    "FLOUR", "FLUID", "FOCUS", "FORCE", "FORTH",
    "FORTY", "FORUM", "FRAME", "FRESH", "FRONT",
    "FRUIT", "GIANT", "GLASS", "GLOBE", "GRACE",
    "GRADE", "GRAND", "GRANT", "GRASS", "GREAT",
    "GREEN", "GROUP", "GUARD", "GUESS", "GUIDE",
    "HAPPY", "HEART", "HEAVY", "HOTEL", "HUMAN",
    "IMAGE", "INDEX", "INPUT", "ISSUE", "JUDGE",
    "KNIFE", "LAYER", "LEMON", "LEVEL", "LIMIT",
    "LUNCH", "MAGIC", "MAJOR", "MARCH", "MATCH",
    "MEDAL", "MONEY", "MONTH", "MUSIC", "NIGHT",
    "NOVEL", "NURSE", "OCEAN", "OFFER", "ORDER"
]


# 遊戲資料庫
games_db: Dict[str, dict] = {}


# 遊戲統計
total_games = 0
total_wins = 0

# 接收玩家猜測的資料
class GuessRequest(BaseModel):
    game_id: str
    guess: str


# 接收建立遊戲的資料
class NewGameRequest(BaseModel):
    hard_mode: bool = False

@app.post("/api/new-game")
def start_new_game(req: NewGameRequest = None):
    global total_games

    if req is None:
        req = NewGameRequest()

    # 產生唯一遊戲編號
    game_id = str(uuid.uuid4())

    # 隨機選擇答案
    target_word = random.choice(WORD_BANK)

    # 儲存遊戲狀態
    games_db[game_id] = {
        "target": target_word,
        "status": "PLAYING",
        "attempts": 0,
        "hard_mode": req.hard_mode,
        "green_hints": {}
    }

    total_games += 1

    return {
        "game_id": game_id,
        "message": "New game started!",
        "hard_mode": req.hard_mode
    }

@app.get("/api/stats")
def get_stats():

    win_rate = (
        total_wins / total_games * 100
        if total_games > 0 else 0
    )

    return {
        "total_games": total_games,
        "wins": total_wins,
        "win_rate": round(win_rate, 2)
    }

    
@app.post("/api/guess")
def process_guess(req: GuessRequest):

    global total_wins

    game_id = req.game_id
    guess = req.guess.upper()

    # 1. 檢查遊戲是否存在
    if game_id not in games_db:
        raise HTTPException(
            status_code=404,
            detail="Game session not found."
        )

    game = games_db[game_id]

    # 2. 檢查遊戲是否結束
    if game["status"] != "PLAYING":
        raise HTTPException(
            status_code=400,
            detail="Game is already over."
        )

    # 3. 檢查長度
    if len(guess) != 5:
        raise HTTPException(
            status_code=400,
            detail="Word must be 5 letters."
        )

    # 4. 檢查字典
    if guess not in WORD_BANK:
        raise HTTPException(
            status_code=400,
            detail="Invalid word: not in dictionary"
        )

    # 5. Hard Mode 檢查
    if game["hard_mode"]:

        for position, letter in game["green_hints"].items():

            if guess[position] != letter:
                raise HTTPException(
                    status_code=400,
                    detail="Hard Mode: Must use revealed hint at green position"
                )

    target = game["target"]

    feedback = ["absent"] * 5
    target_letter_counts = {}

    # 計算答案中的字母數量
    for char in target:
        target_letter_counts[char] = (
            target_letter_counts.get(char, 0) + 1
        )

    # 6. 第一階段：判斷綠色
    for i in range(5):

        if guess[i] == target[i]:

            feedback[i] = "correct"

            target_letter_counts[guess[i]] -= 1

            # 記住綠色字母的位置
            game["green_hints"][i] = guess[i]

    # 7. 第二階段：判斷黃色
    for i in range(5):

        if feedback[i] != "correct":

            letter = guess[i]

            if target_letter_counts.get(letter, 0) > 0:

                feedback[i] = "present"

                target_letter_counts[letter] -= 1

    # 8. 增加有效猜測次數
    game["attempts"] += 1

    is_correct = (guess == target)

    # 9. 判斷勝負
    if is_correct:

        game["status"] = "WON"
        total_wins += 1

    elif game["attempts"] >= 6:

        game["status"] = "LOST"

    game_over = game["status"] != "PLAYING"

    return {
        "guess": guess,
        "feedback": feedback,
        "is_correct": is_correct,
        "attempts": game["attempts"],
        "remaining": max(0, 6 - game["attempts"]),
        "game_over": game_over,
        "target_word": target if game_over else None,
        "stats": get_stats()
    }


# 啟動 Server
if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
