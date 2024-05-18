import socket
import json
import base64
import time

# 配置信息 替换为你的账号密码
username = '****'
password = '*****'
client_name = 'Client'
client_version = '1.0'


# 读取 get_list.txt 文件并提取 ID
def read_vn_ids(file_path):
    vn_ids = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("ID: v"):
                vn_id = line.split(",")[0].split(":")[1].strip()[1:]  # 去除前缀 'v'
                vn_ids.append(vn_id)
    return vn_ids

# VN IDs 列表
vn_ids = read_vn_ids('get_list.txt')



def login_to_vndb():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('api.vndb.org', 19534))

    login_request = {
        "protocol": 1,
        "client": client_name,
        "clientver": client_version,
        "username": username,
        "password": password
    }
    s.sendall(f"login {json.dumps(login_request)}\x04".encode())
    response = s.recv(4096).decode('utf-8')
    if 'ok' in response:
        print("登录成功！")
        return s
    else:
        print("登录失败。")
        s.close()
        return None

def get_characters(s, vn_id):
    get_request = {
        "type": "character",
        "flags": "basic,details,vns,voiced",
        "filters": f"(vn = {vn_id})"
    }
    s.sendall(f"get character {get_request['flags']} {get_request['filters']}\x04".encode())

    complete_response = ""
    while True:
        part = s.recv(4096).decode('latin-1', errors='ignore')
        complete_response += part
        if '\x04' in part:
            break

    complete_response = complete_response.replace('\x04', '')
    response_data = json.loads(complete_response.split(' ', 1)[1].strip().encode('latin-1').decode('utf-8'))
    return response_data.get('items', [])


def main():
    s = login_to_vndb()
    if s is None:
        return

    cv_dict = {}
    failed_vns = []
    count = 1
    for vn_id in vn_ids:
        success = False
        for attempt in range(10):  # 尝试最多10次
            try:
                characters = get_characters(s, vn_id)
                if characters:
                    success = True
                    break
                print(f"Retrying for VN ID: {vn_id} (Attempt {attempt + 1}/10)")
                time.sleep(2)  # 每次尝试之间添加2秒延迟
            except Exception as e:
                print(f"Error retrieving characters for VN ID: {vn_id}, Error: {e}")

        if not success:
            failed_vns.append(vn_id)
            continue
        print(count)
        print(characters)
        count += 1
        for character in characters:
            character_id = character.get('id', 'N/A')
            character_name = character.get('original', 'N/A')
            voiced_list = character.get('voiced', [])
            for voiced in voiced_list:
                staff_id = voiced.get('id', 'N/A')
                if staff_id not in cv_dict:
                    cv_dict[staff_id] = {"name": "N/A", "roles": []}
                if not any(role['Character ID'] == character_id for role in cv_dict[staff_id]["roles"]):
                    cv_dict[staff_id]["roles"].append({
                        "Character ID": character_id,
                        "Name": character_name,
                        "VN ID": vn_id
                    })


    # 打印并写入CV配音的角色信息
    with open('cv_count.txt', 'w', encoding='utf-8') as f:
        for staff_id, data in cv_dict.items():
            print(f"Staff ID: {staff_id}")
            f.write(f"Staff ID: {staff_id}\n")
            for role in data["roles"]:
                print(f"    Character ID: {role['Character ID']}, Name: {role['Name']}, VN ID: {role['VN ID']}")
                f.write(f"    Character ID: {role['Character ID']}, Name: {role['Name']}, VN ID: {role['VN ID']}\n")


    s.sendall("logout\x04".encode())
    s.close()

main()
