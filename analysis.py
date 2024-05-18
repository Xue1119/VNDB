import re
from collections import defaultdict

def read_cv_list(file_path):
    cv_dict = defaultdict(lambda: {'name': '', 'characters': []})
    
    with open(file_path, 'r', encoding='utf-8') as file:
        current_cv = None
        for line in file:
            line = line.strip()
            if line.startswith("Staff ID:"):
                match = re.match(r"Staff ID: (\d+), Name: (.+)", line)
                if match:
                    current_cv = match.group(1)
                    cv_dict[current_cv]['name'] = match.group(2)
            elif line.startswith("Character ID:") and current_cv:
                match = re.match(r"Character ID: (\d+), Name: (.+), VN ID: (\d+), VN Title: (.+)", line)
                if match:
                    character_info = {
                        'character_id': match.group(1),
                        'character_name': match.group(2),
                        'vn_id': match.group(3),
                        'vn_title': match.group(4)
                    }
                    cv_dict[current_cv]['characters'].append(character_info)
    
    return cv_dict

def analyze_cv_data(cv_dict):
    total_cvs = len(cv_dict)
    total_characters = sum(len(cv['characters']) for cv in cv_dict.values())
    cv_10plus = {cv_id: cv for cv_id, cv in cv_dict.items() if len(cv['characters']) >= 10}
    sorted_cv_10plus = sorted(cv_10plus.items(), key=lambda item: len(item[1]['characters']), reverse=True)
    
    print(f"总共出现 {total_cvs} 个CV")
    print(f"总共出现 {total_characters} 个角色")
    print(f"出现过10次及以上的CV有 {len(cv_10plus)} 个")
    
    for cv_id, cv in sorted_cv_10plus:
        print(f"Staff ID: {cv_id}, Name: {cv['name']}, 出现次数: {len(cv['characters'])}")
        for character in cv['characters']:
            print(f"    Character ID: {character['character_id']}, Name: {character['character_name']}, VN ID: {character['vn_id']}, VN Title: {character['vn_title']}")

def main():
    cv_dict = read_cv_list('cv_list.txt')
    analyze_cv_data(cv_dict)


main()
