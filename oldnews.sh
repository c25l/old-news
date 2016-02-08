cd /home/chris/old_news
git pull
nohup /home/chris/miniconda/bin/python old_news.py authinfo.json config.json bloom.bl > errors.out &
