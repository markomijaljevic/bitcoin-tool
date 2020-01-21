from bitcoinrpc.authproxy import AuthServiceProxy #, JSONRPCException
import requests, tqdm, ast, sys
from ip2geotools.databases.noncommercial import DbIpCity
import PySimpleGUI as sg
from urllib.parse import quote
from collections import Counter

sg.LOOK_AND_FEEL_TABLE['Bitcoin'] = {'BACKGROUND': '#ff9500', 'TEXT': '#13161f', 'INPUT': '#ffffff', 'TEXT_INPUT': '#13161f', 'SCROLL': '#c8cf94',
                  'BUTTON': ('#ffffff', '#13161f'), 'PROGRESS': ('#01826B', '#D0D0D0'), 'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                  'COLOR_LIST': ['#3b503d', '#4a746e', '#c8cf94', '#f1edb3'], 'DESCRIPTION': ['Green', 'Turquoise', 'Yellow']}


def connect_to_client(user, password, host, port):
    url = 'http://' + user + ':' + password + '@' + host + ':' + port
    return AuthServiceProxy(url)

def get_geolocation_from_ip(ip):

    request = requests.get('http://api.db-ip.com/v2/'
                        + quote('free')
                        + '/' + quote(ip),
                        timeout=62)

    content = ast.literal_eval(request.content.decode('utf-8'))

    return content

def get_statistics(peers):
    
    countries     = []
    versions      = []
    sub_versions  = []
    min_fee       = []
    whitelisted   = []

    for _, item in tqdm.tqdm(peers.items()):
        countries.append(item.get('country'))
        versions.append(item.get('version'))
        sub_versions.append(item.get('sub_version'))
        min_fee.append(str(item.get('min_fee')))
        whitelisted.append(item.get('whitelisted'))
    
    count = {}
    for key, item in dict(Counter(countries)).items():
        count[key] = str(int((int(item) / len(countries)) * 100)) + str('%')

    ver = {}
    for key, item in dict(Counter(versions)).items():
        ver[key] = str(int((int(item) / len(versions)) * 100)) + str('%')

    sub = {}
    for key, item in dict(Counter(sub_versions)).items():
        sub[key] = str(int((int(item) / len(sub_versions)) * 100)) + str('%')

    white = {}
    for key, item in dict(Counter(whitelisted)).items():
        white[key] = str(int((int(item) / len(whitelisted)) * 100)) + str('%')

    min_feee = {}
    for key, item in dict(Counter(min_fee)).items():
        min_feee[key] = str(int((int(item) / len(min_fee)) * 100)) + str('%')


    stats = {   'countries' : count, 'versions' : ver, 'sub_versions' : sub,
                'min_fee' : min_feee, 'whitelisted' : white}

    return stats

def GUI(peer_info, net_info):

    stats = get_statistics(peer_info)
    #print(stats)
    #print('--')
    #print(peer_info)
    sg.theme('Bitcoin')

    # All the stuff inside your window.
    layout = [  [sg.Text('Bitcoin Testnet Network', font = 'Courier 22', size = (75,2))],
                [sg.Text('Network active : ' + str(net_info.get('networkactive')) , font = 'Courier 16')],
                [sg.Text('Network connections : ' + str(net_info.get('connections')) , font = 'Courier 16')],
                [sg.Text('Network version : ' + str(net_info.get('version')) , font = 'Courier 16')],
                [sg.Text('Network sub-version : ' + str(net_info.get('subversion')) , font = 'Courier 16')],
                [sg.Text('Network protocol version : ' + str(net_info.get('protocolversion')) , font = 'Courier 16', size = (75,2))],
                [sg.Text(str(net_info.get('warnings')) , font = 'Ariel 14' , size = (75,1), text_color='#ff0023')],
                [sg.Button('Show Peer Info', button_color=('#f7931a','#13161f'), font='Courier 14', border_width=2), sg.Button('Cancel', button_color=('#f7931a','#13161f'), font='Courier 14', border_width=2)]]

    # Create the Window
    win1 = sg.Window('Bitcoin Testnet Network', layout)
    
    win2_active=False
    while True:
        ev1, _ = win1.Read()
        if ev1 is None or ev1 == 'Cancel':
            break

        if ev1 == 'Show Peer Info' and not win2_active:
            win2_active = True
            #win1.Hide()
            # All the stuff inside your window.
            layout_peer = [     [sg.Text('Network Peers Info', font = 'Courier 22', size = (75,2))],
                                [sg.Text('Countries:', font = 'Ariel 18')],
                                [sg.Text(str(dict(stats.get('countries'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(110,4))],
                                [sg.Text('Versions:', font = 'Ariel 18')],
                                [sg.Text(str(dict(stats.get('versions'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,2))],
                                [sg.Text('Sub Versions:', font = 'Ariel 18')],
                                [sg.Text(str(dict(stats.get('sub_versions'))).replace('{','').replace('}','').replace("'",''), font = 'Courier 14',size=(120,4))],
                                [sg.Text('Min Fee:', font = 'Ariel 18')],
                                [sg.Text(str(dict(stats.get('min_fee'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,2))],
                                [sg.Text('Whitelisted:', font = 'Ariel 18')],
                                [sg.Text(str(dict(stats.get('whitelisted'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,2))],
    
                                [   sg.Button('Peer Details', button_color=('#f7931a','#13161f'), font='Courier 14', border_width=2), 
                                    sg.Button('Cancel', button_color=('#f7931a','#13161f'), font='Courier 14', border_width=2)]]

            win2 = sg.Window('Network Peers Info', layout_peer, size = (1500,700))

            while True:
                ev2, _ = win2.Read()
                if ev2 is None or ev2 == 'Cancel':
                    win2.Close()
                    win2_active = False
                    #win1.UnHide()
                    break
                elif ev2 == 'Peer Details':
                    win2.Close()
                    win2_active = False
                    break

    win1.close()
    

def get_geolocation_details(peers):

    filtered_data = {} 

    for peer in tqdm.tqdm(peers):
        ip_address = peer.get('addr')[:peer.get('addr').find(':')]        
        geo_info = get_geolocation_from_ip(ip_address)

        #geo data
        country   = geo_info.setdefault('countryName','')
        region    = geo_info.setdefault('stateProv', '')   
        city      = geo_info.setdefault('city','')
        continent = geo_info.setdefault('continentName','')

        #tech data
        bytes_sent      = peer.get('bytessent')
        bytes_recived   = peer.get('bytesrecv')
        connection_time = peer.get('conntime')
        ping_time       = peer.get('pingtime')
        version         = peer.get('version')
        sub_version     = peer.get('subver')
        start_height    = peer.get('startingheight')
        ban_score       = peer.get('banscore')
        synced_blocks   = peer.get('synced_blocks')
        whitelisted     = peer.get('whitelisted')
        min_fee         = peer.get('minfeefilter') 

        filtered_data[ip_address] = {   'country' : country, 'region' : region, 'city' : city, 'continent' : continent, 'bytes_sent' : bytes_sent, 
                                        'bytes_recived' : bytes_recived, 'connection_time' : connection_time, 'ping_time' : ping_time,'version' : version,
                                        'sub_version' : sub_version, 'start_height' : start_height, 'ban_score' : ban_score, 'synced_blocks' : synced_blocks,
                                        'whitelisted' : whitelisted, 'min_fee' : min_fee}

    return filtered_data

def main():

    host     = 'blockchain.oss.unist.hr'
    user     = 'student'
    password = 'WYVyF5DTERJASAiIiYGg4UkRH'
    port     = '8332'

    client = connect_to_client(user, password, host, port)
    print(client.getblockchaininfo())
    peer_info = get_geolocation_details(client.getpeerinfo())

    #GUI(peer_info, client.getnetworkinfo())
    # Design pattern 2 - First window remains active




if __name__ == "__main__":
    main()