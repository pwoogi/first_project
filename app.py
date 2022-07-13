import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.ns2pf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.todo

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
    # len은 몇개인지 세어줌, 끝난거 지우줄려면 어떤건지 숫자 지정줘야한다
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
    # 해당 num의 done을 1로 변경해준다
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
