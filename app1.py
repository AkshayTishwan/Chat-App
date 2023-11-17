# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, login_required, current_user
from db import get_user, login_user, logout_user

# Create a Flask web application
app = Flask(__name__)
app.secret_key = "my secret key"
# Create a SocketIO instance and associate it with the Flask app
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Define a route for the home page
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)

        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Failed to login!'
    return render_template('login.html', message=message)

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Define a route for the chat page
@app.route('/chat')
@login_required
def chat():
    # Get the username and room from the query parameters
    username = request.args.get('username')
    room = request.args.get('room')

    # If both username and room are provided, render the chat.html template
    if username and room:
        return render_template('chat.html', username=username, room=room)
    # If either username or room is missing, redirect to the home page
    else:
        return redirect(url_for('home'))
        

# Define a SocketIO event handler for sending messages
@socketio.on('send_message')
def handle_send_message_event(data):
    # Log the message information
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'], data['room'], data['message']))
    # Broadcast the message to all clients in the specified room
    socketio.emit('receive_message', data, room=data['room'])

# Define a SocketIO event handler for joining a room
@socketio.on('join_room')
def handle_join_room_event(data):
    # Log the join room announcement
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    # Join the specified room
    join_room(data['room'])
    # Broadcast the join room announcement to all clients in the room
    socketio.emit('join_room_announcement', data, room=data['room'])

# Define a SocketIO event handler for leaving a room
@socketio.on('leave_room')
def handle_leave_room_event(data):
    # Log the leave room announcement
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    # Leave the specified room
    leave_room(data['room'])
    # Broadcast the leave room announcement to all clients in the room
    socketio.emit('leave_room_announcement', data, room=data['room'])


@login_manager.user_loader
def load_user(username):
    return get_user()

# Run the Flask application with the SocketIO server
if __name__ == '__main__':
    # Run the application in debug mode
    socketio.run(app, debug=True)
