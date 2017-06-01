#!/bin/bash
echo "running RSS_Digest!"
SCRIPTPATH=$(dirname "$BASH_SOURCE")
source $HOME/.profile
cd $SCRIPTPATH
source activate rss
python rss_digest.py authinfo.json config.json bloom.bl
source deactivate
