Wordle Game
專案介紹

這是一款使用 Python 開發的英文單字猜謎遊戲，結合 Pygame 和 FastAPI，採用 Client-Server 架構。

遊戲規則
玩家需要在六次機會內猜出五個英文字母的單字。
綠色：字母和位置都正確。
黃色：字母正確，但位置錯誤。
灰色：答案中沒有這個字母。
使用技術
Python 3.12
Pygame
FastAPI
Uvicorn
Requests
Pydantic
專案檔案
client.py：遊戲畫面及玩家操作。
server.py：後端 API 及答案判斷。
requirements.txt：所需 Python 套件。
安裝套件
bash
py -3.12 -m pip install -r requirements.txt

執行方式

先啟動 Server：

bash
py -3.12 server.py


再開啟另一個 Terminal，執行 Client：

bash
py -3.12 client.py

遊戲操作
A～Z：輸入英文字母
Backspace：刪除字母
Enter：提交答案
ESC：重新開始遊戲