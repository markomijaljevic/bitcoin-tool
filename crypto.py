from bitcoinrpc.authproxy import AuthServiceProxy #, JSONRPCException
import requests, tqdm, ast, time, folium, webbrowser
from ip2geotools.databases.noncommercial import DbIpCity
import PySimpleGUI as sg
from urllib.parse import quote
from collections import Counter
from decimal import Decimal

sg.LOOK_AND_FEEL_TABLE['Bitcoin'] = {'BACKGROUND': '#ffae00', 'TEXT': '#13161f', 'INPUT': '#ffffff', 'TEXT_INPUT': '#13161f', 'SCROLL': '#c8cf94',
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


def create_peer_map(peer_info):
    
    peer_map = folium.Map(
                    location=[40.710982, 8.799805],
                    zoom_start=3,
                    tiles='Stamen Toner'
                )

    tooltip = 'Click me!'

    for peer_ip, info in peer_info.items():

        try:
            response = DbIpCity.get(peer_ip, api_key='free')
        except KeyError:
            continue

        lat = response.latitude
        lon = response.longitude

        folium.Marker([lat, lon], popup='<i>' + str(info.get('city')) + '</i>', tooltip=tooltip).add_to(peer_map)
    
    peer_map.save('index.html')
    time.sleep(1)
    webbrowser.open('index.html')

def get_statistics(peers):
    
    countries     = []
    versions      = []
    sub_versions  = []
    min_fee       = []
    whitelisted   = []

    for _, item in peers.items():
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

def GUI(peer_info, net_info, chain_info):

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
                [   sg.Button('Show Peer Info', button_color=('#ffae00','#13161f'), font='Courier 14', border_width=2),
                    sg.Button('Show Blockchain Info',button_color=('#ffae00','#13161f'), font='Courier 14', border_width=2),
                    sg.Button('Cancel', button_color=('#ffae00','#13161f'), font='Courier 14', border_width=2)]]

    # Create the Window
    win1 = sg.Window('Bitcoin Testnet Network', layout)
    
    win2_active = False
    win3_active = False
    
    while True:
        ev1, _ = win1.Read()
        if ev1 is None or ev1 == 'Cancel':
            break

        if ev1 == 'Show Peer Info' and not win2_active:
            win2_active = True
            #win1.Hide()
            # All the stuff inside your window.
            layout_peer = [     [sg.Text('Network Peers Info', font = 'Courier 22', size = (75,2))],
                                [sg.Text('Countries:', font = 'Ariel 18'), sg.Text('## Percentage of users per countries', font = 'Ariel 12')],
                                [sg.Text(str(dict(stats.get('countries'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(70,4))],
                                [sg.Text('Versions:', font = 'Ariel 18'), sg.Text('## The peer version', font = 'Ariel 12')],
                                [sg.Text(str(dict(stats.get('versions'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(70,2))],
                                [sg.Text('Sub Versions:', font = 'Ariel 18'), sg.Text('## The string version', font = 'Ariel 12')],
                                [sg.Text(str(dict(stats.get('sub_versions'))).replace('{','').replace('}','').replace("'",''), font = 'Courier 14',size=(70,4))],
                                [sg.Text('Min Fee:', font = 'Ariel 18'), sg.Text('## The minimum fee rate for transactions peers accepts', font = 'Ariel 12')],
                                [sg.Text(str(dict(stats.get('min_fee'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(70,2))],
                                [sg.Text('Whitelisted:', font = 'Ariel 18'), sg.Text('## Whether the peer is whitelisted', font = 'Ariel 12')],
                                [sg.Text(str(dict(stats.get('whitelisted'))).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(70,2))],
    
                                [   sg.Button('Peer Details', button_color=('#ffae00','#13161f'), font='Courier 14', border_width=2),
                                    sg.Button('Show Peer Locations on Map', button_color=('#ffae00','#13161f'), font='Courier 14', border_width=2),
                                    sg.Button('Cancel', button_color=('#ffae00','#13161f'), font='Courier 14', border_width=2)]]

            win2 = sg.Window('Network Peers Info', layout_peer, size = (1000,650))
           

            while True:

                ev2, _ = win2.Read()
                if ev2 is None or ev2 == 'Cancel':
                    win2.Close()
                    win2_active = False
                    #win1.UnHide()
                    break
                elif ev2 == 'Peer Details':
                    output_peer_string = ''
                    for key, item in peer_info.items():
                        output_peer_string += str(key) + ' || ' + str(item).replace('{','').replace('}','').replace("'",'').replace(',',', ').title() + ' ' * 10 + '-' * 180 + ' ' * 10

                    sg.PopupScrolled(output_peer_string, title='Peer Details', size=(60,55), background_color='#ffae00',
                                     button_color=('#ffae00','#13161f'), font = 'Fixedsys 12')

                elif ev2 == 'Show Peer Locations on Map':
                    sg.PopupAnimated(sg.DEFAULT_BASE64_LOADING_GIF, time_between_frames=100)
                    create_peer_map(peer_info)
                    sg.PopupAnimated(image_source=None)

        if ev1 == 'Show Blockchain Info' and not win3_active:
            win3_active = True

            layout_chain = [    [sg.Text('Blockchain Info', font = 'Courier 22', size = (75,2))],
                                [sg.Text('Network Name:', font = 'Ariel 16'), sg.Text('## Current network name as defined in BIP70', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('chain')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(110,1))],
                                [sg.Text('Number of Blocks:', font = 'Ariel 16'), sg.Text('## The current number of blocks processed in the server', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('blocks')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Number of Headers:', font = 'Ariel 16'), sg.Text('## The current number of headers we have validated', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('headers')).replace('{','').replace('}','').replace("'",''), font = 'Courier 14',size=(120,1))],
                                [sg.Text('Best Block Hash:', font = 'Ariel 16'), sg.Text('## The hash of the currently best block', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('bestblockhash')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Difficulty:', font = 'Ariel 16'), sg.Text('## The current difficulty', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('difficulty')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Median time:', font = 'Ariel 16'), sg.Text('## Median time for the current best block', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('mediantime')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Verification progress:', font = 'Ariel 16'), sg.Text('## Estimate of verification progress [0..1]', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('verificationprogress')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Initial Block Download:', font = 'Ariel 16'), sg.Text('## Estimate of whether this node is in Initial Block Download mode.', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('initialblockdownload')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Chainwork:', font = 'Ariel 16'), sg.Text('## Total amount of work in active chain, in hexadecimal', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('chainwork')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Size on Disk:', font = 'Ariel 16'), sg.Text('## The estimated size of the block and undo files on disk', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('size_on_disk')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(120,1))],
                                [sg.Text('Softforks:', font = 'Ariel 16'), sg.Text('## Status of softforks in progress', font = 'Ariel 12')],
                                [sg.Text(str(chain_info.get('softforks')).replace('{','').replace('}','').replace("'",'') , font = 'Courier 14',size=(70,3))],
                                [sg.Text(str(chain_info.get('warnings')).replace('{','').replace('}','').replace("'",'') , font = 'Ariel 14',size=(120,1), text_color='#ff0023')],
                                [sg.Button('Cancel', button_color=('#ffae00','#13161f'), font='Courier 14', border_width=2)]]

            win3 = sg.Window('Blockchain Info', layout_chain, size = (1000,920))

            while True:
                ev3, _ = win3.Read()
                if ev3 is None or ev3 == 'Cancel':
                    win3.Close()
                    win3_active = False
                    #win1.UnHide()
                    break
                elif ev3 == 'Peer Details':
                    win3.Close()
                    win3_active = False
                    break

    win1.close()
    

def get_geolocation_details(peers):

    filtered_data = {} 

    for peer in tqdm.tqdm(peers[:5]):
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

    print('')
    print('-' * 50)
    print('Bitcoin Network Tool'.title())
    print('Version: 1.0')
    print('Author: Marko Mijaljević')
    print('-' * 50)

    time.sleep(2)
    print()
    print('Connecting to the Bitcoin Node')
    client = connect_to_client(user, password, host, port)
    print('Connected...')
    print('-' * 50)
    print()
    print('Gathering Network information. This can take a while depending on the number of peers in the network.\n')
    
    chain_info = client.getblockchaininfo()
    peer_info = get_geolocation_details(client.getpeerinfo())
    net_info = client.getnetworkinfo()
    
    print('\nCompleted...')
    print('')
    print('-' * 50)
    print('======> ' + 'Everything is done, Enjoy!' + ' <======')
    print('-' * 50)
    time.sleep(2)

    GUI(peer_info, net_info, chain_info)


if __name__ == "__main__":
    main()