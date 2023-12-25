#Converts the read_log string to tellraw commands to test if the read_log command is working
#Only needed two years of lost data to finally code this 

import re
from datetime import datetime

def apply_regex(string, pattern, result_format):
    matches = re.findall(pattern, string)

    if isinstance(matches[0],tuple):
        result = ""
        sep= ""
        for match in matches:
            result += sep + result_format.format(*match)
            sep = ","
        return result
    
    return result_format.format(*matches[0])

def replace_regex(string, pattern, replacement_format):
    matches = re.findall(pattern, string)
    result = re.sub(pattern, replacement_format, string.replace("{", "{{").replace("}","}}"))

    if isinstance(matches[0],tuple):
        new_list = []
        for entry in matches:
            for subentry in entry:
                new_list.append(subentry)
        return result.format(*new_list)
    

    return result.format(*matches)

def create_tellraw_command(summon_cmd):
    #Creates tellraw command that shows you the resulting entry in the log file
    tellraw_cmd = apply_regex(summon_cmd, r'"(\w+)\|(.+)"', 'tellraw @a [{{"text":"Print in file: {}\\n"}},{{"text":"$"}},{}]')

    tellraw_cmd = tellraw_cmd.replace("$",datetime.now().strftime("[%d.%m.%Y %H:%M:%S] "))

    tellraw_cmd = replace_regex(tellraw_cmd, r'string::(.*?)(?=-{2}|])', '{{"text":"{}"}}')

    tellraw_cmd = replace_regex(tellraw_cmd, r'score::(\w+),(\w+)', '{{"score":{{"name":"{}","objective":"{}"}}}}')

    tellraw_cmd = replace_regex(tellraw_cmd, r'--', ',')

    #Creates the tellraw command that shows you the values of the scores

    tellraw_cmd2 = apply_regex(summon_cmd,r'score::(\w+),(\w+)','{{"text":"\\n{0}: "}},{{"score":{{"name":"{0}","objective":"{1}"}}}}')
    
    tellraw_cmd2 = f'tellraw @a [{{"text":"\\nScore results:"}},{tellraw_cmd2}]'

    return f'{tellraw_cmd}\n{tellraw_cmd2}'

if __name__ == "__main__":
    file_path = "reset.mcfunction"

    with open(file_path, 'r') as file:
        file_content = file.read()

    command = None
    for line in file_content.split('\n'):
        if line.startswith('execute if score Release data_arcadia matches 0 run summon marker ~ ~ ~ {Tags:["arcadia_command read_log"'):
            command = create_tellraw_command(line)
            break

    if command:
        start_marker = "##Data write check"
        end_marker = "##Data write check"
        start_index = file_content.find(start_marker)
        end_index = file_content.find(end_marker, start_index + len(start_marker))

        if start_index != -1 and end_index != -1:
            new_content = (
                file_content[:start_index + len(start_marker)] +
                '\n' + command +
                file_content[end_index-1:]
            )
        else:
            new_content = file_content + f'\n{start_marker}\n{command}\n{end_marker}'

        with open(file_path, 'w') as file:
            file.write(new_content)    
    
        print("Updated tellraw command")



    