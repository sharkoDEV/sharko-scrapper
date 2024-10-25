import requests
import json
import os
import time
from fake_useragent import UserAgent
import re
import uuid
import ctypes
from colorama import init, Fore, Style
import fade
import colorama

colorama.init()



def sanitize_filename(name):
    try:
        return re.sub(r'^([0-9])', '', re.sub(r'[/:"*?<>|]', '', name)).replace('^0','').replace('^1','').replace('^2','').replace('^3','').replace('^4','').replace('^5','').replace('^6','').replace('^7','').replace('^8','').replace('^9','')
    except Exception as e:
        print(f'Error sanitizing the filename : {str(e)}')
        return str(uuid.uuid4())

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

def player_exists(file_path, player_info, player_list):
    try:
        if not os.path.exists(file_path):
            return False

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines:
            try:
                existing_player = json.loads(line)
            except json.JSONDecodeError:
                continue

            if existing_player.get('fivem') == player_info.get('fivem'):
                fields_to_check = ['steam', 'name', 'live', 'xbl', 'license', 'license2', 'name']
                fields_match = all(existing_player.get(field) == player_info.get(field) for field in fields_to_check if (existing_player.get(field) or player_info.get(field)))

                if fields_match:
                    return True

        if player_info['identifiers'] in player_list:
            return True

        return False
    except Exception as e:
        print(f"Error verifying the player's existence: {str(e)}")
        return False
player_scrapped = 0
def fetch_server_info(server_id, proxy_config, player_list):
    try:
        url = f'https://servers-frontend.fivem.net/api/servers/single/{server_id}'
        user_agent = UserAgent()
        headers = {
            'User-Agent': user_agent.random,
            'method': 'GET'
        }

        try:
            response = requests.get(url, headers=headers, proxies=proxy_config)

            if response.status_code == 200:
                server_data = response.json()
                hostname = sanitize_filename(str(uuid.uuid4()))

                try:
                    hostname = sanitize_filename(server_data['Data']['hostname'])[:100]
                except Exception as err:
                    print(f'Error retrieving the hostname : {str(err)}')

                try:
                    if len(server_data['Data']['vars']['sv_projectName']) >= 10:
                        hostname = sanitize_filename(server_data['Data']['vars']['sv_projectName'])[:100]
                except:
                    pass

                if not os.path.exists('scrap'):
                    os.makedirs('scrap')

                file_path = f'scrap/{hostname}.txt'
                global player_scrapped
                for player in server_data['Data']['players']:
                    player_data = json.dumps(player, ensure_ascii=False)
                    player_identifiers = player['identifiers']

                    if not player_exists(file_path, player, player_list):
                        with open(file_path, 'a', encoding='utf-8') as file:
                            file.write(player_data)
                            file.write('\n')

                        player_list.append(player_identifiers)
                    player_scrapped = player_scrapped + 1

                    print(f"{BLUE}[{player_scrapped}]  [{player['name']}]       [{file_path}]")

            

        except requests.RequestException as e:
            print(f'HTTP request error : {str(e)}')

    except Exception as e:
        print(f'Error retrieving server information: {str(e)}')

def process_server_batches(server_ids, proxy_configs, player_list):
    try:
        for server_id, proxy_config in zip(server_ids, proxy_configs):
            fetch_server_info(server_id, proxy_config, player_list)
            time.sleep(0.5)
    except Exception as e:
        print(f'Error while processing server batches : {str(e)}')

def run_main():
    try:
        with open('serveurid.txt', 'r') as server_file:
            server_ids = [line.strip() for line in server_file.readlines()]

        with open('proxies.txt', 'r') as proxy_file:
            proxies = [{'http': f'socks5://{proxy.strip()}'} for proxy in proxy_file]

        total_proxies = len(proxies)
        added_players = []

        while True:
            mid_index = len(server_ids) // 2
            first_half = server_ids[:mid_index]
            second_half = server_ids[mid_index:]

            process_server_batches(first_half, proxies, added_players)
            process_server_batches(second_half, proxies, added_players)
    except FileNotFoundError as e:
        print(f'File not found : {str(e)}')
    except Exception as e:
        print(f'Error : {str(e)}')
            
def display_startup_banner():
    try:
        os.system("cls")
        banner = f'''                    
{BLUE} ::::::::  :::    :::     :::     :::::::::  :::    ::: ::::::::                         
:+:    :+: :+:    :+:   :+: :+:   :+:    :+: :+:   :+: :+:    :+:                         |_        _ |_   _. ._ |   _  
+:+        +:+    +:+  +:+   +:+  +:+    +:+ +:+  +:+  +:+    +:+                         |_) \/   _> | | (_| |  |< (_) 
+#++:++#++ +#++:++#++ +#++:++#++: +#++:++#:  +#++:++   +#+    +:+                             /                         

       +#+ +#+    +#+ +#+     +#+ +#+    +#+ +#+  +#+  +#+    +#+                        
#+#    #+# #+#    #+# #+#     #+# #+#    #+# #+#   #+# #+#    #+#                        
 ########  ###    ### ###     ### ###    ### ###    ### ########                         

  ::::::::   ::::::::  :::::::::      :::     :::::::::  :::::::::  :::::::::: :::::::::  
:+:    :+: :+:    :+: :+:    :+:   :+: :+:   :+:    :+: :+:    :+: :+:        :+:    :+: 
+:+        +:+        +:+    +:+  +:+   +:+  +:+    +:+ +:+    +:+ +:+        +:+    +:+ 
+#++:++#++ +#+        +#++:++#:  +#++:++#++: +#++:++#+  +#++:++#+  +#++:++#   +#++:++#:  
       +#+ +#+        +#+    +#+ +#+     +#+ +#+        +#+        +#+        +#+    +#+ 
#+#    #+# #+#    #+# #+#    #+# #+#     #+# #+#        #+#        #+#        #+#    #+# 
 ########   ########  ###    ### ###     ### ###        ###        ########## ###    ### 

'''
        os.system("pip install -r requirements.txt")
        faded_text = (banner)
        print(faded_text)
    except Exception as e:
        print(f'error : {str(e)}')

    run_main()

display_startup_banner()
