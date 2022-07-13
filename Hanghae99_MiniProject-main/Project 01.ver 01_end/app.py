from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = ''

from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('')
db = client.dbsparta

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})  # 사용자 정보 보내주기 (아래줄 포함)
        return render_template('calender.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/studylog')
def list_home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})  # 사용자 정보 보내주기 (아래줄 포함)
        return render_template('list.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#################################################################

# 달력 페이지
@app.route('/calendar')
def render_calendar():
    return render_template('calender.html')

# 투두 및 일정 페이지
@app.route('/calender_toodo')
def render_calender_toodo():
    return render_template('todo_list.html')

# todo리스트의 값 가져와서 보여주기
@app.route("/todo", methods=["GET"])
def todo_get():
    todo_list = list(db.todo.find({}, {'_id': False}))

    return jsonify({'todo': todo_list})

# DB에 todo리스트 값 저장하기
@app.route("/todo", methods=["POST"])
def todo_post():
    todo_receive = request.form['todo_give']
    date_receive = request.form['date_give']

    todo_list = list(db.todo.find({}, {'_id': False}))
    count = len(todo_list) + 1

    doc = {
        'num':count,
        'todo':todo_receive,
        'date':date_receive,
        'done':0
    }

    db.todo.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})

# 완료함수를 실행시켰을 때 done 값을 1로 변경하기
@app.route("/todo/done", methods=["POST"])
def todo_done():
    num_receive = request.form['num_give']
    db.todo.update_one({'num': int(num_receive)}, {'$set': {'done': 1}})
    return jsonify({'msg': '수행 완료!'})

# 취소함수를 실행시켰을 때 done 값을 0으로 변경하기
@app.route("/todo/cancel", methods=["POST"])
def todo_cancel():
    num_receive = request.form['num_give']
    db.todo.update_one({'num': int(num_receive)}, {'$set': {'done': 0}})
    return jsonify({'msg': '취소 완료!'})

# 삭제함수를 실행시켰을때 DB 삭제하기
@app.route("/todo/delete", methods=["POST"])
def todo_delete():
    num_receive = request.form['num_give']
    print("데이터 확인 : " + num_receive);
    # print로 찍어봤을 때, 해당 순번이 정상적으로 들어옴
    # 문제는 mongoDb에 있는 num은 int형이고, 내가 받아오려고 했던 num은 str형식이었음
    db.todo.delete_one({'num': int(num_receive)})
    # 문자열로 받은 데이터를 정수형으로 변환 시켜줘서 문제 해결
    # int()를 이용한 형변환
    return jsonify({'msg': '삭제 완료!'})

# 공부기록 페이지
@app.route('/studylog')
def studylog():
    return render_template('list.html')

# DB에 공부기록 리스트 값 저장하기
@app.route("/list", methods=["POST"])
def list_post():
    name_receive = request.form['name_give']
    blrink_receive = request.form['blrink_give']
    chrink_receive = request.form['chrink_give']
    comment_receive = request.form['comment_give']


    list_list = list(db.list.find({}, {'_id': False}))
    count = len(list_list) + 1

    doc = {
        'num': count,
        'name':name_receive,
        'blrink':blrink_receive,
        'chrink':chrink_receive,
        'comment':comment_receive,
        'done': 0
    }
    db.list.insert_one(doc)

    return jsonify({'msg': '저장 완료!!'})

# 공부기록 리스트의 값 가져와서 보여주기
@app.route("/list", methods=["GET"])
def list_get():
    list_list = list(db.list.find({}, {'_id': False}))
    return jsonify({'lists': list_list})

# 완료함수를 실행시켰을 때 done 값을 1으로 변경하기
@app.route("/list/done", methods=["POST"])
def list_done():
    num_receive = request.form['num_give']
    db.list.update_one({'num': int(num_receive)}, {'$set': {'done': 1}})
    return jsonify({'msg': '공부 목록 완료! 기억해야지!'})

# 취소함수를 실행시켰을 때 done 값을 0으로 변경하기
@app.route("/list/undone", methods=["POST"])
def list_undone():
    num_receive = request.form['num_give']
    db.list.update_one({'num': int(num_receive)}, {'$set': {'done': 0}})
    return jsonify({'msg': '취소 완료~! 더해보자!'})

# 삭제함수를 실행시켰을 때 DB삭제
@app.route("/list/delete", methods=["POST"])
def list_delete():
    num_receive = request.form['num_give']
    db.list.delete_one({'num': int(num_receive)})
    return jsonify({'msg': '삭제 완료'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
