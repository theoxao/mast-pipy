import json
import os.path
import os
import socket
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from contextlib import closing

from webargs import fields
from webargs.flaskparser import use_args, use_kwargs

import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, make_response,
    send_from_directory, current_app
)

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

from .pi import update_state, query_state
from .sqlite import get_db, query_db

bp = Blueprint('api', __name__, url_prefix='/api')

globals().setdefault('timestamp', int(round(time.time() * 1000)))


def ok(result):
    return jsonify(code=200, message='ok', data=result)


@bp.app_errorhandler(HTTPException)
def handle_invalid_usage(error):
    return jsonify(code=500, message="internal error", data=None)


@bp.route("/aligenie/5e9199f65abd9c10124f2f35e294f91b.txt", methods=['GET'])
def auth_aligenie(file):
    return "Jfc4Z4Ur15JwUBuvUQD5wg7Nu8+l+HscqYlfofbyJdYrwmXUPrPUrLoC7K/NBG4h"


@bp.route("/aligenie/task", methods=['POST'])
def aligenie_task():
    query = request.get_json()
    entities = query['slotEntities']
    pm0 = entities[0]['intentParameterName']
    v0 = entities[0]['standardValue']
    v1 = entities[1]['standardValue']
    logging.log(logging.DEBUG, v0 + '----->' + v1)
    pos = -1
    if v1 == '客厅灯光':
        pos = 4
    if v1 == '餐厅灯光':
        pos = 5
    if v1 == '次卧灯光':
        pos = 6
    if v1 == '主卧背光':
        pos = 3
    if v1 == '书房灯光':
        pos = 0
    if v1 == '主卧灯带':
        pos = 2
    if v1 == '主卧灯光':
        pos = 1
    if v1 == '厨房灯光':
        pos = 7
    conn = get_db()
    result = query_db('select * from device where position = ?', (pos,))[0]
    origin = result['value']
    value = update_state(pos, origin ^ 1, result['detect'])
    conn.execute('update device set value = ? where position = ? ', (value, pos))
    # conn.execute('insert into operate_record ')
    globals().update({'timestamp': int(round(time.time() * 1000))})
    conn.commit()
    return json.dumps({
        "returnCode": "0",
        "returnErrorSolution": "",
        "returnMessage": "",
        "returnValue": {
            "reply": "收到",
            "resultType": "RESULT",
            "executeCode": "SUCCESS"
        }
    }), 200, [("Content-Type", "application/json")]


@bp.route("/device/list", methods=['GET'])
def device_list():
    result = query_db('select * from device where support = 1')
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
    ret_value = query_state(result['detect'])
    result['value'] = ret_value
    conn = get_db()
    conn.execute('update device set value = ? where id = ? ', (ret_value, device_id))
    conn.commit()
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
    ret_value = update_state(dev['position'], value, dev['detect'])
    conn = get_db()
    conn.execute('update device set value = ? where id = ? ', (ret_value, dev_id))
    # conn.execute('insert into operate_record ')
    globals().update({'timestamp': int(round(time.time() * 1000))})
    conn.commit()
    # return ok(value)
    return ok(ret_value)


@bp.route('/param/timestamp', methods=['GET'])
def param_timestamp():
    return ok(globals().get('timestamp'))


@bp.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename, ext = os.path.splitext(file.filename)
    directory = int(round(time.time() * 1000)).__str__()
    path = os.path.join(os.environ['STATIC_DIR'], secure_filename(directory + ext))
    os.makedirs(os.path.join(os.environ['STATIC_DIR'], directory), exist_ok=True)
    meta = os.path.join(os.environ['STATIC_DIR'], directory, 'meta.json')
    conn = get_db()
    file.save(path)
    conn.execute("insert into upload_file(name , path, create_time) values (?,?,?)", (filename, path, time.time()))
    conn.commit()
    return ok(path)


executor = ThreadPoolExecutor(5)


@bp.route("/pdf2image", methods=['POST'])
def pdf2image():
    path = request.args.get('path')
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    name, _ = os.path.splitext(filename)
    out_path = directory + '/' + name
    print(out_path)
    os.makedirs(out_path, exist_ok=True)
    executor.submit(transfer, path, out_path)
    return ok(out_path)


@bp.route('/ll', methods=['GET'])
@use_kwargs({"path": fields.Str()}, location='query')
def ll(path):
    result = []
    if not path.startswith(os.environ['STATIC_DIR']):
        return ok([])
    get_all(result, path)
    return ok(result)


def get_all(result, cwd):
    get_dir = os.listdir(cwd)
    for i in get_dir:
        sub_dir = os.path.join(cwd, i)
        if os.path.isdir(sub_dir):
            get_all(result, sub_dir)
        else:
            result.append(os.path.join(cwd, i))


def transfer(path, out_path):
    from pdf2image import convert_from_path
    try:
        images = convert_from_path(path, output_folder=out_path, fmt="jpeg")
        print("")
    except Exception as err:
        print("convert error", err)
