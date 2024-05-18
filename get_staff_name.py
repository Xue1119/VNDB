import requests
import json

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
            original = results[0].get('original', '')
            name = results[0].get('name', 'N/A')
            cv_name = original if original else name
            return cv_name
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

# 从文件读取cv字典
def read_cv_file(filename):
    cv_dict = {}
    with open(filename, 'r', encoding='utf-8') as f:
        current_staff_id = None
        for line in f:
            line = line.strip()
            if line.startswith("Staff ID:"):
                current_staff_id = line.split(":")[1].strip()
                cv_dict[current_staff_id] = {'name': '', 'roles': []}
            elif line.startswith("Character ID:") and current_staff_id:
                parts = line.split(',')
                char_id = parts[0].split(':')[1].strip()
                char_name = parts[1].split(':')[1].strip()
                vn_id = parts[2].split(':')[1].strip()
                cv_dict[current_staff_id]['roles'].append({'char_id': char_id, 'char_name': char_name, 'vn_id': vn_id})
    return cv_dict

def main():
    cv_dict = read_cv_file('cv_count.txt')
    vn_cache = {}
    failed_vn_ids = []
    count = 1
    for staff_id in cv_dict:
        print(count)
        count += 1
        # 查询并更新CV名字
        cv_name = get_staff_name(staff_id)
        cv_dict[staff_id]['name'] = cv_name
        
        # 查询并更新角色信息
        for role in cv_dict[staff_id]['roles']:
            vn_id = role['vn_id']
            vn_title = get_vn_title(vn_id, vn_cache)
            if vn_title == 'N/A':
                failed_vn_ids.append(vn_id)
            role['vn_title'] = vn_title
    
    # 打印并保存结果
    with open('cv_list.txt', 'w', encoding='utf-8') as f:
        for staff_id, info in cv_dict.items():
            f.write(f"Staff ID: {staff_id}, Name: {info['name']}\n")
            for role in info['roles']:
                f.write(f"    Character ID: {role['char_id']}, Name: {role['char_name']}, VN ID: {role['vn_id']}, VN Title: {role.get('vn_title', 'N/A')}\n")
    
    # 打印失败的vn_id
    with open('failed_vn_ids.txt', 'w', encoding='utf-8') as f:
        for vn_id in failed_vn_ids:
            f.write(f"{vn_id}\n")
            print(f"Failed VN ID: {vn_id}")


main()
