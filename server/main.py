from flask import Flask, request
from flask_socketio import SocketIO, emit1
from game import Game, Timer
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins='*')

connections = 0
round_count = 3
round_time = 10
finish_by_time = True
game = Game(round_count)
clients = {}  # Stores session ID for each user


@socketio.on('connect')
def new_connection():
    global connections
    connections += 1
    clients[request.sid] = connections
    emit('assign-id', {'id': connections, 'players': game.jsonify()})


@socketio.on('disconnect')
def disconnected():
    p = game.get_player(clients[request.sid])
    if p is not None:
        print(f"[Server] {p.name} disconnected")
        emit('user-disconnected', {'id': p.id}, broadcast=True)
        game.remove_player(p)
        del clients[request.sid]


@socketio.on('assign-name')
def add_player(data):
    game.add_player(data['id'], data['name'])
    emit('user-connected', data, broadcast=True)
    print(f"[Server] {data['name']} connected to the server")


@socketio.on('chat-message')
def handle_message(data):
    p = game.get_player(data['id'])
    print(f"[Chat] {p.name}({data['id']}): {data['text']}")
    if game.guess_attempt(data['id'], data['text']):
        print(f"[Game] {p.name} has guessed the word")
        emit('chat-message', {'type': 2, 'text': f'{p.name} has guessed the word!'}, broadcast=True)
        if game.all_guessed():
            pass
            #cancel_timer()
            #timer.cancel()
            #end_turn()
    elif not game.check_word(data['text']):
        emit('chat-message', data, broadcast=True)


# @socketio.on('done-drawing')
# def done_drawing():
#     print('the time ended')
#     if finish_by_time and clients[request.sid] == game.current_player().id:
#         print('ending turn')
#         end_turn()


@socketio.on('user-draw')
def handle_draw(data):
    emit('user-draw', data, broadcast=True)


@socketio.on('clear-board')
def clear_board():
    emit('clear-board', broadcast=True)


@socketio.on('start-game')
def start_game():
    emit('start-game', {'roundCount': round_count, 'roundTime': round_time}, broadcast=True)
    progress()


def progress():
    global game
    p = game.current_player()
    if p is not None:
        socketio.emit('next-turn', {'id': p.id, 'round': game.currentRound, 'scores': game.get_scores()})
        socketio.emit('word-selection', {'words': game.three_words()}, room=sid_by_id(p.id))
        print(f'[Game] {p.name} is now drawing')
        global finish_by_time
        finish_by_time = True
    else:
        socketio.emit('game-finished')
        game = Game(round_count)


@socketio.on('word-selected')
def word_selected(data):
    game.set_word(data['word'])
    emit('start-turn', {'hint': game.get_hint()}, broadcast=True)
    print(f"[Game] {game.current_player().name} selected the word {data['word']}")
    threading.Timer(round_time + 1, end_turn).start()
    #timer.start(round_time + 2, end_turn)


def end_turn():
    global finish_by_time
    finish_by_time = False
    socketio.emit('chat-message', {'type': 2, 'text': f'The word was {game.currentWord}'})
    game.next_player()
    threading.Timer(2, progress).start()


def cancel_timer():
    pass
    # global timer
    # timer.cancel()
    # timer = threading.Timer(round_time + 2, end_turn)
    # timer.cancel()
    #timer.start(2, end_turn)


def sid_by_id(target):
    for sid, _id in clients.items():
        if _id == target:
            return sid


if __name__ == '__main__':
    socketio.run(app)
