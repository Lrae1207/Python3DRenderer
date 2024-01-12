# Linux shell script to download python dependencies
depmissing=false

# Check for python3
type -P python3 >/dev/null 2>&1 && depmissing=true
if $depmissing
then
    echo "Dependency python3 missing; download it?"
    read input
    if [ $input = "yes" ] || [ $input = "Yes" ] || [ $input = "y" ] || [ $input = "Y" ]
    then
        echo "Downloading python3"
        sudo apt install python3 -y
    else
        echo "Dependency download failed."
        exit 1
    fi
fi

# Check for pip
echo "Downloading pip"
sudo apt install python3-pip -y
echo "Downloading python dependencies..."
sudo apt install python3-pygame -y
sudo apt install python3-pillow -y
echo "Done."
