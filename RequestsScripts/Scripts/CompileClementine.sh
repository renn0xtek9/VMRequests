#!/bin/bash
function exitonlastfail {
errorcode="$?"
if [ "$errorcode" != "0" ]
then 
	echo -e "$(basename "$0") exits on error code $errorcode after: $1 "
	exit $errorcode #!WARNING you might want to override it as errorcode does not correspond to samething in that script!
fi 
}
logfile="$2"
rm -rf $logfile
echo "$1" | sudo -S apt-get update 
echo "$1" | sudo -S apt-get install git build-essential  -y    
exitonlastfail "apt-get install build essential"
echo "$1" | sudo -S apt-get install liblastfm-dev libtag1-dev gettext libboost-dev \
    libboost-serialization-dev libqt4-dev qt4-dev-tools libqt4-opengl-dev \
    cmake libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libglew1.5-dev libqjson-dev libgpod-dev libplist-dev \
    libusbmuxd-dev libmtp-dev libcdio-dev \
    protobuf-compiler libprotobuf-dev libcrypto++-dev \
    libfftw3-dev libsparsehash-dev libsqlite3-dev libpulse-dev \
    libqtwebkit-dev libchromaprint-dev libqca2-dev -y 
exitonlastfail "apt-get install dependencies"
mkdir -p /home/max/source/
cd /home/max/source
exitonlastfail "cd to source"
git clone https://github.com/clementine-player/Clementine.git 
exitonlastfail "clone git repository"

cd Clementine
git apply /media/sf_Public/RequestsScripts/Scrcipts/clementine.patch
exitonlastfail "apply patch for fts tokenizer"

cd /home/max/source/Clementine/bin
exitonlastfail "cd to bin folder"
rm -rf*
cmake .. && make -j2 > "$logfile"
exitonlastfail "cmake-make"
echo "$1" | sudo -S make install
exitonlastfail "make install"
exit 0



