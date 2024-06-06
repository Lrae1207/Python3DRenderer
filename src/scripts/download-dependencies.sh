#!/bin/bash
# Linux only/run by sudo

# Linux shell script to download python dependencies
depmissing=true

# Check for python3
type -P python3 >/dev/null 2>&1 && depmissing=false
if $depmissing
then
    echo "Dependency python3 missing; download it?"
    read input
    if [ $input = "yes" ] || [ $input = "Yes" ] || [ $input = "y" ] || [ $input = "Y" ]
    then
        echo "Downloading python..."
        apt install -y python3 > /dev/null
        echo "Download complete"
    else
        echo "Dependency download failed."
        exit 1
    fi
fi

# Check for pip
echo "Downloading pip..."
apt install -y python3-pip > /dev/null
apt update -y python3-pip > /dev/null

echo "Downloading python dependencies..."

echo "Downloading python3-pygame..."
apt install -y python3-pygame > /dev/null
pip install pygame --upgrade > /dev/null
apt update -y python3-pygame > /dev/null
echo "Download complete."

echo "Downloading python3-pillow..."
apt install -y python3-pillow > /dev/null
apt update -y python3-pillow > /dev/null
echo "Download complete."

echo "Done."
exit 0
