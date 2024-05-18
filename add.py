import requests
import re

# 替换为你的VNDB API令牌
api_token = '*****************'

# API基础URL
api_base_url = 'https://api.vndb.org/kana'

# 读取游戏ID文件
def extract_game_ids(file_path):
    game_ids = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.search(r'ID:\s*(v\d+)', line)
            if match:
                game_ids.append(match.group(1))
    return game_ids

game_ids = extract_game_ids('search_results.txt')

# 添加或更新游戏到列表的API URL
for game_id in game_ids:
    add_game_url = f'{api_base_url}/ulist/{game_id}'
    response = requests.patch(
        add_game_url,
        headers={'Authorization': f'Token {api_token}'},
        json={
            'labels_set': [2],  # 设置标签，例如 "finish"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    if response.status_code == 204:
        print(f'Successfully added or updated game {game_id} to your list.')
    else:
        print(f'Failed to add or update game {game_id}: {response.status_code}, {response.text}')
