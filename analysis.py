import re
from collections import defaultdict

def read_cv_list(file_path):
    cv_dict = defaultdict(lambda: {'name': '', 'characters': {}})
    
    with open(file_path, 'r', encoding='utf-8') as file:
        current_cv = None
        for line in file:
            line = line.strip()
            if line.startswith("Staff ID:"):
                match = re.match(r"Staff ID: s(\d+), Name: (.+)", line)
                if match:
                    current_cv = match.group(1)
                    cv_dict[current_cv]['name'] = match.group(2)
            elif line.startswith("Character ID:") and current_cv:
                match = re.match(r"Character ID: c(\d+), Name: (.+), VN ID: (\d+), VN Title: (.+)", line)
                if match:
                    character_id = match.group(1)
                    character_info = (
                        match.group(1),  # character_id
                        match.group(2),  # character_name
                        match.group(3),  # vn_id
                        match.group(4)   # vn_title
                    )
                    cv_dict[current_cv]['characters'][character_id] = character_info
                else:
                    print(f"Line did not match character pattern: {line}")
    
    return cv_dict

def analyze_cv_data(cv_dict):
    total_cvs = len(cv_dict)
    total_characters = sum(len(cv['characters']) for cv in cv_dict.values())
    cv_4plus = {cv_id: cv for cv_id, cv in cv_dict.items() if len(cv['characters']) >= 4}
    sorted_cv_4plus = sorted(cv_4plus.items(), key=lambda item: len(item[1]['characters']), reverse=True)
    
    print(f"总共出现 {total_cvs} 个CV")
    print(f"总共出现 {total_characters} 个角色")
    print(f"出现过4次及以上的CV有 {len(cv_4plus)} 个")
    
    for cv_id, cv in sorted_cv_4plus:
        print(f"Staff ID: s{cv_id}, Name: {cv['name']}, 出现次数: {len(cv['characters'])}")
        for character_id, character in cv['characters'].items():
            print(f"    Character ID: c{character[0]}, Name: {character[1]}, VN ID: {character[2]}, VN Title: {character[3]}")

def write_deduplicated_cv_list(file_path, cv_dict):
    with open(file_path, 'w', encoding='utf-8') as file:
        for cv_id, cv in cv_dict.items():
            file.write(f"Staff ID: s{cv_id}, Name: {cv['name']}\n")
            for character_id, character in cv['characters'].items():
                if len(character) < 4:
                    print(f"Character info has missing parts: {character}")
                else:
                    file.write(f"    Character ID: c{character[0]}, Name: {character[1]}, VN ID: {character[2]}, VN Title: {character[3]}\n")

def main():
    cv_dict = read_cv_list('cv_list.txt')
    write_deduplicated_cv_list('cv_list_deduplicated.txt', cv_dict)
    analyze_cv_data(cv_dict)

main()
