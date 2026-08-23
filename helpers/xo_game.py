"""
لعبة إكس أو (Tic Tac Toe) للبوت

Developer: https://t.me/iJUCK
"""

import json
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class XOGame:
    def __init__(self, game_id: str, player1: dict, player2: dict = None):
        self.game_id = game_id
        self.player1 = player1  # {"id": int, "name": str}
        self.player2 = player2  # {"id": int, "name": str}
        self.winner = None
        self.winner_keys = []
        self.whose_turn = True  # True: Player1 (X), False: Player2 (O)
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self.board_keys = [
            [InlineKeyboardButton(
                "⬜",
                callback_data=f"XO:move:{i}:{j}:{game_id}"
            ) for j in range(3)] for i in range(3)
        ]
        # لا نضيف زر "العب مرة أخرى" هنا - سيتم إضافته فقط عند انتهاء اللعبة

    def is_draw(self) -> bool:
        """فحص إذا كانت اللعبة تعادل"""
        for i in range(3):
            for j in range(3):
                if not self.board[i][j]:
                    return False
        return True

    def fill_board(self, player_id: int, coord: tuple) -> bool:
        """ملء خانة في اللوحة"""
        row, col = coord
        if self.board[row][col]:
            return False
        
        if player_id == self.player1["id"]:
            self.board[row][col] = 1
            self.board_keys[row][col] = InlineKeyboardButton(
                "❌", 
                callback_data=f"XO:filled:{row}:{col}:{self.game_id}"
            )
        else:
            self.board[row][col] = 2
            self.board_keys[row][col] = InlineKeyboardButton(
                "⭕", 
                callback_data=f"XO:filled:{row}:{col}:{self.game_id}"
            )
        return True

    def check_winner(self) -> bool:
        """فحص الفائز"""
        # فحص الصفوف
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != 0:
                self.winner = self.player1 if self.board[i][0] == 1 else self.player2
                self.winner_keys.extend([(i, 0), (i, 1), (i, 2)])
                break
        
        # فحص الأعمدة
        if not self.winner:
            for j in range(3):
                if self.board[0][j] == self.board[1][j] == self.board[2][j] != 0:
                    self.winner = self.player1 if self.board[0][j] == 1 else self.player2
                    self.winner_keys.extend([(0, j), (1, j), (2, j)])
                    break
        
        # فحص القطر الرئيسي
        if not self.winner:
            if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0:
                self.winner = self.player1 if self.board[0][0] == 1 else self.player2
                self.winner_keys.extend([(0, 0), (1, 1), (2, 2)])
        
        # فحص القطر الثانوي
        if not self.winner:
            if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0:
                self.winner = self.player1 if self.board[0][2] == 1 else self.player2
                self.winner_keys.extend([(0, 2), (1, 1), (2, 0)])
        
        if self.winner:
            self._update_board_keys_for_end()
            return True
        return False

    def _update_board_keys_for_end(self, is_draw=False):
        """تحديث الأزرار عند انتهاء اللعبة"""
        new_board_keys = []
        for i in range(3):
            temp = []
            for j in range(3):
                if self.board[i][j] == 0:
                    temp.append(InlineKeyboardButton(
                        "⬜", 
                        callback_data=f"XO:ended:{i}:{j}:{self.game_id}"
                    ))
                elif self.board[i][j] == 1:
                    if not is_draw and self.winner and self.player1["id"] == self.winner["id"] and (i, j) in self.winner_keys:
                        temp.append(InlineKeyboardButton(
                            "✅", 
                            callback_data=f"XO:ended:{i}:{j}:{self.game_id}"
                        ))
                    else:
                        temp.append(InlineKeyboardButton(
                            "❌", 
                            callback_data=f"XO:ended:{i}:{j}:{self.game_id}"
                        ))
                else:  # self.board[i][j] == 2
                    if not is_draw and self.winner and self.player2["id"] == self.winner["id"] and (i, j) in self.winner_keys:
                        temp.append(InlineKeyboardButton(
                            "✅", 
                            callback_data=f"XO:ended:{i}:{j}:{self.game_id}"
                        ))
                    else:
                        temp.append(InlineKeyboardButton(
                            "⭕", 
                            callback_data=f"XO:ended:{i}:{j}:{self.game_id}"
                        ))
            new_board_keys.append(temp)
        
        # إضافة زر اللعب مرة أخرى
        new_board_keys.append([
            InlineKeyboardButton("🔄 العب مرة أخرى", callback_data=f"XO:reset:{self.game_id}")
        ])
        self.board_keys = new_board_keys

    def get_board_markup(self) -> InlineKeyboardMarkup:
        """الحصول على لوحة المفاتيح للعبة"""
        return InlineKeyboardMarkup(self.board_keys)

    def reset_game(self):
        """إعادة تعيين اللعبة"""
        # تبديل اللاعبين
        temp_p1 = self.player2 if self.player2 else self.player1
        temp_p2 = self.player1

        self.player1 = temp_p1
        self.player2 = temp_p2
        self.winner = None
        self.winner_keys = []
        self.whose_turn = True
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self._rebuild_board_keys()

    def _rebuild_board_keys(self):
        """إعادة بناء أزرار اللوحة بناءً على حالة اللعبة"""
        if self.winner or self.is_draw():
            # إذا انتهت اللعبة
            self._update_board_keys_for_end(is_draw=(not self.winner))
        else:
            # إذا كانت اللعبة مستمرة
            self.board_keys = []
            for i in range(3):
                row = []
                for j in range(3):
                    if self.board[i][j] == 0:
                        row.append(InlineKeyboardButton(
                            "⬜",
                            callback_data=f"XO:move:{i}:{j}:{self.game_id}"
                        ))
                    elif self.board[i][j] == 1:
                        row.append(InlineKeyboardButton(
                            "❌",
                            callback_data=f"XO:filled:{i}:{j}:{self.game_id}"
                        ))
                    else:  # self.board[i][j] == 2
                        row.append(InlineKeyboardButton(
                            "⭕",
                            callback_data=f"XO:filled:{i}:{j}:{self.game_id}"
                        ))
                self.board_keys.append(row)

            # لا نضيف زر "العب مرة أخرى" هنا - فقط عند انتهاء اللعبة


# دوال إدارة الألعاب
def get_game_from_redis(r, game_id: str) -> XOGame:
    """الحصول على لعبة من Redis"""
    game_data = r.get(f"XOGame:{game_id}")
    if game_data:
        import json
        data = json.loads(game_data)

        # إعادة بناء كائن اللعبة من البيانات المحفوظة
        game = XOGame(data["game_id"], data["player1"], data.get("player2"))
        game.winner = data.get("winner")
        game.winner_keys = data.get("winner_keys", [])
        game.whose_turn = data.get("whose_turn", True)
        game.board = data.get("board", [[0, 0, 0], [0, 0, 0], [0, 0, 0]])

        # إعادة بناء الأزرار
        game._rebuild_board_keys()

        return game
    return None

def save_game_to_redis(r, game: XOGame):
    """حفظ لعبة في Redis"""
    import json

    # تحويل كائن اللعبة إلى قاموس
    game_data = {
        "game_id": game.game_id,
        "player1": game.player1,
        "player2": game.player2,
        "winner": game.winner,
        "winner_keys": game.winner_keys,
        "whose_turn": game.whose_turn,
        "board": game.board
    }

    r.set(f"XOGame:{game.game_id}", json.dumps(game_data), ex=3600)  # تنتهي صلاحيتها بعد ساعة

def delete_game_from_redis(r, game_id: str):
    """حذف لعبة من Redis"""
    r.delete(f"XOGame:{game_id}")

def create_new_game(r, game_id: str, player1: dict) -> XOGame:
    """إنشاء لعبة جديدة"""
    game = XOGame(game_id, player1)
    save_game_to_redis(r, game)
    return game
