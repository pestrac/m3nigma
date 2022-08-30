import re
import m3u8
from m3u8 import protocol
from m3u8.parser import save_segment_custom_value
import urllib.parse
import sys, getopt

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
    
def save_group(groups,group_name,output):
    filename = str(output)+ group_name.replace(" ","_").replace("/","_") + ".tv"
    with open(filename, 'w', encoding="utf-8") as the_file:
        the_file.write("#NAME " + group_name)
        the_file.write("\n")
        for channel in groups[group_name]:
            line = create_service_line(channel["uri"],channel["name"])
            the_file.write(line)
            the_file.write("\n")
            
def save_bouquets_all(groups,filename):
    #filename = "./output/bouquets.tv"
    with open(filename, 'w', encoding="utf-8") as the_file:
        the_file.write('#NAME User - bouquets (TV)\n')
        for group_name in groups.keys():
            the_file.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "m3nigma.'+ group_name.replace(" ","_").replace("/","_") +'.tv" ORDER BY bouquet\n')
    
    


def show_groups(filename):
    groups = parse_m3u(filename)
    for group in groups.keys():
        print(group)
        

def save_groups(filename,output,groupslist):
    groups = parse_m3u(filename)
    for group in groupslist:
        print(group)
        save_group(groups,group,output)
    pass

def save_groups_all(filename,output):
    groups = parse_m3u(filename)
    
    for group in groups:
        print(group)
        save_group(groups,group,output)
    pass

def save_bouquets_list(filename,output,groupsist):
    pass




def main(argv):
    print("/etc/enigma2")
    inputfile = ''
    outputfile = "./output/m3nigma."
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:k:a",["ifile=","ofile=","showgroups=","groupslist="])
    except getopt.GetoptError:
        print ('m3nigma.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile> -o <outputfile>')
            print ('test.py -i <inputfile> -s #Show groups')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-s", "--showgroups"):
            show_groups(inputfile)
        elif opt in ("-k", "--groupslist"):
            groupslist = arg.split(",")
            print(groupslist)
            save_groups(inputfile,outputfile,groupslist)
        elif opt in ("-a", "--allgroups"):
            save_groups_all(inputfile,outputfile)
         

if __name__ == "__main__":
   main(sys.argv[1:])
