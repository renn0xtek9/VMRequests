#!/bin/bash
cd ~/Downloads
rm -rf sdk
# wget https://download.virtualbox.org/virtualbox/5.2.16/VirtualBoxSDK-5.2.16-123759.zip
wget https://download.virtualbox.org/virtualbox/5.2.18/VirtualBoxSDK-5.2.18-124319.zip
# unzip VirtualBoxSDK-5.2.16-123759.zip 
unzip VirtualBoxSDK-5.2.18-124319.zip
sudo rm -rf /opt/sdk
sudo mv sdk /opt/sdk 
export VBOX_INSTALL_PATH=$(which VirtualBox)
export VBOX_SDK_PATH=/opt/sdk/
cd $VBOX_SDK_PATH
sudo chmod +x $VBOX_SDK_PATH/installer/vboxapisetup.py
sudo chmod +x $VBOX_SDK_PATH/bindings/glue/python/sample/vboxshell.py
cd installer
sudo VBOX_INSTALL_PATH=/usr/lib/virtualbox python3 ./vboxapisetup.py install		#For python3 as well
sudo VBOX_INSTALL_PATH=/usr/lib/virtualbox python2 ./vboxapisetup.py install		#For python3 as well
pip install pyvbox
echo "You need to put export VBOX_INSTALL_PATH=$VBOX_INSTALL_PATH in you .bashrc"
echo "You need to put export VBOX_SDK_PATH=$VBOX_SDK_PATH in you .bashrc"
echo "You need to put export PYTHONPATH=\$PYTHONPATH:$VBOX_SDK_PATH/bindings/xpcom/python in your .bashrc"
echo "Test the installation by running $VBOX_SDK_PATH/bindings/glue/python/sample/vboxshell.py"
