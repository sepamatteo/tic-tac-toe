'''
code author : Matteo Sepa
contact : sepamatteo@protonmail.me
website : sepamatteo.github.io

Software released under GNU GPLv3 license
'''

import sys
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt
import socket
import threading
import mariadb
from datetime import datetime


class SocketChat:
    def __init__(self):
        self.nickname = ""
        # Server Ip and Port
        self.IP = "127.0.0.1"
        self.PORT = 12345
        self.client_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM
        )

    def receive(self):
        message = self.client_socket.recv(1024).decode("utf-8")
        return message

    def write(self, msg: str):
        message = msg
        self.client_socket.send(message.encode("utf-8"))
        if message.startswith("/"):
            self.handleCommand(message[1:])

    def handleCommand(self, command: str):
        if command == "exit":
            return 404  # status code for exit


class Example(QWidget):

    winning_states = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    def __init__(self):
        super().__init__()
        self.player = ""
        self.turn = "x"
        self.initUI()
        self.p1_score = 0
        self.p2_score = 0
        self.chat_object = SocketChat()
        self.chat_object.client_socket.connect(
            (self.chat_object.IP, self.chat_object.PORT)
        )
        self.player = self.chat_object.receive()
        print(f"player {self.player}")
        self.player_label.setText("{}\nGiocatore : ".format(self.player))

        if self.player != self.turn:
            self.otherPalyerTurn()

    def initUI(self):
        self.game_size = 3
        self.buttons = [
            [],
            [],
            [],
        ]
        grid = QGridLayout()
        self.setLayout(grid)

        # buttons
        for i in range(self.game_size):
            for j in range(self.game_size):
                button = QPushButton()
                button.setFixedSize(200, 200)
                button.clicked.connect(self.takeTurn(button, i, j))
                font = button.font()
                font.setPointSize(60)
                button.setFont(font)
                grid.addWidget(button, i, j)
                self.buttons[i].append(button)

        # turn label
        self.turn_label = QLabel(
            "{}\nE' il turno di : ".format(SocketChat().nickname))
        self.player_label = QLabel("{}\nGiocatore".format(self.player))
        font = self.turn_label.font()
        font.setPointSize(20)
        self.turn_label.setFont(font)
        grid.addWidget(self.turn_label, self.game_size + 1, 0)
        grid.addWidget(self.player_label, self.game_size + 2, 0)
        self.turn_label.setAlignment(Qt.AlignCenter)

        # newgame button
        button = QPushButton("Reset")
        font = button.font()
        font.setPointSize(15)
        button.setFont(font)
        button.clicked.connect(
            lambda: self.writeToDbServer(self.p1_score, self.p2_score))
        button.clicked.connect(self.newGame)
        grid.addWidget(button, self.game_size + 1, 1)

        # who wins label
        self.player_won_label = QLabel()
        font = self.player_won_label.font()
        font.setPointSize(15)
        self.player_won_label.setFont(font)
        grid.addWidget(self.player_won_label, self.game_size + 1, 2)
        self.player_won_label.setAlignment(Qt.AlignCenter)

    # method that writes the game results into a SQL database
    def writeToDbServer(self, p1_score, p2_score):

        date = datetime.today().strftime("%Y-%m-%d")  # gets game date

        # Connect to MariaDB Platform
        conn = mariadb.connect(
            user="tictactoeuser",
            password="password",
            host="localhost",
            database="tictactoe")
        cur = conn.cursor()

        # insert data into the SQL table
        try:
            statement = (
                "INSERT INTO results (p1_score,p2_score,date) "
                "VALUES (%s,%s,%s)"
                )
            items_to_insert = (p1_score, p2_score, date)

            cur.execute(statement, items_to_insert)
            conn.commit()
            # print("data successfully written")
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        conn.close()  # closes connection

    # method that starts a new game
    def newGame(self):
        for row in self.buttons:
            for btn in row:
                btn.setText("")

    # method that checks game state
    def checkGame(self):
        win = ""
        for win_state in Example.winning_states:
            i, j = win_state[0]
            state = self.buttons[i][j].text()
            if state == "":
                continue
            for i, j in win_state:
                if state != self.buttons[i][j].text():
                    break
            else:
                win = state
                print(f"'{win}' vince")
                self.player_won_label.setText("{} ha vinto".format(win))
                if win == 'x':
                    self.p1_score = self.p1_score + 1
                else:
                    self.p2_score = self.p2_score + 1
                self.newGame()

        if win == "":
            empty = False
            for row in self.buttons:
                for btn in row:
                    if btn.text() == "":
                        empty = True

            if not empty:
                print("draw")
                self.newGame()

    def _otherPalyerTurn(self):
        message = self.chat_object.receive()
        i, j = map(lambda x: int(x), message.split(" "))
        self.buttons[i][j].setText(self.turn)
        self.toggle_turn()
        self.checkGame()

    def otherPalyerTurn(self):
        threading.Thread(target=self._otherPalyerTurn).start()

    def toggle_turn(self):
        if self.turn == "x":
            self.turn = "o"
        else:
            self.turn = "x"
        self.turn_label.setText("{}\nTurn".format(self.turn))

    def endTurn(self):
        self.toggle_turn()
        self.checkGame()
        self.otherPalyerTurn()

    def takeTurn(self, button: QPushButton, i, j):
        def action():
            if self.player != self.turn:
                return
            if button.text() == "" and button.text() != self.player:
                button.setText(self.player)
                self.chat_object.write(f"{i} {j}")
                self.endTurn()

        return action


def main():
    app = QApplication([])
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
