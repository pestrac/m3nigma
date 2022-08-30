# m3nigma
m3u to enigma2 channel list converter


## venv
### venv create
python -m venv venv
### venv activate
/venv/Scripts/Activate.ps1

## install requiremnts
pip install -r requirements.txt

## examples
### show all groups
py .\m3nigma.py -i "playlist_TV_plus.m3u" -s
### export all groups
py .\m3nigma.py -i "playlist_TV_plus.m3u" --ofolder="outputfolder" -a
### export all groups and generate bouquets.tv file
py .\m3nigma.py -i "playlist_TV_plus.m3u" --ofolder="outputfolder" -a -b
### export selected groups and generate bouquets.tv file
py .\m3nigma.py -i "playlist_TV_plus.m3u" --ofolder="outputfolder" --prefix="myiptvserver." --groupslist="Various,Drama" -b


