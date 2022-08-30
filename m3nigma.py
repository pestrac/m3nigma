import re
import m3u8
from m3u8 import protocol
from m3u8.parser import save_segment_custom_value
import urllib.parse
import sys, getopt
import os
from pathlib import Path
def parse_iptv_attributes(line, lineno, data, state):
    # Customize parsing #EXTINF
    if line.startswith(protocol.extinf):
        title = ''
        #chunks = line.replace(protocol.extinf + ':', '').split(',', 1)
        chunks = line.replace(protocol.extinf + ':', '').replace('",','"SE_ACABA_AQUI').split('SE_ACABA_AQUI', 1)
        if len(chunks) == 2:
            duration_and_props, title = chunks
        elif len(chunks) == 1:
            duration_and_props = chunks[0]

        additional_props = {}
        chunks = duration_and_props.strip().split(' ', 1)
        if len(chunks) == 2:
            duration, raw_props = chunks
            matched_props = re.finditer(r'([\w\-]+)="([^"]*)"', raw_props)
            for match in matched_props:
                additional_props[match.group(1)] = match.group(2)
        else:
            duration = duration_and_props

        if 'segment' not in state:
            state['segment'] = {}
        state['segment']['duration'] = float(duration)
        state['segment']['title'] = title

        # Helper function for saving custom values
        save_segment_custom_value(state, 'extinf_props', additional_props)

        # Tell 'main parser' that we expect an URL on next lines
        state['expect_segment'] = True

        # Tell 'main parser' that it can go to next line, we've parsed current fully.
        return True

def create_service_line(url,name):
    uno = "0"
    dos = "0"
    tres = "0"
    url =urllib.parse.quote(url)    
    line = "#SERVICE 4097:0:1:"+uno+":"+dos+":"+tres+":0:0:0:0:"+url+":"+name
    return line

def parse_m3u(source):
    playlist = m3u8.load(source,custom_tags_parser=parse_iptv_attributes)
    groups = {}
    index = 0
    for item in playlist.segments:
        try:
            group = item.custom_parser_values['extinf_props']['group-title']
        except:
            group = "NONE"
            print(index,item.title,group)
        #name = item.custom_parser_values['extinf_props']['tvg-name']
        name = item.title
        
        if group not in groups:
            groups[group] = []
        channel = {
            "name": name,
            "uri": item.uri,
        }
        groups[group].append(channel)
        index = index +1
        
    return groups
    
def save_group(groups,group_name,outputfolder,prefix):
    filename = prefix + group_name.replace(" ","_").replace("/","_") + ".tv"
    filename_path = os.path.join(outputfolder,filename)
    with open(filename_path , 'w', encoding="utf-8") as the_file:
        the_file.write("#NAME " + group_name)
        the_file.write("\n")
        for channel in groups[group_name]:
            line = create_service_line(channel["uri"],channel["name"])
            the_file.write(line)
            the_file.write("\n")
            

    
    


def show_groups(filename):
    groups = parse_m3u(filename)
    for group in groups.keys():
        print(group)
        

def save_groups(filename,outputfolder,prefix,groupslist):
    groups = parse_m3u(filename)
    for group in groupslist:
        print(group)
        save_group(groups,group,outputfolder,prefix)
    return groups

def save_groups_all(filename,outputfolder,prefix):
    groups = parse_m3u(filename)
    
    for group in groups:
        print(group)
        save_group(groups,group,outputfolder,prefix)
    return groups

def save_bouquets_all(groups,prefix,outputfolder):
    filename = outputfolder+"bouquets.tv"
    with open(filename, 'w', encoding="utf-8") as the_file:
        the_file.write('#NAME User - bouquets (TV)\n')
        for group_name in groups.keys():
            the_file.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "'+prefix+group_name.replace(" ","_").replace("/","_") +'.tv" ORDER BY bouquet\n')

def save_bouquets_list(groupslist,prefix,outputfolder):
    filename = os.path.join(outputfolder,"bouquets.tv")
    with open(filename, 'w', encoding="utf-8") as the_file:
        the_file.write('#NAME User - bouquets (TV)\n')
        for group_name in groupslist:
            the_file.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "'+prefix+group_name.replace(" ","_").replace("/","_") +'.tv" ORDER BY bouquet\n')




def main(argv):
    #print("copy files to /etc/enigma2")
    inputfile = ''
    outputfolder = "./output/"
    prefix = "m3nigma."
    save_bouquets = False
    all_groups = True
    groupslist = []

    try:
        opts, args = getopt.getopt(argv,"hi:bopsga",["ifile=","ofolder=","prefix=","savebouquets","allgroups","showgroups=","groupslist="])
    except getopt.GetoptError:
        print ('m3nigma.py -i <inputfile> -o <outputfolder>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('### show all groups')
            print('py .\m3nigma.py -i "playlist_TV_plus.m3u" -s')
            print('### export all groups')
            print('py .\m3nigma.py -i "playlist_TV_plus.m3u" --ofolder="outputfolder" -a')
            print('### export all groups and generate bouquets.tv file')
            print('py .\m3nigma.py -i "playlist_TV_plus.m3u" --ofolder="outputfolder" -a -b')
            print('### export selected groups and generate bouquets.tv file')
            print('py .\m3nigma.py -i "playlist_TV_plus.m3u" --ofolder="outputfolder" --prefix="myiptvserver." --groupslist="Various,Drama" -b')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            if not os.path.isfile(inputfile):
                print("[ERROR]  File ", inputfile, " not extits")
                sys.exit()
            else:
                print("[OK] Reading ", inputfile)
        elif opt in ("-o", "--ofolder"):
            outputfolder = Path(arg).resolve()
            if not os.path.isdir(outputfolder):
                print("[ERROR] Folder ", outputfolder, " not exits")
                sys.exit()
            else:
                print("[OK] Output folder is: ", outputfolder)
        elif opt in ("-p", "--prefix"):
            prefix = arg
        elif opt in ("-b", "--savebouquets"):
            save_bouquets = True
        elif opt in ("-s", "--showgroups"):
            show_groups(inputfile)
            sys.exit()
        elif opt in ("-g", "--groupslist"):
            groupslist = arg.split(",")
            all_groups = False
        elif opt in ("-a", "--allgroups"):
            all_groups = True
    #run:
    
    if all_groups:
        groups = save_groups_all(inputfile,outputfolder,prefix)
        groupslist=groups.keys()
    else:
        save_groups(inputfile,outputfolder,prefix,groupslist)
    if save_bouquets:
        save_bouquets_list(groupslist,prefix,outputfolder)

if __name__ == "__main__":
   main(sys.argv[1:])
