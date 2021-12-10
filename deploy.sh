
git reset --hard
git pull
kill $(ps aux | grep -m 1 'bin/flask' | awk '{ print $2 }')
export FLASK_APP=mast
nohup  flask run -p 8000 > server.log 2>&1 & echo $! > pid
