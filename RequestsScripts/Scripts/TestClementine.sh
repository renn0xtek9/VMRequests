#!/bin/bash
logfile="$2"
echo "$1" | sudo -S apt-get install sqlite3 -y
rmdir /home/max/Music
ln -s /media/max/zalman/Music /home/max/Music 
clementine -c 'Adele' '/home/max/Music/Adele/Adele_-_Someone_Like_You_(Brit_Awards).mp3' '/home/max/Music/Adele/Adel-Rolling_In_The_Deep.mp3' &
sleep 10
result=$(sqlite3 /home/max/.config/Clementine/clementine.db "SELECT * FROM playlist_items_fts")
if [[ $result == *"unknown tokenizer"* ]]; then   #eg if [[ $str == *"in"* ]]
	echo $result > "$logfile"
	exit 1
fi


echo "Test completed successfully" > "$logfile"
exit 0 
