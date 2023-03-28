import base64

from flask import Flask
import os
import io
from flask import request, redirect, render_template
from flask import session
from flask import Flask, url_for
import matplotlib.pyplot as plt
from datetime import datetime
from flask import abort

app = Flask(__name__)

app.secret_key = 'mysecretkey'


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('dashboard', username=username))
        else:
            return render_template('login.html', message="invalid")
            # return 'Invalid username or password'
    else:

        return render_template('login.html')


def check_user(username, password):
    with open('db.txt', 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if parts[0] == username and parts[1] == password:
                return True
    return False


def load_users():
    users = {}
    with open('db.txt', 'r') as f:
        for line in f:
            username, password, access_level = line.strip().split(':')
            users[username] = {'password': password, 'access_level': access_level}
    return users


@app.route('/dashboard/<username>')
def userboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    username = username
    filename = f"user_data/{username}.txt"

    with open(filename, 'r') as file:
        data = file.readlines()

    x = []
    y = []
    for line in data:
        values = line.strip().split(',')
        time = int(values[0]) * 24 * 60 * 60 + int(values[1]) * 60 * 60 + int(values[2]) * 60 + int(values[3])
        power = float(values[4])
        x.append(time)
        y.append(power)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('Time')
    ax.set_ylabel('Power')
    ax.set_title('Power Usage')
    plt.xticks(rotation=45)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Передаем путь к изображению в шаблон
    img_url = base64.b64encode(img.read()).decode()
    return render_template('user_dashboard.html', img_url=img_url, user=username)


@app.route('/dashboard/<username>')
def dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    else:
        users = load_users()
        access_level = users[username]['access_level']
        if access_level == 'admin':
            # показать информацию для администратора
            return admin_dashboard(username)
        elif access_level == 'operator':
            # показать информацию для оператора
            return render_template('operator_dashboard.html', username=username)
        else:
            # показать информацию для пользователя
            user_file = os.path.join('user_data', f'{username}.txt')
            if not os.path.exists(user_file):
                return f'User {username} not found'
            with open(user_file, 'r') as f:
                lines = f.readlines()
                temperature = lines[0].strip()
                cost = lines[1].strip()
            return userboard(username)
@app.route('/admin_dashboard/<admin_username>')
def admin_dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    users = load_users()
    if username not in users or users[username]['access_level'] != 'admin':
        abort(404)

    all_users = []
    for username, data in users.items():
        user_info = {
            'username': username,
            'field1': '',  # заполни данные для поля 1
            'field2': '',  # заполни данные для поля 2
        }
        all_users.append(user_info)

    return render_template('admin_dashboard.html', username=username, all_users=all_users)


@app.route('/admin_dashboard/<admin_username>/user_stats/<user_username>')
def user_stats(admin_username, user_username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    users = load_users()
    if admin_username not in users or users[admin_username]['access_level'] != 'admin':
        abort(404)
    if user_username not in users:
        abort(404)

    # здесь собираем статистику для пользователя user_username
    # и передаем ее в шаблон для отображения
    user_stats = {}

    return render_template('user_stats.html', username=admin_username, user_username=user_username, user_stats=user_stats)


if __name__ == '__main__':
    app.run(debug=1)
