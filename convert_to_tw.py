import os
import opencc

# 注意：此處不要加 .json，傳入 's2twp' 即可 (簡體 -> 臺灣繁體，含慣用語轉換)
# 若只需字形純簡轉繁、不轉換臺灣詞彙，可改為 's2t'
converter = opencc.OpenCC('s2twp')

# 欲掃描轉換的副檔名
TARGET_EXTENSIONS = {'.html', '.js', '.json', '.geojson', '.md'}

# 排除不需要處理的目錄或檔案
EXCLUDE_DIRS = {'.git', 'node_modules', '.vscode'}
EXCLUDE_FILES = {'convert_to_tw.py', 'package-lock.json'}

def convert_project(root_path):
    count = 0
    for root, dirs, files in os.walk(root_path):
        # 過濾排除目錄
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file in EXCLUDE_FILES:
                continue
            
            ext = os.path.splitext(file)[1].lower()
            if ext in TARGET_EXTENSIONS:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    converted = converter.convert(content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(converted)
                    
                    print(f"已轉換: {file_path}")
                    count += 1
                except UnicodeDecodeError:
                    print(f"略過非 UTF-8 檔案: {file_path}")
                except Exception as e:
                    print(f"處理失敗 {file_path}: {e}")
                    
    print(f"\n全部完成！共轉換 {count} 個檔案。")

if __name__ == '__main__':
    convert_project('.')