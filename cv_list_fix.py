import requests
import json
import time

# 替换为你的VNDB API令牌
api_token = '***************'
api_base_url_vn = 'https://api.vndb.org/kana/vn'
api_base_url_staff = 'https://api.vndb.org/kana/staff'




# 获取staff original name
def get_staff_name(staff_id):
    response = requests.post(
        api_base_url_staff,
        headers={'Authorization': f'Token {api_token}', 'Content-Type': 'application/json'},
        json={
            "filters": ["id", "=", staff_id],
            "fields": "original, name"
        }
    )
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0].get('original', results[0].get('name', 'N/A'))
    return 'N/A'

# 获取vn title
def get_vn_title(vn_id, vn_cache):
    if vn_id in vn_cache:
        return vn_cache[vn_id]

    retry_count = 3
    for _ in range(retry_count):
        response = requests.post(
            api_base_url_vn,
            headers={'Authorization': f'Token {api_token}', 'Content-Type': 'application/json'},
            json={
                "filters": ["id", "=", vn_id],
                "fields": "alttitle, title"
            }
        )
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                alt_title = results[0].get('alttitle', '')
                title = results[0].get('title', 'N/A')
                vn_title = alt_title if alt_title else title
                vn_cache[vn_id] = vn_title
                return vn_title
        elif response.status_code == 500:  # Internal Server Error, retry
            continue
        else:
            break
    return 'N/A'


# 读取并修复cv_list.txt文件
def read_and_fix_cv_list(filename):
    vn_cache = {}
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        if "VN Title: None" in line:
            vn_id = line.split("VN ID:")[1].split(",")[0].strip()
            vn_title = get_vn_title(vn_id, vn_cache)
            updated_line = line.replace("VN Title: None", f"VN Title: {vn_title}")
            updated_lines.append(updated_line)
            print(f"Updated VN ID: v{vn_id} with title: {vn_title}")
        elif "VN Title: N/A" in line:
            vn_id = line.split("VN ID:")[1].split(",")[0].strip()
            vn_title = get_vn_title(vn_id, vn_cache)
            updated_line = line.replace("VN Title: N/A", f"VN Title: {vn_title}")
            updated_lines.append(updated_line)
            print(f"Updated VN ID: v{vn_id} with title: {vn_title}")
        elif "Name: N/A" in line:
            staff_id = line.split("Staff ID:")[1].split(",")[0].strip()
            staff_name = get_staff_name(staff_id)
            updated_line = line.replace("Name: N/A", f"Name: {staff_name}")
            updated_lines.append(updated_line)
            print(f"Updated Staff ID: s{staff_id} with name: {staff_name}")
        else:
            updated_lines.append(line)

    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

def main():
    read_and_fix_cv_list('cv_list.txt')

main()
