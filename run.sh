#!/bin/bash
cd /home/chris/Dropbox/Rss_Digest/
nohup /home/chris/miniconda2/bin/python rss_digest.py authinfo.json config.json bloom.bl > errors.out &
