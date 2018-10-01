# first make sure to remove your current virtualbox
sudo apt purge virtualbox

# next, add the repository to your sources
sudo add-apt-repository "deb http://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib"

# add public keys to verify downloads
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -

# now update to complete the process of adding the repository
sudo apt update

# install dkms if you haven't already
sudo apt install dkms

# install virtualbox; change version number as needed
sudo apt install virtualbox-5.2

