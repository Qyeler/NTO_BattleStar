import base64
from io import BytesIO
from random import randint

from flask import Flask, send_file
import os
import io
from flask import request, redirect, render_template
from flask import session
from flask import Flask, url_for
import matplotlib.pyplot as plt
from datetime import datetime
from flask import abort
import calcsum
import doPdf
from calculate_users import on_button_update

app = Flask(__name__)

app.secret_key = 'mysecretkey'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            users = load_users()
            access_level = users[username]['access_level']
            if access_level == 'admin':
                session['username'] = username
                return redirect(url_for('admin_dashboard', admin_username=username))
            elif access_level == 'operator':
                session['username'] = username
                return redirect(url_for('owner_dashboard', owner_name=username))
            else:
                session['username'] = username
                user_file = os.path.join('user_data', f'{username}.txt')
                if not os.path.exists(user_file):
                    return f'User {username} not found'
                with open(user_file, 'r') as f:
                    lines = f.readlines()
                    temperature = lines[0].strip()
                    cost = lines[1].strip()
            return redirect(url_for('userboard', username=username))
        else:
            return render_template('login.html', message="invalid")
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


@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def userboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    if request.method == 'POST':
        start_str = request.form['start']
        end_str = request.form['end']
        cost = calcsum.count_watts(f"user_data/{username}.txt", start_str, end_str)
        img_url = url_for('static', filename=f"images/{username}.png")  # формируем url для файла
        totalscore = cost * 1.74
        cost = round(cost, 2)
        totalscore = round(totalscore, 2)
        return render_template('user_dashboard.html', user=username, img_url=img_url, cost=cost, totalscore=totalscore)
    username = username
    filename = f"user_data/{username}.txt"
    with open(filename, 'r') as file:
        data = file.readlines()
    x = []
    y = []
    sr = 0.0
    for line in data:
        values = line.strip().split(',')
        time = float(float(float(values[0]) * 24 * 60 * 60 + float(values[1]) * 60 * 60 + float(values[2]) * 60 + float(
            values[3])) / 3600)
        if (float(time) < float(sr) + 0.2):
            continue
        sr = float(time)
        power = float(values[4])
        x.append(time)
        y.append(power)

    filename = f"user_data/temperature/{username}.txt"
    with open(filename, 'r') as file:
        data2 = file.readlines()
    xtmp = []
    ytmp = []
    sr = 0.0
    for line in data2:
        values = line.strip().split(',')
        time = float(float(float(values[0]) * 24 * 60 * 60 + float(values[1]) * 60 * 60 + float(values[2]) * 60 + float(
            values[3])) / 3600)
        if (float(time) < float(sr) + 0.2):
            continue
        sr = float(time)
        temp = float(values[4])
        xtmp.append(time)
        ytmp.append(temp)
    fig2, ax2 = plt.subplots()
    ax2.plot(xtmp, ytmp)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Temperature')
    ax2.set_title('Temperature trend')
    plt.xticks(rotation=45)
    img_path2 = f"static/images/tempgraf/{username}.png"
    plt.savefig(img_path2, format='png')
    img_url2 = url_for('static', filename=f"images/tempgraf/{username}.png")

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('Time')
    ax.set_ylabel('Power')
    ax.set_title('Power Usage')
    plt.xticks(rotation=45)
    img_path = f"static/images/{username}.png"
    plt.savefig(img_path, format='png')
    img_url = url_for('static', filename=f"images/{username}.png")
    costpdf = calcsum.count_watts(f"user_data/{username}.txt", "0,0,0,0", "30,0,0,0")
    doPdf.create_pdf_with_image_and_sum(f"static/images/{username}.png", f"static/pdf/{username}.pdf", 5, costpdf,
                                        costpdf * 1.78)
    filename = f"user_data/userStatus/{username}.txt"
    with open(filename, 'r') as f:
        data = f.read()
    return render_template('user_dashboard.html', img_url=img_url, user=username, status=data.split(',')[0])


# @app.route('/dashboard/<username>')
# def dashboard(username):
#     if 'username' not in session or session['username'] != username:
#         return redirect(url_for('login'))
#     else:
#         users = load_users()
#         access_level = users[username]['access_level']
#         if access_level == 'admin':
#             return admin_dashboard(username)
#         elif access_level == 'operator':
#             return render_template('operator_dashboard.html', username=username)
#         else:
#             user_file = os.path.join('user_data', f'{username}.txt')
#             if not os.path.exists(user_file):
#                 return f'User {username} not found'
#             with open(user_file, 'r') as f:
#                 lines = f.readlines()
#                 temperature = lines[0].strip()
#                 cost = lines[1].strip()
#                 return userboard(username)
@app.route('/admin_dashboard/<admin_username>', methods=['GET', 'POST'])
def admin_dashboard(admin_username):
    if 'username' not in session or session['username'] != admin_username:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_str = request.form['username']
        start_str = request.form['start']
        end_str = request.form['end']
        cost = calcsum.count_watts(f"user_data/{user_str}.txt", start_str, end_str)
        img_url = url_for('static', filename=f"images/{user_str}.png")  # формируем url для файла
        totalscore = cost * 1.74
        cost = round(cost, 2)
        totalscore = round(totalscore, 2)
        return render_template('calc info.html', username=admin_username, cost=cost, totalscore=totalscore)

    users = load_users()
    all_users = []
    for username, data in users.items():
        if (users[username]['access_level'] == "admin" or users[username]['access_level'] == "operator"):
            continue
        filename = f"user_data/{username}.txt"
        with open(filename, 'r') as file:
            data = file.readlines()
        x = []
        y = []
        sr = 0.0
        for line in data:
            values = line.strip().split(',')
            time = float(float(
                float(values[0]) * 24 * 60 * 60 + float(values[1]) * 60 * 60 + float(values[2]) * 60 + float(
                    values[3])) / 3600)
            if (float(time) < float(sr) + 0.2):
                continue
            sr = float(time)
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
        filename = f"user_data/temperature/{username}.txt"
        img_url = base64.b64encode(img.read()).decode()

        with open(filename, 'r') as file:
            data2 = file.readlines()
        xtmp = []
        ytmp = []
        sr = 0.0
        for line in data2:
            values = line.strip().split(',')
            time = float(float(
                float(values[0]) * 24 * 60 * 60 + float(values[1]) * 60 * 60 + float(values[2]) * 60 + float(
                    values[3])) / 3600)
            if (float(time) < float(sr) + 0.2):
                continue
            sr = float(time)
            temp = float(values[4])
            xtmp.append(time)
            ytmp.append(temp)
        fig2, ax2 = plt.subplots()
        ax2.plot(xtmp, ytmp)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Temperature')
        ax2.set_title('Temperature trend')
        plt.xticks(rotation=45)
        img_path2 = f"static/images/tempgraf/{username}.png"
        plt.savefig(img_path2, format='png')
        img_url2 = url_for('static', filename=f"images/tempgraf/{username}.png")

        start_str = "0,0,0,0"
        end_str = "30,0,0,0"
        cost = calcsum.count_watts(f"user_data/{username}.txt", start_str, end_str)
        filename = f"user_data/userStatus/{username}.txt"
        with open(filename, 'r') as file:
            data = file.readlines()
        onoff = data[0].split(',')[0]
        payinfo = data[0].split(',')[1]
        user_info = {
            'username': username,
            'field1': str(cost),  # заполни данные для поля 1
            'graf': f'data:image/png;base64,{img_url}',  # заполни данные для поля 2
            'graf2': f'data:image/png;base64,{img_url2}',
            'on/off': onoff,
            'payinfo': payinfo
        }
        all_users.append(user_info)
    return render_template('admin_dashboard.html', username=admin_username, all_users=all_users)


@app.route('/button_pressed', methods=['GET', 'POST'])
def button_pressed():
    username = request.form['username']
    filename = f"user_data/userStatus/{username}.txt"
    with open(filename, 'r') as f:
        data = f.read()
    first_status, second_status = data.split(',')
    if request.form['action'] == '1':
        if (first_status == 'off'):
            first_status = 'on'
        else:
            first_status = 'off'
    if request.form['action'] == '2':
        print(second_status)
        if second_status == 'off':
            second_status = 'on'
        else:
            second_status = 'off'
    with open(filename, 'w') as f:
        print(first_status, second_status)
        f.write(f"{first_status},{second_status}")
    return redirect(url_for('admin_dashboard', admin_username=request.form['admin']))


# @app.route('/admin_dashboard/<admin_username>/user_stats/<user_username>')
# def user_stats(admin_username, user_username):
#     if 'username' not in session or session['username'] != admin_username:
#         return redirect(url_for('login'))
#     users = load_users()
#     if admin_username not in users or users[admin_username]['access_level'] != 'admin':
#         abort(404)
#     if user_username not in users:
#         abort(404)
#
#     # здесь собираем статистику для пользователя user_username
#     # и передаем ее в шаблон для отображения
#     user_stats = {
#         'username': user_username,
#         'field1': "asfsaafsasaf",  # заполни данные для поля 1
#         'field2': "asfsaafsasasdadaf",  # заполни данные для поля 2
#     }
#     return render_template('user_stats.html', username=admin_username, user_username=user_username, user_stats=user_stats)
@app.route('/download')
def download_file():
    user = request.args.get('username')
    print('Пользователь {} загрузил выписку'.format(user))
    filename = f"user_data/userStatus/{user}.txt"
    with open(filename, 'r') as f:
        data = f.read()
    first_status, second_status = data.split(',')
    second_status = 'off'
    with open(filename, 'w') as f:
        f.write(f"{first_status},{second_status}")
    return send_file('static/pdf/{}.pdf'.format(user), as_attachment=True)


@app.route('/owner_name/<owner_name>', methods=['GET', 'POST'])
def owner_dashboard(owner_name):
    calc = on_button_update()
    ampgen = []
    for i in range(30):
        ampgen.append(1 if calc[i] else 0)
    for i in range(29, 45):
        if (i < 33):
            ampgen.append(4 if calc[i] else 1)
        elif (i < 36):
            ampgen.append(1 if calc[i] else 2)
        elif (i < 40):
            ampgen.append(2 if calc[i] else 3)
        else:
            ampgen.append(3 if calc[i] else 4)
    users = load_users()
    all_users = []
    for username, data in users.items():
        if username == "owner" or username == "username2":
            continue
        filename = f"user_data/{username}.txt"
        with open(filename, 'r') as file:
            data = file.readlines()
        filename = f"user_data/userStatus/{username}.txt"
        with open(filename, 'r') as file:
            data = file.readlines()
        onoff = data[0].split(',')[0]
        payinfo = data[0].split(',')[1]
        user_info = {
            'username': username,
            'on/off': onoff,
            'payinfo': payinfo
        }
        all_users.append(user_info)
    print(all_users)

    return render_template('operator_dashboard.html', username=owner_name, all_users=all_users, ampgen=ampgen)


@app.route('/button_pressed_owner', methods=['GET', 'POST'])
def button_pressed_owner():
    print(1)
    username = request.form['username']
    filename = f"user_data/userStatus/{username}.txt"
    with open(filename, 'r') as f:
        data = f.read()
    first_status, second_status = data.split(',')
    if request.form['action'] == '1':
        if (first_status == 'off'):
            first_status = 'on'
        else:
            first_status = 'off'
    with open(filename, 'w') as f:
        print(first_status, second_status)
        f.write(f"{first_status},{second_status}")
    return redirect(url_for('owner_dashboard', owner_name=request.form['admin']))


if __name__ == '__main__':
    app.run(debug=1)
