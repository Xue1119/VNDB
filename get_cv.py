import requests
import time

# 替换为你的VNDB API令牌
api_token = '**********'

# API基础URL
api_base_url_vn = 'https://api.vndb.org/kana/vn'

# 读取 get_list.txt 文件并提取 ID
def read_vn_ids(file_path):
    vn_ids = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("ID: v"):
                vn_id = line.split(",")[0].split(":")[1].strip()[1:]  # 去除前缀 'v'
                vn_ids.append(vn_id)
    return vn_ids

# 获取 VN 的信息
def get_vn_info(vn_id, vn_cache):
    if vn_id in vn_cache:
        return vn_cache[vn_id]

    retry_count = 10
    for _ in range(retry_count):
        response = requests.post(
            api_base_url_vn,
            headers={'Authorization': f'Token {api_token}', 'Content-Type': 'application/json'},
            json={
                "filters": ["id", "=", vn_id],
                "fields": "va.staff.original,va.character.original,alttitle,title"
            }
        )
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                vn_info = results[0]
                va_info = vn_info.get('va', [])
                alt_title = vn_info.get('alttitle', '')
                title = vn_info.get('title', 'N/A')
                vn_title = alt_title if alt_title else title
                
                staff_dict = {}
                
                for va in va_info:
                    staff_id = va.get('staff', {}).get('id', 'N/A')
                    staff_name = va.get('staff', {}).get('original', 'N/A')
                    character_id = va.get('character', {}).get('id', 'N/A')
                    character_name = va.get('character', {}).get('original', 'N/A')
                    
                    if staff_id not in staff_dict:
                        staff_dict[staff_id] = {
                            'name': staff_name,
                            'characters': []
                        }
                    
                    staff_dict[staff_id]['characters'].append({
                        'id': character_id,
                        'name': character_name,
                        'vn_id': vn_id,
                        'vn_title': vn_title
                    })
                
                vn_cache[vn_id] = staff_dict
                return staff_dict
        elif response.status_code == 500:  # Internal Server Error, retry
            time.sleep(1)
            continue
        else:
            break
    return {}

# 批量获取 VN 信息并输出到文件
def main():
    vn_ids = read_vn_ids('get_list.txt')
    vn_cache = {}
    all_staff_dict = {}

    print(f"Total VN IDs: {len(vn_ids)}")

    for i, vn_id in enumerate(vn_ids):
        print(f"Processing VN {i + 1}/{len(vn_ids)}: v{vn_id}")
        staff_dict = get_vn_info(vn_id, vn_cache)
        
        for staff_id, staff_info in staff_dict.items():
            if staff_id not in all_staff_dict:
                all_staff_dict[staff_id] = {
                    'name': staff_info['name'],
                    'characters': []
                }
            all_staff_dict[staff_id]['characters'].extend(staff_info['characters'])

    # 输出到 cv_list.txt 文件
    with open('cv_list.txt', 'w', encoding='utf-8') as file:
        for staff_id, staff_info in all_staff_dict.items():
            file.write(f"Staff ID: {staff_id}, Name: {staff_info['name']}\n")
            for character in staff_info['characters']:
                file.write(f"    Character ID: {character['id']}, Name: {character['name']}, VN ID: {character['vn_id']}, VN Title: {character['vn_title']}\n")


main()
