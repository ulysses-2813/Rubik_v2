import pygame
import pygame_gui
import sys # 万が一のエラー出力用
import os
import pygame_gui.core

class QuizManager:
	"""クイズ機能の管理に特化したクラス"""

	def __init__(self, manager, screen_rect, required_answers, country_data):
		self.manager = manager
		self.screen_rect = screen_rect
		self.required_answers = required_answers
		#self.country_pool = country_pool
		self.country_data = country_data
		
		self.answered_countries = []
		self.quiz_window = None
		self.question_label = None
		self.answer_entry = None
		self.answered_label = None
		self.is_cleared = False

	def create_window(self):
		"""クイズ用のUIWindowを作成して表示する"""
		if self.quiz_window:
			return
		
		if self.is_cleared:
			self.show_result_message('クリア済み', 'おめでとうございます！<br>すでにクリアしています！')
			return

		quiz_rect = pygame.Rect(0, 0, 500, 350)
		quiz_rect.center = self.screen_rect.center
		
		# object_id には '#' で始まる「文字列」を直接渡す
		self.quiz_window = pygame_gui.elements.UIWindow(
			rect=quiz_rect, manager=self.manager, window_display_title='quiz',
			object_id='#quiz_window' # <-- シンプルな文字列ID
		)


		self.question_label = pygame_gui.elements.UILabel(
			relative_rect=pygame.Rect(10, 10, 460, 50),
			text=f"国名を{self.required_answers}個当ててください ({len(self.answered_countries)}/{self.required_answers})",
			manager=self.manager, container=self.quiz_window,
			object_id=pygame_gui.core.ObjectID(class_id='@quiz_label', object_id='#quiz_question_label')
		)
		
		self.answer_entry = pygame_gui.elements.UITextEntryLine(
			relative_rect=pygame.Rect(50, 70, 400, 50),
			manager=self.manager, container=self.quiz_window,
			object_id=pygame_gui.core.ObjectID(class_id='@quiz_entry', object_id='#quiz_answer_entry')
		)

		self.answered_label = pygame_gui.elements.UILabel(
			relative_rect=pygame.Rect(10, 180, 460, 150),
			text=f"正解済み:{'<br>'.join(self.answered_countries)}",
			manager=self.manager, container=self.quiz_window,
			object_id=pygame_gui.core.ObjectID(class_id='@quiz_label', object_id='#answered_countries_label')
		)

		pygame_gui.elements.UIButton(
			relative_rect=pygame.Rect(200, 130, 100, 40),
			text='回答', manager=self.manager, container=self.quiz_window,
			object_id=pygame_gui.core.ObjectID(class_id='@quiz_button', object_id='#submit_answer_button')
		)
	
	def process_event(self, event):
		"""イベントを処理し、クイズに関連する操作を行う"""

		if event.type == pygame_gui.UI_BUTTON_PRESSED:
			
			obj_id_str = str(event.ui_object_id) # 例: '#wrong_message_window.#wrong_message_window_#ok_button'

			# 1a. メッセージウィンドウの 'OK' ボタン処理
			if '_#ok_button' in obj_id_str:
				
				# イベントをポストする代わりに、見つけたウィンドウを直接 .kill() する
				try:
					parts = obj_id_str.split('.')
					
					if not parts:
						#print(f"ERROR: Could not parse window_id from button_id: {obj_id_str}", file=sys.stderr)
						return
					
					window_id = parts[0] # 例: '#wrong_message_window'
					window_to_kill = None
					
					elements_list = []
					if hasattr(self.manager, 'root_container') and hasattr(self.manager.root_container, 'elements'):
						elements_list = self.manager.root_container.elements
					elif hasattr(self.manager, 'root_container') and hasattr(self.manager.root_container, 'container') and hasattr(self.manager.root_container.container, 'elements'):
						elements_list = self.manager.root_container.container.elements
					else:
						#print("ERROR: Could not find elements list in manager.root_container.", file=sys.stderr)
						elements_list = []

					# 比較対象を .most_specific_combined_id に変更
					for element in elements_list:
						if (isinstance(element, pygame_gui.elements.UIWindow) and 
							hasattr(element, 'most_specific_combined_id') and
							element.most_specific_combined_id == window_id): 
							
							window_to_kill = element
							break
					
					if window_to_kill:
						# ★★★ .kill() を直接呼び出す ★★★
						#print(f"DEBUG: OK Button pressed. Found window '{window_id}'. Calling .kill() directly.")
						window_to_kill.kill()
					
					else:
						# 警告文
						print(f"WARNING: OK button pressed, but could not find UIWindow with id '{window_id}' (using .most_specific_combined_id) to kill.", file=sys.stderr)
						print(f"(Button ID was: {obj_id_str})", file=sys.stderr)
				
				except Exception as e:
					print(f"ERROR: Failed to kill message window by calling .kill(): {e}", file=sys.stderr)
				# ★★★ 修正ここまで ★★★
				return 

			# 1b. クイズウィンドウの '回答' ボタン処理
			if self.quiz_window and obj_id_str.endswith('#submit_answer_button'):
				self.check_answer()
				return

		# 2. クイズウィンドウ自体の処理
		if event.type == pygame_gui.UI_WINDOW_CLOSE:
			
			window_id = "[ID unknown]"
			if hasattr(event.ui_element, 'most_specific_combined_id'):
				window_id = event.ui_element.most_specific_combined_id
			elif hasattr(event.ui_element, 'element_ids') and event.ui_element.element_ids:
				window_id = event.ui_element.element_ids[-1] # フォールバック
			#print(f"DEBUG: Window Close Event Detected - ID: {window_id}")

			if event.ui_element == self.quiz_window:
				#print("    -> This was the Main Quiz Window. Setting self.quiz_window = None.")
				self.quiz_window = None
				return
			
			#print("    -> This was a Result Window. UIManager will handle the kill.")
			return


	# quiz_gui.py の QuizManager クラス内

	def check_answer(self):
		"""ユーザーの回答をチェックして、結果を表示する"""
		
		if not self.answer_entry: 
			return
		
		user_answer = self.answer_entry.get_text()
		user_answer_lower = user_answer.lower() # ユーザーの入力を小文字化
		
		result_title, result_text = '', ''

		# --- ▼ 判定ロジックの変更 ▼ ---
		correct_country_name = None # 見つかった場合のキー（例: "Japan"）を格納
		
		# 保持している辞書 (self.country_data) をループしてチェック
		# (key="Japan", aliases=["日本"]) のようにループ
		for key, aliases in self.country_data.items():
			# 1. キー自体（例: "Japan"）と一致するかチェック
			if key.lower() == user_answer_lower:
				correct_country_name = key
				break
			
			# 2. 別名リスト（例: ["日本"]）と一致するかチェック
			if aliases: # aliases が None や空リストでない場合
				for alias in aliases:
					if alias.lower() == user_answer_lower:
						correct_country_name = key # 見つかったらキー（"Japan"）を採用
						break
			
			if correct_country_name: # どちらかで見つかったらループ終了
				break
		# --- ▲ 判定ロジックの変更ここまで ▲ ---

		# ↓↓↓ 以降のロジックはほぼ変更なし ↓↓↓
		
		# correct_country_name にはキー（"Japan"など）が入る
		if correct_country_name and correct_country_name not in self.answered_countries:
			# self.answered_countries にはキー（例: "Japan"）が追加される
			self.answered_countries.append(correct_country_name) 
			self.answer_entry.set_text('')
			self.update_labels() 

			if len(self.answered_countries) >= self.required_answers:
				# (クリア処理...)
				result_title, result_text = 'ゲームクリア！', 'おめでとうございます！<br>すべての国名を当てました！<br><br><font size=7><b>CLEAR!</b></font>'
				self.is_cleared = True
				if self.quiz_window:
					self.quiz_window.kill() 
					self.quiz_window = None
			else:
				result_title, result_text = '正解！', '<br><font size=7 color=#FF0000><b>○</b></font>'

		elif correct_country_name and correct_country_name in self.answered_countries:
			result_title, result_text = '回答済み', 'その国は既に答えています。'
		else:
			result_title, result_text = '不正解', '<br><font size=7 color=#0000FF><b>×</b></font>'

		if result_text:
			self.show_result_message(result_title, result_text)

	def update_labels(self):
		"""問題文と回答済みリストのラベルを最新の状態に更新する"""
		if self.question_label:
			self.question_label.set_text(f"国名を{self.required_answers}個当ててください ({len(self.answered_countries)}/{self.required_answers})")
		if self.answered_label:
			self.answered_label.set_text(f"正解済み:{'\n'.join(self.answered_countries)}")
	
	def show_result_message(self, title, message):
		"""結果表示用のカスタムメッセージウィンドウを表示する"""
		
		window_id_str = '@info_message_window'
		
		if '○' in message:
			msg_width, msg_height = 300, 200
			window_id_str = '@correct_message_window' # (これは '@' で始まる)
		elif '×' in message:
			msg_width, msg_height = 300, 200
			window_id_str = '@wrong_message_window'
		elif 'CLEAR!' in message:
			msg_width, msg_height = 500, 300
			window_id_str = '@clear_message_window'
		else:
			msg_width, msg_height = 400, 250
		
		center_x = self.screen_rect.centerx - (msg_width // 2)
		center_y = self.screen_rect.centery - (msg_height // 2)
		msg_rect = pygame.Rect((center_x, center_y), (msg_width, msg_height))

		try:
			# ★★★ 修正箇所 (1) ★★★
			# object_id には '#' で始まる「文字列」を直接渡す
			object_id_str = '#' + window_id_str.lstrip('@') # 例: '#wrong_message_window'

			message_window = pygame_gui.elements.UIWindow(
				rect=msg_rect,
				manager=self.manager,
				window_display_title=title,
				object_id=object_id_str # <-- シンプルな文字列ID (例: '#wrong_message_window')
			)
			# ★★★ 修正ここまで ★★★

			# --- ↓↓↓ DEBUG PRINT  ↓↓↓ ---
			#print(f"DEBUG: Window Opened (ResultWindow) - ID: {message_window.element_ids[-1]}")
			# --- ↑↑↑ DEBUG PRINT ↑↑↑ ---

			pygame_gui.elements.UITextBox(
				relative_rect=pygame.Rect(10, 10, msg_width - 40, msg_height - 100),
				html_text=message,
				manager=self.manager,
				container=message_window, 
				object_id=f"{object_id_str}_#text_box" # (object_id_strを使用)
			)

			button_width = 80
			button_height = 40
			button_x = (msg_width // 2) - (button_width // 2)
			button_y = msg_height - 65
			
			# ★★★ 修正箇所 (2) ★★★
			# ボタンの object_id もシンプルな文字列IDにする
			pygame_gui.elements.UIButton(
				relative_rect=pygame.Rect(button_x, button_y, button_width, button_height),
				text='OK',
				manager=self.manager,
				container=message_window, 
				object_id=f"{object_id_str}_#ok_button" # 例: '#wrong_message_window_#ok_button'
			)
			# ★★★ 修正ここまで ★★★
		except Exception as e:
			print(f"!!!!!!!!!!!!! ERROR creating result window: {e} !!!!!!!!!!!!!", file=sys.stderr)


# --- ↓↓↓ 単体実行用の main 関数 ↓↓↓ ---

def main():
	"""単体実行用のメイン関数"""
	pygame.init()


	# スクリーンとUIマネージャーのセットアップ
	WINDOW_WIDTH = 800
	WINDOW_HEIGHT = 600
	screen_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
	screen = pygame.display.set_mode(screen_size)
	pygame.display.set_caption("QuizManager デバッグウィンドウ")
	
	# ★★★ 修正箇所 ★★★

	# 1. この .py ファイルがあるディレクトリの絶対パスを取得
	script_dir = os.path.dirname(os.path.abspath(__file__))
	
	# 2. テーマファイルへの絶対パスを作成
	theme_file_path = os.path.join(script_dir, 'quiz_theme.json') 
	# 3. UIManager を初期化
	manager = pygame_gui.UIManager(
		screen_size, 
		theme_path=theme_file_path,
		starting_language ='ja' # <-- 'starting_language='japanese'' から変更
	)

	clock = pygame.time.Clock()

	# --- QuizManager のセットアップ ---
	
	COUNTRY_POOL = ["日本", "アメリカ", "中国", "フランス", "ドイツ", "イタリア", "イギリス"]
	REQUIRED_ANSWERS = 3
	
	screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
	
	quiz_manager = QuizManager(
		manager=manager,
		screen_rect=screen_rect,
		required_answers=REQUIRED_ANSWERS,
		country_data=COUNTRY_POOL
	)

	quiz_manager.create_window()
	
	# --- メインループ ---
	is_running = True
	while is_running:
		time_delta = clock.tick(60) / 1000.0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				is_running = False

			# 1. まず QuizManager にイベントを渡します
			quiz_manager.process_event(event)
			
			# 2. 次に UIManager にもイベントを渡します
			manager.process_events(event) # .process_events (複数形) に修正済み

		manager.update(time_delta)

		screen.fill((40, 40, 60))
		manager.draw_ui(screen)
		
		pygame.display.update()

	pygame.quit()


if __name__ == '__main__':
	main()
