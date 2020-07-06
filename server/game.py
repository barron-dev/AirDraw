import random
import threading


class Player:
    def __init__(self, _id, name):
        self.id = _id
        self.name = name
        self.score = 0

    def add_score(self, amount):
        self.score += amount


class Game:
    def __init__(self, rounds):
        self.rounds = rounds
        self.currentRound = 1
        self.currentWord = ''
        self.wordHistory = []
        self.guessIds = []
        self.drawingIndex = -1
        self.playerList = []
        self.ended = False

    def guess_attempt(self, _id, word):
        if _id in self.guessIds or not self.check_word(word):
            return False
        p = self.get_player(_id)
        p.add_score(220 - self.guess_count() * 20)
        self.guessIds.append(_id)
        return True

    def check_word(self, word):
        return word.lower() == self.currentWord.lower()

    def update_drawing_score(self):
        try:
            to_add = 220 / self.player_count() * self.guess_count()
            self.current_player().add_score(to_add)
        except:
            pass

    def set_word(self, word):
        self.currentWord = word
        self.wordHistory.append(word)

    def next_round(self):
        if self.currentRound < self.rounds:
            self.currentRound += 1
            self.drawingIndex = -1
            return True
        return False

    def next_player(self):
        self.update_drawing_score()
        if self.drawingIndex < self.player_count() - 1:
            self.drawingIndex += 1
            self.guessIds.clear()
            return self.current_player()
        if self.next_round():
            return self.next_player()
        #return None
        else:
            self.ended = True

    def guess_count(self):
        return len(self.guessIds)

    def all_guessed(self):
        return len(self.guessIds) == len(self.playerList) - 1

    def add_player(self, _id, name):
        self.playerList.append(Player(_id, name))

    def current_player(self):
        if not self.ended:
            return self.playerList[self.drawingIndex]
        return None

    def remove_player(self, p):
        self.playerList.remove(p)

    def get_player(self, _id):
        for p in self.playerList:
            if p.id == _id:
                return p

    def player_count(self):
        return len(self.playerList)

    def get_random_word(self):
        with open('words.txt') as file:
            lines = file.readlines()
        while True:
            word = random.choice(lines).strip()
            if word not in self.wordHistory:
                break
        return word

    def three_words(self):
        words = []
        for _ in range(3):
            while True:
                new = self.get_random_word()
                if new not in words:
                    break
            words.append(new)
        return words

    def get_scores(self):
        temp = []
        for p in self.playerList:
            temp.append({'id': p.id, 'score': p.score})
        return temp

    def get_hint(self):
        hint = ''
        for _ in range(len(self.currentWord)):
            hint += '_ '
        return hint[:-1]

    def jsonify(self):
        temp = []
        for p in self.playerList:
            temp.append({'id': p.id, 'name': p.name})
        return temp


class Timer:
    def __init__(self):
        self.running = False

    def start(self, secs, func):
        self.t = threading.Timer(secs, func)
        self.t.start()
        self.running = True

    def cancel(self):
        if self.running:
            print('cancelling timer')
            self.running = False
            self.t.cancel()
