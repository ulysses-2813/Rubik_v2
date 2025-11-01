# %%
import pygame
import math
import random
import os
from PIL import Image
import pygame_gui
from quiz_gui import QuizManager
import sys

def resource_path(relative_path):
	""" .exe 化された場合と通常実行の場合で、リソースへのパスを正しく取得する """
	# PyInstaller が作成したテンポラリフォルダが設定されている場合はそちらを使い、
	# 無ければカレントディレクトリを使う（属性アクセスを直接しないことで型チェック等の警告を回避）
	base_path = getattr(sys, '_MEIPASS', None)
	if base_path is None:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, relative_path)  

# --- Pygame初期化 ---
try:
	pygame.display.init()
except pygame.error:
	pass # 既に初期化済みの場合
try:
	pygame.font.init()
except pygame.error:
	pass # 既に初期化済みの場合

# --- 定数定義 ---
TILE_SIZE = 60
MARGIN = TILE_SIZE // 3
FACE_SIZE = TILE_SIZE * 3
CANVAS_SIZE_W = (FACE_SIZE + MARGIN) * 4 + MARGIN
CANVAS_SIZE_H = (FACE_SIZE + MARGIN) * 3 + MARGIN
GRID_OFFSET_X = TILE_SIZE * 2
GRID_OFFSET_Y = TILE_SIZE

# ★全画面サイズを取得
screen_info = pygame.display.Info()
SCREEN_W = screen_info.current_w
SCREEN_H = screen_info.current_h


# flags_database_success.csv に基づく英日国名対応辞書
# キー: CSVの '国名' カラムの値 (rubik_gui.ipynb でファイル名から生成される名前と一致することを想定)
# 値: [日本語の略称, 日本語の正式名称, (その他の通称)]
COUNTRY_NAME_MAP = \
{   'Islamic Emirate': ['アフガニスタン・イスラム国', 'アフガニスタン・イスラム首長国', 'アフガニスタン', 'タリバン'],
	'Republic': ['アフガニスタン', 'アフガニスタン・イスラム共和国'],
	'Albania': ['アルバニア', 'アルバニア共和国'],
	'Algeria': ['アルジェリア', 'アルジェリア民主人民共和国'],
	'Andorra': ['アンドラ公国', 'アンドラ'],
	'Angola': ['アンゴラ', 'アンゴラ共和国'],
	'Antigua and Barbuda': ['アンティグア・バーブーダ'],
	'Argentina': ['アルゼンチン', 'アルゼンチン共和国'],
	'Armenia': ['アルメニア共和国', 'アルメニア'],
	'Australia': ['オーストラリア連邦', '豪州', 'オーストラリア', '豪'],
	'Austria': ['オーストリア共和国', 'オーストリア'],
	'Azerbaijan': ['アゼルバイジャン', 'アゼルバイジャン共和国'],
	'Bahrain': ['バーレーン王国', 'バーレーン'],
	'Bangladesh': ['バングラデシュ', 'バングラデシュ人民共和国'],
	'Barbados': ['バルバドス'],
	'Belarus': ['ベラルーシ', 'ベラルーシ共和国'],
	'Belgium': ['ベルギー王国', 'ベルギー'],
	'Belize': ['ベリーズ'],
	'Benin': ['ベナン', 'ベナン共和国'],
	'Bhutan': ['ブータン王国', 'ブータン'],
	'Bolivia': ['ボリビア', 'ボリビア多民族国'],
	'Bosnia and Herzegovina': ['ボスニア・ヘルツェゴビナ'],
	'Botswana': ['ボツワナ共和国', 'ボツワナ'],
	'Brazil': ['ブラジル連邦共和国', 'ブラジル', '伯'],
	'Brunei': ['ブルネイ', 'ブルネイ・ダルサラーム国'],
	'Bulgaria': ['ブルガリア', 'ブルガリア共和国'],
	'Burkina Faso': ['ブルキナファソ'],
	'Burundi': ['ブルンジ', 'ブルンジ共和国'],
	'Cambodia': ['カンボジア王国', 'カンボジア'],
	'Cameroon': ['カメルーン共和国', 'カメルーン'],
	'Canada': ['カナダ', '加'],
	'Chad': ['チャド共和国', 'チャド'],
	'Chile': ['チリ', 'チリ共和国'],
	'China': ['中華人民共和国', '中', '中国'],
	'Colombia': ['コロンビア', 'コロンビア共和国'],
	'Costa Rica': ['コスタリカ共和国', 'コスタリカ'],
	'Croatia': ['クロアチア共和国', 'クロアチア'],
	'Cuba': ['キューバ', 'キューバ共和国'],
	'Cyprus': ['キプロス共和国', 'キプロス'],
	'Denmark': ['デンマーク', 'デンマーク王国'],
	'Djibouti': ['ジブチ共和国', 'ジブチ'],
	'Dominica': ['ドミニカ', 'ドミニカ国'],
	'Ecuador': ['エクアドル共和国', 'エクアドル'],
	'Egypt': ['エジプト', 'エジプト・アラブ共和国'],
	'El Salvador': ['エルサルバドル共和国', 'エルサルバドル'],
	'Equatorial Guinea': ['赤道ギニア', '赤道ギニア共和国'],
	'Eritrea': ['エリトリア国', 'エリトリア'],
	'Estonia': ['エストニア共和国', 'エストニア'],
	'Eswatini': ['エスワティニ', 'エスワティニ王国'],
	'Ethiopia': ['エチオピア連邦民主共和国', 'エチオピア'],
	'Fiji': ['フィジー共和国', 'フィジー'],
	'Finland': ['フィンランド共和国', 'フィンランド'],
	'France': ['フランス共和国', 'フランス', '仏'],
	'Gabon': ['ガボン', 'ガボン共和国'],
	'Georgia': ['ジョージア', 'グルジア'],
	'Germany': ['ドイツ連邦共和国', 'ドイツ', '独'],
	'Ghana': ['ガーナ共和国', 'ガーナ'],
	'Greece': ['ギリシャ共和国', 'ギリシャ'],
	'Grenada': ['グレナダ'],
	'Guatemala': ['グアテマラ', 'グアテマラ共和国'],
	'Guinea': ['ギニア共和国', 'ギニア'],
	'Guinea-Bissau': ['ギニアビサウ共和国', 'ギニアビサウ'],
	'Guyana': ['ガイアナ', 'ガイアナ協同共和国'],
	'Haiti': ['ハイチ', 'ハイチ共和国'],
	'Honduras': ['ホンジュラス共和国', 'ホンジュラス'],
	'Hungary': ['ハンガリー'],
	'Iceland': ['アイスランド', 'アイスランド共和国'],
	'India': ['インド', '印', 'インド共和国'],
	'Indonesia': ['インドネシア', 'インドネシア共和国'],
	'Iran': ['イラン', 'イラン・イスラム共和国'],
	'Iraq': ['イラク共和国', 'イラク'],
	'Ireland': ['アイルランド共和国', 'アイルランド'],
	'Israel': ['イスラエル', 'イスラエル国'],
	'Italy': ['伊', 'イタリア共和国', 'イタリア'],
	'Jamaica': ['ジャマイカ'],
	'Japan': ['日本', '日本国'],
	'Jordan': ['ヨルダン・ハシミテ王国', 'ヨルダン'],
	'Kazakhstan': ['カザフスタン共和国', 'カザフスタン'],
	'Kenya': ['ケニア共和国', 'ケニア'],
	'Kiribati': ['キリバス', 'キリバス共和国'],
	'Kosovo': ['コソボ共和国', 'コソボ'],
	'Kuwait': ['クウェート国', 'クウェート'],
	'Kyrgyzstan': ['キルギスタン', 'キルギス', 'キルギス共和国'],
	'Laos': ['ラオス人民民主共和国', 'ラオス'],
	'Latvia': ['ラトビア共和国', 'ラトビア'],
	'Lebanon': ['レバノン共和国', 'レバノン'],
	'Lesotho': ['レソト', 'レソト王国'],
	'Liberia': ['リベリア共和国', 'リベリア'],
	'Libya': ['リビア', 'リビア国'],
	'Liechtenstein': ['リヒテンシュタイン公国', 'リヒテンシュタイン'],
	'Lithuania': ['リトアニア共和国', 'リトアニア'],
	'Luxembourg': ['ルクセンブルク', 'ルクセンブルク大公国'],
	'Madagascar': ['マダガスカル', 'マダガスカル共和国'],
	'Malawi': ['マラウイ', 'マラウイ共和国'],
	'Malaysia': ['馬', 'マレーシア'],
	'Maldives': ['モルディブ共和国', 'モルディブ'],
	'Mali': ['マリ', 'マリ共和国'],
	'Malta': ['マルタ', 'マルタ共和国'],
	'Mauritania': ['モーリタニア', 'モーリタニア・イスラム共和国'],
	'Mauritius': ['モーリシャス', 'モーリシャス共和国'],
	'Mexico': ['メキシコ', 'メキシコ合衆国', '墨'],
	'Moldova': ['モルドバ共和国', 'モルドバ'],
	'Monaco': ['モナコ', 'モナコ公国'],
	'Mongolia': ['モンゴル', 'モンゴル国'],
	'Montenegro': ['モンテネグロ'],
	'Morocco': ['モロッコ', 'モロッコ王国'],
	'Mozambique': ['モザンビーク共和国', 'モザンビーク'],
	'Myanmar': ['ミャンマー', 'ビルマ', 'ミャンマー連邦共和国'],
	'Namibia': ['ナミビア', 'ナミビア共和国'],
	'Nauru': ['ナウル', 'ナウル共和国'],
	'Nepal': ['ネパール連邦民主共和国', 'ネパール'],
	'New Zealand': ['NZ', 'ニュージーランド'],
	'Nicaragua': ['ニカラグア共和国', 'ニカラグア'],
	'Niger': ['ニジェール共和国', 'ニジェール'],
	'Nigeria': ['ナイジェリア連邦共和国', 'ナイジェリア'],
	'North Korea': ['DPRK', '朝鮮民主主義人民共和国', '北朝鮮'],
	'North Macedonia': ['北マケドニア共和国', '北マケドニア'],
	'Norway': ['ノルウェー', 'ノルウェー王国'],
	'Oman': ['オマーン', 'オマーン国'],
	'Pakistan': ['パキスタン', 'パキスタン・イスラム共和国'],
	'Palau': ['パラオ共和国', 'パラオ'],
	'Palestine': ['パレスチナ国', 'パレスチナ'],
	'Panama': ['パナマ共和国', 'パナマ'],
	'Papua New Guinea': ['パプアニューギニア独立国', 'パプアニューギニア'],
	'Paraguay': ['パラグアイ', 'パラグアイ共和国'],
	'Peru': ['ペルー共和国', 'ペルー'],
	'Poland': ['ポーランド共和国', 'ポーランド'],
	'Portugal': ['ポルトガル', '葡', 'ポルトガル共和国'],
	'Qatar': ['カタール', 'カタール国'],
	'Romania': ['ルーマニア'],
	'Russia': ['ロシア連邦', '露', 'ロシア'],
	'Rwanda': ['ルワンダ', 'ルワンダ共和国'],
	'Saint Kitts and Nevis': ['セントクリストファー・ネーヴィス'],
	'Saint Lucia': ['セントルシア'],
	'Saint Vincent and the Grenadines': ['セントビンセント・グレナディーン'],
	'Samoa': ['サモア独立国', 'サモア'],
	'San Marino': ['サンマリノ共和国', 'サンマリノ'],
	'Saudi Arabia': ['サウジアラビア王国', 'サウジアラビア', 'サウジ'],
	'Senegal': ['セネガル', 'セネガル共和国'],
	'Serbia': ['セルビア', 'セルビア共和国'],
	'Seychelles': ['セーシェル共和国', 'セーシェル'],
	'Sierra Leone': ['シエラレオネ共和国', 'シエラレオネ'],
	'Singapore': ['シンガポール', '星', 'シンガポール共和国'],
	'Slovakia': ['スロバキア共和国', 'スロバキア'],
	'Slovenia': ['スロベニア共和国', 'スロベニア'],
	'Somalia': ['ソマリア', 'ソマリア連邦共和国'],
	'South Africa': ['南アフリカ', '南アフリカ共和国', '南ア'],
	'South Korea': ['南朝鮮', '韓国', '大韓民国'],
	'South Sudan': ['南スーダン', '南スーダン共和国'],
	'Spain': ['スペイン', 'スペイン王国', '西'],
	'Sri Lanka': ['スリランカ民主社会主義共和国', 'スリランカ'],
	'Sudan': ['スーダン共和国', 'スーダン'],
	'Suriname': ['スリナム', 'スリナム共和国'],
	'Sweden': ['スウェーデン', '瑞', 'スウェーデン王国'],
	'Switzerland': ['スイス連邦', '瑞', 'スイス'],
	'Syria': ['シリア・アラブ共和国', 'シリア'],
	'Taiwan': ['台湾', '中華民国'],
	'Tajikistan': ['タジキスタン共和国', 'タジキスタン'],
	'Tanzania': ['タンザニア', 'タンザニア連合共和国'],
	'Thailand': ['タイ王国', 'タイ'],
	'Timor-Leste': ['東ティモール民主共和国', '東ティモール'],
	'Togo': ['トーゴ', 'トーゴ共和国'],
	'Tonga': ['トンガ王国', 'トンガ'],
	'Trinidad and Tobago': ['トリニダード・トバゴ共和国', 'トリニダード・トバゴ'],
	'Tunisia': ['チュニジア', 'チュニジア共和国'],
	'Turkey': ['トルコ共和国', 'トルコ'],
	'Turkmenistan': ['トルクメニスタン'],
	'Tuvalu': ['ツバル'],
	'Uganda': ['ウガンダ', 'ウガンダ共和国'],
	'Ukraine': ['ウクライナ'],
	'United Kingdom': ['英国', 'イギリス', '英', 'グレートブリテン及び北アイルランド連合王国'],
	'Uruguay': ['ウルグアイ', 'ウルグアイ東方共和国'],
	'Uzbekistan': ['ウズベキスタン共和国', 'ウズベキスタン'],
	'Vanuatu': ['バヌアツ', 'バヌアツ共和国'],
	'Venezuela': ['ベネズエラ', 'ベネズエラ・ボリバル共和国'],
	'Vietnam': ['ベトナム社会主義共和国', '越', 'ベトナム'],
	'Yemen': ['イエメン共和国', 'イエメン'],
	'Zambia': ['ザンビア', 'ザンビア共和国'],
	'Zimbabwe': ['ジンバブエ共和国', 'ジンバブエ'],
	
	# --- CSV内の表記揺れ・別名への対応 ---
	# (コード実行時に 'the United States' などが警告として検出されたため、
	#  CSV内の表記に合わせたキーを追加します)
	'the Bahamas': ['バハマ', 'バハマ国'],
	'Cape Verde': ['カーボベルデ', 'カーボベルデ共和国'],
	'the Central African Republic': ['中央アフリカ共和国', '中央アフリカ'],
	'the Comoros': ['コモロ', 'コモロ連合'],
	'the Democratic Republic of the Congo': ['コンゴ民主共和国', 'DRコンゴ'],
	'the Republic of the Congo': ['コンゴ共和国', 'コンゴ'],
	'the Czech Republic': ['チェコ', 'チェコ共和国'],
	'the Dominican Republic': ['ドミニカ共和国'],
	'The Gambia': ['ガンビア', 'ガンビア共和国'],
	'Ivory Coast': ['コートジボワール', 'コートジボワール共和国', '象牙海岸'], # Cote d'Ivoire の別名
	'the Marshall Islands': ['マーシャル諸島', 'マーシャル諸島共和国'],
	'the Federated States of Micronesia': ['ミクロネシア', 'ミクロネシア連邦'],
	'the Netherlands': ['オランダ', 'オランダ王国', '蘭'],
	'the Philippines': ['フィリピン', 'フィリピン共和国', '比'],
	'São Tomé and Príncipe': ['サントメ・プリンシペ', 'サントメ・プリンシペ民主共和国'],
	'the Solomon Islands': ['ソロモン諸島'],
	'the United Arab Emirates': ['アラブ首長国連邦', 'UAE'],
	'the United States': ['アメリカ', 'アメリカ合衆国', '米国', '米'],
	'the Vatican City': ['バチカン', 'バチカン市国']
}

# --- グローバル変数 ---
matrix = [[None for _ in range(12)] for _ in range(12)]
GEOMETRIC_NET = [
	[0, 1, 0, 0], 
	[2, 3, 5, 4], 
	[0, 6, 0, 0], 
	[0, 0, 0, 0]
]
matrix_relation = [
	[103, 100, 101, 102], 
	[200, 300, 500, 400],
	[601, 600, 603, 602], 
	[202, 402, 502, 302],
]

# %%
# --- 画像処理と初期化 ---
def initialize_matrix_with_images(image_files_dict, geometric_net, face_pixel_size=150):
	global matrix
	matrix = [[None for _ in range(12)] for _ in range(12)]
	loaded_images = {}
	for face_num, file_path in image_files_dict.items():
		try:
			img = Image.open(file_path)
			img = img.resize((face_pixel_size, face_pixel_size))
			loaded_images[face_num] = img
		except FileNotFoundError:
			print(f"エラー: 画像ファイル '{file_path}' が見つかりません。")
			return False
	for h_face in range(4):
		for w_face in range(4):
			face_num = geometric_net[h_face][w_face]
			if face_num > 0:
				face_image = loaded_images.get(face_num)
				if face_image is None: continue
				tile_size = face_pixel_size // 3
				for i in range(3):
					for j in range(3):
						tile_box = (j * tile_size, i * tile_size, (j + 1) * tile_size, (i + 1) * tile_size)
						tile_image = face_image.crop(tile_box)
						matrix[h_face * 3 + i][w_face * 3 + j] = tile_image
	print("6面の画像でMatrixを初期化しました。")
	return True

def main_initialization(di, shuffle_count=10):
	image_folder_name = "flags_easy" if di == "easy" else "flags_output" if di == "medium" else "flags_output"
	image_folder = resource_path(image_folder_name)
	try:
		all_image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
		if len(all_image_files) < 6:
			print(f"エラー: '{image_folder}' フォルダに画像が6枚以上ありません。")
			return False
		selected_files = random.sample(all_image_files, 6)
		#print("選ばれた国旗:", selected_files)
		
		country_names = [] # <-- 英語名のリスト (例: ["Japan", "USA"])
		
		for f_name in selected_files:
			clean_name = f_name.replace('_rearranged', '').rsplit('.', 1)[0]#この部分は自分の環境に基づくもの（ふつうは不要）
			clean_name = clean_name.replace('_', ' ')
			country_names.append(clean_name)
			
		flag_image_files = {
			i + 1: resource_path(os.path.join(image_folder_name, selected_files[i])) 
			for i in range(6)
		}
		if not initialize_matrix_with_images(flag_image_files, GEOMETRIC_NET, TILE_SIZE * 3): 
			return False
		
		rotate("X+", 0, 1, 1, True) 
		rotate("X-", 0, 1, 1, True) 
		shuffle_cube(shuffle_count)
		
		print("選ばれた国旗の国名:", country_names) # (確認用)
		# --- ▼ 戻り値を変更 ▼ ---
		# country_names リストを元に、COUNTRY_NAME_MAP から辞書を作成
		quiz_data = {}
		for name in country_names:
			# MAP に存在すれば日本語名のリストを、存在しなければ None を値として辞書に追加
			quiz_data[name] = COUNTRY_NAME_MAP.get(name) 
			
		print(f"クイズ用データ: {quiz_data}") # (確認用)
		print("\n")
		return quiz_data # 辞書を返す (例: {"Japan": ["日本"], "USA": ["アメリカ", "米国"]})
	except FileNotFoundError:
		print(f"エラー: '{image_folder}' という名前のフォルダが見つかりません。")
		return False

# --- 描画関連 ---
def pil_to_pygame(pil_img):
	mode, size, data = pil_img.mode, pil_img.size, pil_img.tobytes()
	return pygame.image.fromstring(data, size, mode)

def draw_grid(surface):
	surface.fill("white")
	bg_rect = (GRID_OFFSET_X, GRID_OFFSET_Y, CANVAS_SIZE_W, CANVAS_SIZE_H)
	surface.fill("lightblue", bg_rect)
	for h in range(3):
		for w in range(4):
			for i in range(3):
				for j in range(3):
					tile_image = matrix[3 * h + i][3 * w + j]
					if tile_image:
						py_image = pil_to_pygame(tile_image)
						w1 = j * TILE_SIZE + (w * TILE_SIZE * 3 + (w + 1) * MARGIN) + GRID_OFFSET_X
						h1 = i * TILE_SIZE + (h * TILE_SIZE * 3 + (h + 1) * MARGIN) + GRID_OFFSET_Y
						surface.blit(py_image, (w1, h1))
	draw_mask(surface)

def draw_mask(surface):
	for w in range(4):
		for h in range(3):
			if GEOMETRIC_NET[h][w] > 0:
				draw_geometric_net_outline(surface, h, w)
			else:
				draw_face(surface, h, w, "lightblue")

def draw_geometric_net_outline(surface, h, w):
	w1 = w * TILE_SIZE * 3 + (w + 1) * MARGIN + GRID_OFFSET_X
	h1 = h * TILE_SIZE * 3 + (h + 1) * MARGIN + GRID_OFFSET_Y
	pygame.draw.rect(surface, "black", (w1, h1, TILE_SIZE * 3, TILE_SIZE * 3), width=5)

def draw_face(surface, h, w, color):
	w1 = w * TILE_SIZE * 3 + (w + 1) * MARGIN + GRID_OFFSET_X
	h1 = h * TILE_SIZE * 3 + (h + 1) * MARGIN + GRID_OFFSET_Y
	pygame.draw.rect(surface, color, (w1, h1, TILE_SIZE * 3, TILE_SIZE * 3))

# --- キューブ操作ロジック ---
def get3x3(x, y): return [[matrix[3 * x + i][3 * y + j] for j in range(3)] for i in range(3)]
def put3x3(x, y, array):
	for i in range(3):
		for j in range(3): matrix[3 * x + i][3 * y + j] = array[i][j]

def rotate_clockwise(array):
	#面の時計回り90度回転
	rotated_array = [[None] * 3 for _ in range(3)]
	for i in range(3):
		for j in range(3):
			if array[i][j]: rotated_array[j][2 - i] = array[i][j].rotate(-90)
	return rotated_array

def rotate_tile_clockwise(tile_image):
	"""単一のPIL画像タイルを時計回り(-90度)に回転させる"""
	if tile_image:
		return tile_image.rotate(-90)
	return None

def rotate_counterclockwise(array):
	#面の反時計回り90度回転
	rotated_array = [[None] * 3 for _ in range(3)]
	for i in range(3):
		for j in range(3):
			if array[i][j]: rotated_array[2 - j][i] = array[i][j].rotate(90)
	return rotated_array

def rotate_tile_counterclockwise(tile_image):
	"""単一のPIL画像タイルを反時計回り(90度)に回転させる"""
	if tile_image:
		return tile_image.rotate(90)
	return None

def rotate(direction, index, geometry_net_x, geometry_net_y, R):
	if direction == "X+":
		margin = 3 * geometry_net_x
		temp = [matrix[margin + index][9], matrix[margin + index][10], matrix[margin + index][11]]
		for j in range(11, 2, -3):
			matrix[margin + index][j] = matrix[margin + index][j - 3]
			matrix[margin + index][j - 1] = matrix[margin + index][j - 4]
			matrix[margin + index][j - 2] = matrix[margin + index][j - 5]
		matrix[margin + index][2] = temp[2]
		matrix[margin + index][1] = temp[1]
		matrix[margin + index][0] = temp[0]
		if index == 0:
			temp0 = get3x3(0, 1)
			temp1 = rotate_counterclockwise(temp0)
			put3x3(0, 1, temp1)
		elif index == 2:
			temp0 = get3x3(2, 1)
			temp1 = rotate_clockwise(temp0)
			put3x3(2, 1, temp1)
	elif direction == "X-":
		margin = 3 * geometry_net_x
		temp = [matrix[margin + index][0], matrix[margin + index][1], matrix[margin + index][2]]
		for j in range(0, 9, 3):
			matrix[margin + index][j] = matrix[margin + index][j + 3]
			matrix[margin + index][j + 1] = matrix[margin + index][j + 4]
			matrix[margin + index][j + 2] = matrix[margin + index][j + 5]
		matrix[margin + index][9] = temp[0]
		matrix[margin + index][10] = temp[1]
		matrix[margin + index][11] = temp[2]
		if index == 0:
			temp0 = get3x3(0, 1)
			temp1 = rotate_clockwise(temp0)
			put3x3(0, 1, temp1)
		elif index == 2:
			temp0 = get3x3(2, 1)
			temp1 = rotate_counterclockwise(temp0)
			put3x3(2, 1, temp1)
	elif direction == "Y-":
		margin = 3 * geometry_net_y
		temp = [matrix[9][margin + index], matrix[10][margin + index], matrix[11][margin + index]]
		for i in range(11, 2, -3):
			matrix[i][margin + index] = matrix[i - 3][margin + index]
			matrix[i - 1][margin + index] = matrix[i - 4][margin + index]
			matrix[i - 2][margin + index] = matrix[i - 5][margin + index]
		matrix[2][margin + index] = temp[2]
		matrix[1][margin + index] = temp[1]
		matrix[0][margin + index] = temp[0]
		if index == 0:
			temp0 = get3x3(1, 0)
			temp1 = rotate_clockwise(temp0)
			put3x3(1, 0, temp1)
		elif index == 2:
			temp0 = get3x3(1, 2)
			temp1 = rotate_counterclockwise(temp0)
			put3x3(1, 2, temp1)
	elif direction == "Y+":
		margin = 3 * geometry_net_y #2+のとき＝３,index=2
		temp = [matrix[0][margin + index], matrix[1][margin + index], matrix[2][margin + index]]
		for i in range(0, 9, 3):
			matrix[i][margin + index] = matrix[i + 3][margin + index]
			matrix[i + 1][margin + index] = matrix[i + 4][margin + index]
			matrix[i + 2][margin + index] = matrix[i + 5][margin + index]
		
		matrix[9][margin + index] = temp[0]
		matrix[10][margin + index] = temp[1]
		matrix[11][margin + index] = temp[2] 
		if index == 0:
			temp0 = get3x3(1, 0)
			temp1 = rotate_counterclockwise(temp0)
			put3x3(1, 0, temp1)
		elif index == 2:
			temp0 = get3x3(1, 2)
			temp1 = rotate_clockwise(temp0)
			put3x3(1, 2, temp1)
	elif direction == "Z+":
		temp = [matrix[index][3], matrix[index][4], matrix[index][5]]
		
		# 面1 (上辺) <-- 面2 (左辺)
		matrix[index][3] = rotate_tile_clockwise(matrix[5][index]) # 向きも変える
		matrix[index][4] = rotate_tile_clockwise(matrix[4][index])
		matrix[index][5] = rotate_tile_clockwise(matrix[3][index])
		
		# 面2 (左辺) <-- 面6 (下辺)
		matrix[3][index] = rotate_tile_clockwise(matrix[8 - index][3])
		matrix[4][index] = rotate_tile_clockwise(matrix[8 - index][4])
		matrix[5][index] = rotate_tile_clockwise(matrix[8 - index][5])

		# 面6 (下辺) <-- 面4 (右辺)
		matrix[8 - index][3] = rotate_tile_clockwise(matrix[5][8 - index])
		matrix[8 - index][4] = rotate_tile_clockwise(matrix[4][8 - index])
		matrix[8 - index][5] = rotate_tile_clockwise(matrix[3][8 - index])

		# 面4 (右辺) <-- temp (面1)
		matrix[3][8 - index] = rotate_tile_clockwise(temp[0])
		matrix[4][8 - index] = rotate_tile_clockwise(temp[1])
		matrix[5][8 - index] = rotate_tile_clockwise(temp[2])	
		if index == 0:
			temp0 = get3x3(1, 3)
			temp1 = rotate_counterclockwise(temp0)
			put3x3(1, 3, temp1)
		elif index == 2:
			temp0 = get3x3(1, 1)
			temp1 = rotate_clockwise(temp0)
			put3x3(1, 1, temp1)
	elif direction == "Z-":
		temp = [matrix[index][3], matrix[index][4], matrix[index][5]]
		# 面1 (上辺) <-- 面4 (右辺)
		# (タイルの向きも時計回りに回転)
		matrix[index][3] = rotate_tile_counterclockwise(matrix[3][8 - index])
		matrix[index][4] = rotate_tile_counterclockwise(matrix[4][8 - index])
		matrix[index][5] = rotate_tile_counterclockwise(matrix[5][8 - index])
		
		# 面4 (右辺) <-- 面6 (下辺)
		matrix[3][8 - index] = rotate_tile_counterclockwise(matrix[8 - index][3])
		matrix[4][8 - index] = rotate_tile_counterclockwise(matrix[8 - index][4])
		matrix[5][8 - index] = rotate_tile_counterclockwise(matrix[8 - index][5])

		# 面6 (下辺) <-- 面2 (左辺)
		matrix[8 - index][3] = rotate_tile_counterclockwise(matrix[3][index])
		matrix[8 - index][4] = rotate_tile_counterclockwise(matrix[4][index])
		matrix[8 - index][5] = rotate_tile_counterclockwise(matrix[5][index])
		
		# 面2 (左辺) <-- temp (面1)
		matrix[3][index] = rotate_tile_counterclockwise(temp[0])
		matrix[4][index] = rotate_tile_counterclockwise(temp[1])
		matrix[5][index] = rotate_tile_counterclockwise(temp[2])
		if index == 0:
			temp0 = get3x3(1, 3)
			temp1 = rotate_clockwise(temp0)
			put3x3(1, 3, temp1)
		elif index == 2:
			temp0 = get3x3(1, 1)
			temp1 = rotate_counterclockwise(temp0)
			put3x3(1, 1, temp1)


	if direction == "X+" or direction == "X-":
		for j in range(4):
			consistency1(geometry_net_x, j)
	elif direction == "Y-" or direction == "Y+":
		for i in range(4):
			consistency1(i, geometry_net_y)
	elif direction == "Z+" or direction == "Z-":
		consistency1(0, 1)
		consistency1(1, 0)
		consistency1(2, 1)
		consistency1(1, 2)
		consistency1(1, 3)
		consistency1(1, 1)

	if R: return # RがTrue(silent)なら画面更新しない



def consistency0():
	for i in range(4):
		for j in range(4):
			if GEOMETRIC_NET[i][j] > 0:
				consistency1(i, j)

def consistency1(x, y):
	k = matrix_relation[x][y]
	for i in range(4):
		for j in range(4):
			if math.floor(k / 100) == math.floor(matrix_relation[i][j] / 100):
				consistency2(x, y, i, j, matrix_relation[i][j] - k)

def consistency2(x1, y1, x2, y2, rotate):
	base_array = get3x3(x1, y1)
	if rotate < 0: rotate += 4
	
	rotated_array = base_array
	if rotate == 1: rotated_array = rotate_clockwise(base_array)
	elif rotate == 2: rotated_array = rotate_clockwise(rotate_clockwise(base_array))
	elif rotate == 3: rotated_array = rotate_counterclockwise(base_array)
	
	put3x3(x2, y2, rotated_array)

def shuffle_cube(num_rotations):
	directions = ["X+", "X-", "Y+", "Y-", "Z+", "Z-"]
	for _ in range(num_rotations):
		direction = random.choice(directions)
		index = random.choice([0, 1, 2])
		print(f"回転: {direction}, インデックス: {index}")
		if direction.startswith("Z"): rotate(direction, index, 0, 1, True)
		else: rotate(direction, index, 1, 1, True)

# %%
class RubikGame:
	"""ルービックキューブゲームのメインクラス"""

	def __init__(self, difficulty, screen_surface):
		self.difficulty = difficulty
		self.screen = screen_surface
		
		#画面サイズを動的に取得
		self.screen_info = pygame.display.Info()
		self.SCREEN_W = self.screen_info.current_w
		self.SCREEN_H = self.screen_info.current_h
		
		#UIManager にも動的なサイズを渡す
		self.manager = pygame_gui.UIManager((self.SCREEN_W, self.SCREEN_H), resource_path('theme.json'), starting_language ='ja') # <-- 修正
		self.manager.get_theme().load_theme(resource_path('quiz_theme.json')) # <-- 修正
		self.running = True
		self.shuffle_count = 5 if difficulty == "easy" else 5 if difficulty == "medium" else 10
		
		# 難易度に応じて必要な正解数を設定
		if self.difficulty == 'easy':
			self.required_answers = 3
		elif self.difficulty == 'medium':
			self.required_answers = 3
		else: # hard
			self.required_answers = 6
		
		# QuizManagerのインスタンスを保持
		self.quiz_manager = None
		
		self._create_buttons() # __init__ の最後で呼ぶ

	def _create_buttons(self):
		btn_w, btn_h = 40, 30
		actions = {"X+": (1,1), "X-": (1,1), "Y+": (1,1), "Y-": (1,1), "Z+": (0,1), "Z-": (0,1)}
		positions = {
			"X+": (CANVAS_SIZE_W + TILE_SIZE*2.5, TILE_SIZE*4 + MARGIN*2), "X-": (TILE_SIZE*0.5, TILE_SIZE*4 + MARGIN*2),
			"Y+": (TILE_SIZE*5 + MARGIN*2.5, TILE_SIZE*0.2), "Y-": (TILE_SIZE*5 + MARGIN*2.5, CANVAS_SIZE_H + TILE_SIZE*1.5),
			"Z+": (CANVAS_SIZE_W + TILE_SIZE*2.5, TILE_SIZE*1 + MARGIN*1), "Z-": (TILE_SIZE*0.5, TILE_SIZE*1 + MARGIN*1)
		}
		for axis_dir, (gx, gy) in actions.items():
			for i in range(3):
				pos_x, pos_y = positions[axis_dir]
				if axis_dir.startswith("X"): pos_y += TILE_SIZE * i
				elif axis_dir.startswith("Y"): pos_x += TILE_SIZE * i
				elif axis_dir.startswith("Z"): pos_y += (TILE_SIZE+MARGIN/3) * i
				pygame_gui.elements.UIButton(
					relative_rect=pygame.Rect((pos_x, pos_y), (btn_w, btn_h)),
					text=f'{axis_dir[0]}{i}{axis_dir[1]}', manager=self.manager,
					object_id=pygame_gui.core.ObjectID(class_id='@rotate_button', object_id=f'#rotate_{axis_dir}_{i}')
				)
		
		# キャンバスの右端 (ライトブルーの領域の右端)
		canvas_right_edge = GRID_OFFSET_X + CANVAS_SIZE_W 

		#クイズボタンのサイズと位置
		btn_w_quiz, btn_h_quiz = 150, 60 
		
		# 右側余白の中央あたりに配置
		pos_x_quiz = canvas_right_edge + (self.SCREEN_W - canvas_right_edge - btn_w_quiz) // 2
		pos_y_quiz = (self.SCREEN_H - btn_h_quiz) // 2 # 画面の縦中央
		
		pygame_gui.elements.UIButton(
			relative_rect=pygame.Rect((pos_x_quiz, pos_y_quiz), (btn_w_quiz, btn_h_quiz)), 
			text='クイズ', 
			manager=self.manager, 
			object_id=pygame_gui.core.ObjectID(class_id='@game_button', object_id='#quiz_button')
		)

		#戻るボタンのサイズ 
		btn_w_long, btn_h_long = 100, 40
		pygame_gui.elements.UIButton(
			relative_rect=pygame.Rect((TILE_SIZE * 3, CANVAS_SIZE_H + TILE_SIZE * 1.5), (btn_w_long, btn_h_long)), 
			text='戻る', 
			manager=self.manager, 
			object_id=pygame_gui.core.ObjectID(class_id='@game_button', object_id='#back_button')
		)

		pygame_gui.elements.UIButton(
			relative_rect=pygame.Rect((pos_x_quiz + TILE_SIZE * 3, pos_y_quiz), (btn_w_quiz, btn_h_quiz)), 
			text='正解を見る', 
			manager=self.manager, 
			object_id=pygame_gui.core.ObjectID(class_id='@game_button', object_id='#answer_button')
		)
		#注意文のテキストボックス
		# 位置決め (右側余白の上部)
		text_box_start_x = canvas_right_edge + TILE_SIZE * 2
		text_box_start_y = GRID_OFFSET_Y + 20
		
		# 幅と高さを計算 (クイズボタンの上に来るように)
		text_box_width = self.SCREEN_W - text_box_start_x - 20 # 右に20pxマージン
		text_box_height = pos_y_quiz - text_box_start_y - 20 # クイズボタンの 20px 上まで
		
		if text_box_height < 100: # 高さが足りない場合 (低解像度など)
			text_box_height = 200 # 最小の高さを確保

		# 難易度に応じたテキスト (self.required_answers を参照)
		if self.difficulty == 'hard':
			quiz_rule_text = "・Hardモード: 全問正解でクリア"
		elif self.difficulty == 'medium':
			quiz_rule_text = f"Mediumモード: {self.required_answers}問正解でクリア"
		else: # easy
			quiz_rule_text = f"Easyモード: {self.required_answers}問正解でクリア"


		warning_html_text = (
			f"<b><font color='#FF0000'>注意 (難易度: {self.difficulty}):</font></b><br><br>"
			f"{quiz_rule_text}<br><br>"
			"・クイズ中にルービックキューブを操作しても、クイズの進行には影響しません。<br>"
			"・回転ボタンを連打すると動作が停止することがあるので注意してください。<br>"
			"・日本語(カタカナ、漢字)もしくは英語で回答してください。<br>"
			"・pygame_guiの仕様上、変換してenterキー押下まで日本語入力は表示されません。あらかじめ、ご了承ください。<br>"
			"・国名の別名や略称も一部認識しますが、全ての別名に対応しているわけではありません。<br>"
		)
		
		pygame_gui.elements.UITextBox(
			html_text=warning_html_text,
			relative_rect=pygame.Rect((text_box_start_x, text_box_start_y), (text_box_width, text_box_height)),
			manager=self.manager,
			object_id=pygame_gui.core.ObjectID(class_id='@warning_text') # テーマで @warning_text を指定可能
		)
	# rubik_gui.py の RubikGame クラス内

	def run(self):
		# ゲームの初期化 (main_initialization は辞書を返すようになる)
		country_data = main_initialization(di=self.difficulty, shuffle_count=self.shuffle_count)
		if not country_data:
			print("初期化に失敗したため、ゲームを開始できません。")
			return

		self.country_data = country_data # 正解表示用に保持
		self.answer_window = None       # 正解表示ウィンドウの参照

		# QuizManagerを初期化
		self.quiz_manager = QuizManager(
			manager=self.manager, 
			screen_rect=self.screen.get_rect(),
			required_answers=self.required_answers, 
			country_data=country_data   
		)

		clock = pygame.time.Clock()
		self.running = True
		while self.running:
			time_delta = clock.tick(60) / 1000.0
			for event in pygame.event.get():
				if event.type == pygame.QUIT: return "QUIT_PROGRAM"
				
				
				self.manager.process_events(event)
				

				if event.type == pygame_gui.UI_BUTTON_PRESSED:
					
					obj_id_str = str(event.ui_object_id)

					# 2a. 「正解」ウィンドウのOKボタン (「解散」ボタン)
					if self.answer_window and obj_id_str == '#answer_message_window.#ok_button':
						self.running = False 
						self.answer_window = None # 参照のみクリア
					
					# 2b. 戻るボタン
					elif obj_id_str.endswith('#back_button'): 
						self.running = False
					
					# 2c. クイズボタン
					elif obj_id_str.endswith('#quiz_button'):
						if self.quiz_manager:
							self.quiz_manager.create_window()
					
					# 2d. 正解ボタン (変更なし)
					elif obj_id_str.endswith('#answer_button'):
						if self.country_data and not self.answer_window:
							answer_names = []
							for key, aliases in self.country_data.items():
								if aliases: 
									answer_names.append(aliases[0]) 
								else: 
									answer_names.append(key) 
							
							answer_html = "<b>正解の国名:</b><br><br>" + "<br>".join(answer_names)
							
							msg_width, msg_height = 400, 350
							msg_rect = pygame.Rect(0, 0, msg_width, msg_height)
							msg_rect.center = self.screen.get_rect().center

							self.answer_window = pygame_gui.windows.UIMessageWindow(
								rect=msg_rect,
								html_message=answer_html,
								manager=self.manager,
								window_title='正解',
								object_id='#answer_message_window',
							)
					
					# 2e. 回転ボタン (変更なし)
					elif '#rotate_' in obj_id_str:
						try:
							parts = obj_id_str.split('_'); direction, index = parts[-2], int(parts[-1])
							gx, gy = (0,1) if direction[0] == 'Z' else (1,1)
							rotate(direction, index, gx, gy, False)
						except (ValueError, IndexError):
							pass 
				
				# 3. (後で) QuizManager 側のイベント処理 (変更なし)
				if self.quiz_manager:
					self.quiz_manager.process_event(event) 
				

				# 4. ×ボタン (UI_WINDOW_CLOSE) の処理
				if event.type == pygame_gui.UI_WINDOW_CLOSE:
					
					# 閉じたのが「正解表示ウィンドウ」か確認
					if self.answer_window and event.ui_element == self.answer_window:
						self.running = False 
						self.answer_window = None # 参照のみクリア
					
				


			self.manager.update(time_delta)
			draw_grid(self.screen)
			self.manager.draw_ui(self.screen)
			pygame.display.flip()

