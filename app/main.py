from flask import Flask
import getMatch

app = Flask(__name__)

@app.route("/match/<imgName>")
def get_match(imgName):
	return getMatch.getImg(str(imgName))
