#import the Flask object from the flask package.
from flask import Flask, render_template, request, redirect, url_for, session
#to create a socket connection
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from flask import flash
import pickle

with open('sent.pkl', 'rb') as pickle_in:
     unpickled_sent = pickle.load(pickle_in)

#define Flask application instance with the name app
app = Flask(__name__)
#debug=True allows possible Python errors to appear on the web page. This will help us trace the errors.
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

#SocketIO instance
socketio = SocketIO(app, manage_session=False)
# False because we don't want session to manage our sessions, we want to flask to manage sessions

arr = []
y_new = []

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):  #if someone new user has logged in
        username = request.form['username']
        room = request.form['room']
        #Store the data in session variable
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session = session)
    else:                        # for existing user
        if(session.get('username') is not None):
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))

@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)
    arr.append(message['msg'])
    #print(arr)
    if(len(arr) > 9):
        for i in arr:
          y_prob = unpickled_sent.predict([i])
          y_new.append(int(y_prob))
		print(y_new)
        avg = sum(y_new)/len(y_new)
        print(avg)
        if (avg > 49.99):
          flash('Malicious activity detected')
        else:
          flash('No Malicious activity detected')
        del arr[:]
        del y_new[:]

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app)
'''socketio.run() function starts a Socket.IO enabled web server.'''

 
