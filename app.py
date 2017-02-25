from flask import Flask, render_template, request, session, flash, redirect, url_for
import datetime
import urllib.request
import urllib
import json
import requests


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='development key',
))


# url = 'https://raw.githubusercontent.com/rrlero/git-blog-content/master'
# x = urllib.request.urlopen('https://api.github.com/repos/rrlero/git-blog-content/contents/')
# y = x.read()
# y = json.loads(y)
# for el in y:
#     print(el['name'])


# считываем с репозитория git-blog-content файл README.md и читаем в переменную file
def get_file(git_name, git_repository):
    list_git_files = []
    git_objects = requests.get('https://api.github.com/repos/%s/%s/contents/' % (git_name, git_repository))
    git_objects = git_objects.json()
    if str(type(git_objects)) == "<class 'dict'>":
        session['logged_in'] = False
        return False
    for git_object in git_objects:
        url = git_object['download_url']
        val = {}
        s = git_object['name'].rfind('.')
        if s != -1:
            val['date'] = git_object['name'][0: s]
        else:
            val['date'] = git_object['name']
        try:
            val['date'] = datetime.datetime.strptime(val['date'], "%H:%M %d-%m-%Y")
        except:
            val['date'] = 'No date'
        val['title'] = 'No title'
        resource = requests.get(url)
        data = resource.content.decode('utf-8')
        data = [i for i in data.split('\n')]
        data.remove('')
        val['text'] = ''
        if len(data) > 5:
            for i in range(5):
                key, string = test_string(data[i])
                val[key] = string
            for i in range(5, len(data)):
                val['text'] = val['text'] + ' ' + data[i]
        else:
            val['text'] = 'your file not in right format'
        list_git_files.append(val)
    return sorted(list_git_files, key=lambda d: str(d['date']), reverse=True)


def test_string(test):
    if '---' in test:
        return 'symbol', test
    if 'title' in test and ':' in test:
        return 'title', test.split(':')[1].strip()
    if 'tegs' in test and ':' in test:
        return 'tegs', test.split(':')[1]
    if 'layout' in test and ':' in test:
        return 'layout', test.split(':')[1]


@app.route('/index')
@app.route('/')
def homepage():
    return render_template('base.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('homepage'))


@app.route('/login', methods=['POST'])
def login():
    if request.form['git_name'] and request.form['git_repository_blog']:
        session['logged_in'] = True
        git_name = request.form['git_name']
        git_repository_blog = request.form['git_repository_blog']
        return redirect(url_for('blog', git_name=git_name, git_repository_blog=git_repository_blog))
    else:
        session['logged_in'] = False
        return redirect(url_for('homepage'))


@app.route('/<git_name>/<git_repository_blog>/')
def blog(git_name, git_repository_blog):
    session['logged_in'] = True
    file = get_file(git_name, git_repository_blog)
    if file:
        return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file)
    else:
        session['logged_in'] = False
        flash('No such name or repository or both')
        return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')