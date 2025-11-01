# %%
import pygame
import sys
import pygame_gui
import import_ipynb
import os

def resource_path(relative_path):
	""" .exe 化された場合と通常実行の場合で、リソースへのパスを正しく取得する """
	# PyInstaller が作成したテンポラリフォルダが設定されている場合はそちらを使い、
	# 無ければカレントディレクトリを使う（属性アクセスを直接しないことで型チェック等の警告を回避）
	base_path = getattr(sys, '_MEIPASS', None)
	if base_path is None:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, relative_path)

# %%
from rubik_gui import RubikGame, SCREEN_W, SCREEN_H  # type: ignore

try:
	pygame.mixer.init()
except pygame.error as e:
	print(f"Warning: pygame.mixer.init() に失敗しました: {e}", file=sys.stderr)

pygame.init()
# %%
def run_difficulty_selector(screen, manager):
	width, height = screen.get_size()
	pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 50, width, 100), text='難易度選択', manager=manager, object_id='#title_label')
	button_width, button_height = 300, 90
	button_x = (width - button_width) // 2
	buttons_info = {
		"easy":   {"text": "初級", "y_pos": 180, "id": "#easy_button"},
		"medium": {"text": "中級", "y_pos": 300, "id": "#medium_button"},
		"hard":   {"text": "上級", "y_pos": 420, "id": "#hard_button"},
		"quit":   {"text": "終了", "y_pos": 540, "id": "#quit_button"}
	}

	# forループでボタンをまとめて作成
	for key, info in buttons_info.items():
		pygame_gui.elements.UIButton(
			relative_rect=pygame.Rect(button_x, info["y_pos"], button_width, button_height),
			text=info["text"],
			manager=manager,
			# object_idにユニークなIDを指定する
			object_id=pygame_gui.core.ObjectID(class_id='@difficulty_button', object_id=info["id"])
		)

	clock = pygame.time.Clock()
	while True:
		time_delta = clock.tick(60) / 1000.0
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return None
			if event.type == pygame_gui.UI_BUTTON_PRESSED:
				if event.ui_element.text == "初級": return "easy"
				if event.ui_element.text == "中級": return "medium"
				if event.ui_element.text == "上級": return "hard"
				if event.ui_element.text == "終了": return None
			manager.process_events(event)
		manager.update(time_delta)
		screen.fill((255, 255, 255))
		manager.draw_ui(screen)
		pygame.display.flip()

# %%
def main():
	screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
	while True:
		pygame.display.set_caption("難易度選択")
		ui_manager = pygame_gui.UIManager((SCREEN_W, SCREEN_H), resource_path('theme.json') , starting_language='ja')
		difficulty = run_difficulty_selector(screen, ui_manager)
		if difficulty is None: break
		print(f"難易度「{difficulty}」でゲームを開始します。")
		game = RubikGame(difficulty=difficulty, screen_surface=screen)
		game_result = game.run()
		if game_result == "QUIT_PROGRAM": break
	pygame.quit()
	print("プログラムを終了しました。")

# --- このセルを実行するとゲームが始まります ---
main()


