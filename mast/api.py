import json
import socket

import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, app
)
from werkzeug.security import check_password_hash, generate_password_hash

from .pi import update_state
from .sqlite import get_db, query_db

bp = Blueprint('api', __name__, url_prefix='/api')


def ok(result):
    return jsonify(code=200, message='ok', data=result)


@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin']='*'
    environ.headers['Access-Control-Allow-Method']='*'
    environ.headers['Access-Control-Allow-Headers']='x-requested-with,content-type'
    return environ


@bp.route("/device/list", methods=['GET'])
def device_list():
    result = query_db('select * from device')
    for device in result:
        if device.__contains__('room_id'):
            rs = query_db('select * from room where id = ?', (device['room_id'],))
            if len(rs) != 0:
                device['room'] = rs[0]
            else:
                device['room'] = None
        if device.__contains__('cate_id'):
            cs = query_db('select * from cate where id = ?', (device['cate_id'],))
            if len(cs) != 0:
                device['cate'] = cs[0]
            else:
                device['cate'] = None
    return ok(result)


@bp.route('/device/<device_id>', methods=['GET'])
def device(device_id):
    result = query_db('select * from device where id = ?', (device_id,))[0]
    return ok(result)


@bp.route('/remarkable/list', methods=['GET'])
def rm_device():
    result = query_db('select * from rm_device order by sort')
    for rm in result:
        rm['device'] = query_db('select * from device where id = ?' ,(rm['device_id'],))
    return ok(result)


@bp.route('/room/list', methods=['GET'])
def room_list():
    result = query_db('select * from room')
    for room in result:
        room['devices'] = query_db('select * from device where room_id = ?', (room['id'],))
    return ok(result)


@bp.route('/cate/list', methods=['GET'])
def cate_list():
    result = query_db('select* from cate')
    for cate in result:
        cate['devices'] = query_db('select * from device where cate_id = ?', (cate['id'],))
    return ok(result)


@bp.route('/ping', methods=['GET'])
def ping():
    return ok(socket.gethostbyname(socket.gethostname()))


@bp.route('/weather', methods=['GET'])
def weather():
    mock = request.args.get('mock')
    if mock is True:
        with open('mast/static/weather.json', 'r') as f:
            json_data = json.load(f)
            return ok(json_data)
    else:
        data = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat=30.287716668804674&lon=120.06577596450808&lang=zh_cn&units=metric&appid=2a49e2d2ff8a324e28c6f717685f55e3')
        return ok(data.json())


@bp.route('/device/update', methods=['POST'])
def update_device():
    dev_id = request.get_json()['id']
    value = request.get_json()['value']
    dev = query_db('select * from device where id = ?', (dev_id,))[0]
    update_state(dev['position'], value)
    conn = get_db()
    conn.execute('update device set value = ? where id = ? ', (value, dev_id))
    # conn.execute('insert into operate_record ')
    conn.commit()
    return ok(None)
