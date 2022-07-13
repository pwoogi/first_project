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


# 운동기록 페이지
@app.route('/workoutlog')
def workoutlog():
    return render_template('list.html')

# DB에 운동기록 리스트 값 저장하기
@app.route("/list", methods=["POST"])
def list_post():
    title_receive = request.form['title_give']
    name_receive = request.form['name_give']
    hour_receive = request.form['hour_give']
    comment_receive = request.form['comment_give']


    list_list = list(db.list.find({}, {'_id': False}))
    count = len(list_list) + 1

    doc = {
        'num': count,
        'name':name_receive,
        'title':title_receive,
        'hour':hour_receive,
        'comment':comment_receive,
        'done': 0
    }
    db.list.insert_one(doc)

    return jsonify({'msg': '저장 완료!!'})

# 운동기록 리스트의 값 가져와서 보여주기
@app.route("/list", methods=["GET"])
def list_get():
    list_list = list(db.list.find({}, {'_id': False}))
    return jsonify({'lists': list_list})

# 완료함수를 실행시켰을 때 done 값을 1으로 변경하기
@app.route("/list/done", methods=["POST"])
def list_done():
    num_receive = request.form['num_give']
    db.list.update_one({'num': int(num_receive)}, {'$set': {'done': 1}})
    return jsonify({'msg': '운동 기록 완료!'})

# 취소함수를 실행시켰을 때 done 값을 0으로 변경하기
@app.route("/list/undone", methods=["POST"])
def list_undone():
    num_receive = request.form['num_give']
    db.list.update_one({'num': int(num_receive)}, {'$set': {'done': 0}})
    return jsonify({'msg': '취소 완료!'})

# 삭제함수를 실행시켰을 때 DB삭제
@app.route("/list/delete", methods=["POST"])
def list_delete():
    num_receive = request.form['num_give']
    db.list.delete_one({'num': int(num_receive)})
    return jsonify({'msg': '삭제 완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
