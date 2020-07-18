from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime

app = Flask(__name__,  static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/cricketDB.db'
db = SQLAlchemy(app)

class CricketPlay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dice1 = db.Column(db.Integer, default=0)
    dice2 = db.Column(db.Integer, default=0)
    callBluf = db.Column(db.Boolean, default=False)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    def __lt__(self, other):
        return self.position < other.position

playersName = ['Sergio (que homem)', 'Cuia', 'Vivi', 'Lucas', 'Leo','Luiza de Simone', 'Rute', 'Burgao', 'Lanches', 'EaiGabi'];
playersPositions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

@app.route('/')
def index():
    cricketPlay = CricketPlay.query.all()

    if len(cricketPlay) == 0:
        cricketPlay = CricketPlay()
        db.session.add(cricketPlay)
        db.session.commit()

    players = Player.query.all()

    if len(players) == 0:
        for idx, name in playersName:
            player = Player()
            player.name = name
            db.session.add(player)
            db.session.commit()

    return render_template('index.html')

@app.route('/rolldices', methods=['POST'])
def rollDices():
    players = Player.query.order_by(Player.position).all()
    random.seed(datetime.now())

    cricketPlay = CricketPlay.query.get_or_404(1)
    cricketPlay.dice1 = random.randint(1,6)
    cricketPlay.dice2 = random.randint(1,6)
    cricketPlay.callBluf = False
    sum = calculateSum(cricketPlay.dice1, cricketPlay.dice2) 

    db.session.commit()

    return render_template('index.html',  players=players, dices=[cricketPlay.dice1, cricketPlay.dice2, sum])

@app.route('/callbluf', methods=['POST'])
def callBluf():
    players = Player.query.order_by(Player.position).all()
    cricketPlay = CricketPlay.query.get_or_404(1)
    sum = calculateSum(cricketPlay.dice1, cricketPlay.dice2) 

    cricketPlay.callBluf = True
    db.session.commit()

    return render_template('index.html', players=players, bluf=[cricketPlay.dice1, cricketPlay.dice2, sum])

@app.route('/checkBluf', methods=['GET'])
def checkBluf():
    cricketPlay = CricketPlay.query.get_or_404(1)
    sum = calculateSum(cricketPlay.dice1, cricketPlay.dice2) 

    if cricketPlay.callBluf == True:
        return 'Blefe chamado %s - %s = %s.' % (cricketPlay.dice1, cricketPlay.dice2, sum)
    else:
        return "" 

@app.route('/randomizePlayersList', methods=['POST'])
def randomizePlayersList():
    random.shuffle(playersPositions)

    players = Player.query.all()
    index = 0
    for player in players:
            player.position = playersPositions[index]
            player.points = 0
            index += 1
            db.session.commit()   

    return render_template('index.html')

@app.route('/getPlayersList', methods=['GET', 'POST'])
def getPlayersList():
    players = Player.query.order_by(Player.position).all()
    cricketPlay = CricketPlay.query.get_or_404(1)
    sum = calculateSum(cricketPlay.dice1, cricketPlay.dice2) 
    bluf = ""

    if cricketPlay.callBluf == True:
        bluf = 'Blefe chamado %s - %s = %s.' % (cricketPlay.dice1, cricketPlay.dice2, sum)

    return render_template('index.html', players=players, checkBlufInfo=bluf)

@app.route('/addPoint/<int:id>', methods=['GET', 'POST'])
def addPoint(id):
    player = Player.query.get_or_404(id)
    player.points += 1
    db.session.commit()
        
    return redirect('/getPlayersList')

def calculateSum(dice1, dice2):
    if (dice1 != 1 or dice2 != 2) and (dice1 != 2 or dice2 != 1):
        return dice1 + dice2 if dice1 != dice2 else "Par" 
    else:
        return "CRICKET"

if __name__ == "__main__":
    app.run(debug=True)