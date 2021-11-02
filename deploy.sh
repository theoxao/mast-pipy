
export FLASK_APP=mast
nohup  flask run -p 8000 > server.log 2>&1 & echo $! > pid
