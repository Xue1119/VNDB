import requests

# 替换为你的VNDB API令牌
api_token = '***************'

# API基础URL
api_base_url = 'https://api.vndb.org/kana/vn'

# 示例中文游戏名列表
game_names = [
    '****','****','***','****','*****'
]

# 搜索并获取游戏ID，并将结果写入txt文件
def search_vn_by_name(name, result_file, no_result_file):
    response = requests.post(
        api_base_url,
        headers={'Authorization': f'Token {api_token}', 'Content-Type': 'application/json'},
        json={
            "filters": ["search", "=", name],
            "fields": "id, title"
        }
    )
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            with open(result_file, 'a', encoding='utf-8') as f:
                for vn in results:
                    print(f"ID: {vn['id']}, Title: {vn['title']}")
                    f.write(f"ID: {vn['id']}, Title: {vn['title']}\n")
        else:
            print(f"No results found for: {name}")
            with open(no_result_file, 'a', encoding='utf-8') as f:
                f.write(f"No results found for: {name}\n")
    else:
        print(f"Failed to search for: {name}, Status Code: {response.status_code}, Response Text: {response.text}")

# 输出文件名
output_file = 'search_results.txt'
no_result_file = 'no_results.txt'


# 批量搜索并将结果写入文件
for game_name in game_names:
    search_vn_by_name(game_name, output_file,no_result_file)
