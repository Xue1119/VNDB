import requests

# 替换为你的VNDB API令牌和用户ID
api_token = '***************'
user_id = 'u*****'

# API基础URL
api_base_url = 'https://api.vndb.org/kana/ulist'

# 构建请求体
def get_payload(page):
    return {
        "user": user_id,
        "fields": "id, vote,vn.title",
        "results": 100,
        "page": page
    }


# 处理响应
def handle_response(response):
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Failed to fetch list: Status Code: {response.status_code}, Response Text: {response.text}")
        return []

# 获取全部列表
all_vns = []
page = 1
while True:
    payload = get_payload(page)
    response = requests.post(
        api_base_url,
        headers={'Authorization': f'Token {api_token}', 'Content-Type': 'application/json'},
        json=payload
    )
    vn_list = handle_response(response)
    if not vn_list:
        break
    all_vns.extend(vn_list)
    page += 1
    if len(vn_list) < 100:
        break

# 输出文件名
output_file = 'get_list.txt'

# 写入文件
with open(output_file, 'w', encoding='utf-8') as f:
    for vn in all_vns:
        vn_id = vn.get('id', 'N/A')
        vn_vote = vn.get('vote', 'N/A')
        vn_data = vn.get('vn', {})
        vn_title = vn_data.get('title', 'N/A')
        f.write(f"ID: {vn_id}, Vote: {vn_vote}, Title: {vn_title}\n")
