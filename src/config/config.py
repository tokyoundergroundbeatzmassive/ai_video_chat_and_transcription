import os

# プロジェクトのルートディレクトリを取得
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP_DIR = os.path.join(BASE_DIR, "tmp")