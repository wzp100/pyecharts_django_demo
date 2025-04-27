import os, time, json

def get_data_file_path(filename: str) -> str:
    """获取 data/ 目录下的完整路径，按需创建目录。"""
    from django.conf import settings
    data_dir = os.path.join(settings.BASE_DIR, 'demo', 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename)

def save_data_to_json(data, filename: str) -> str:
    """将数据写入 JSON 并返回文件路径。"""
    file_path = get_data_file_path(filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return file_path

def load_data_from_json(filename: str, max_age_hours: int = 24):
    """若文件不存在或超过 max_age_hours 过期，则返回 None。"""
    path = get_data_file_path(filename)
    if not os.path.exists(path):
        return None
    if time.time() - os.path.getmtime(path) > max_age_hours * 3600:
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
