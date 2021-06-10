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
# and passed the special variable __name__ that holds the name of the current Python module
# __name__ means this current file. In this case, it will be main.py.
app = Flask(__name__)
'''Hence, with the Debug Mode on, 
all the application code changes will get updated right away in the development stage, eliminating the need to restart the server.'''
#debug=True allows possible Python errors to appear on the web page. This will help us trace the errors.
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'


# To store session variables on server side in within flask_session folder to know when user has logged in and left the room.
#Like Cookie, Session data is stored on client.
#The Session is the time between the client logs in to the server and logs out of the server.
'''A session with each client is assigned a Session ID. The Session data is stored on top of cookies and the server signs them cryptographically. 
For this encryption, a Flask applicati
on needs a defined SECRET_KEY.'''
Session(app)

#SocketIO is a cross-browser Javascript library that abstracts the client application from the actual transport protocol
#SocketIO instance
socketio = SocketIO(app, manage_session=False)
# False because we don't want session to manage our sessions, we want to flask to manage sessions

arr = []
y_new = []

''' @app.route is a decorator that turns a regular Python function into a Flask view function,
 which converts the function’s return value into an HTTP response to be displayed by an HTTP client, such as a web browser.
 this function will respond to web requests for the URL / i.e. main url'''
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

'''GET- if someone tries to reload the page, information will not get lost ,
most common method which can be used to send data in the unencrypted form to the server'''
#POST - Used to send HTML form data to the server. The data received by the POST method is not cached by the server.
# So essentially GET is used to retrieve remote data, and POST is used to insert/update remote data.

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

'''To start the development server we call the run() method of the Flask object.
  socketio.run() function starts a Socket.IO enabled web server.'''


# __name__ means this current file. In this case, it will be main.py.
'''The condition __name__ == "__main__" ensures that the run() method is called only 
when main.py is run as the main program. 
The run() method will not be called if you import main.py in another Python module.'''
'''socketio.run() function starts a Socket.IO enabled web server.'''

 