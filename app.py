from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL,MySQLdb
import re
import pickle
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if (password == user["password"]):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("predictor.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("logint.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("registert.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        gender=request.form['checkbox']
        if(gender=="on"):
            gender="MALE"
        else:gender="Female"
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email,password,gender) VALUES (%s,%s,%s,%s)",(name,email,password,gender))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return render_template("logint.html")

def preprocess(text):
    '''This function preprocesses the text'''
    preprocessed_text = []
    text = text.replace('\\r', ' ')
    text = text.replace('\\"', ' ')
    text = text.replace('\\n', ' ')
    text = re.sub('[^A-Za-z0-9]+', ' ', text)
    preprocessed_string = text.lower().strip()

    return preprocessed_string


def vectorize(text):
    '''This function takes the text and vectorizes ithe text using keras vectorizer.pkl'''
   
    vectorizer =  pickle.load(open('vectorizer.pkl', 'rb'))
    #preprocessed_string = [preprocessed_string]
    final = vectorizer.transform([text])
    
    return final


@app.route('/predict',methods=['POST'])
def predict():
    '''This function predicts the class(real or fake)'''
    text = request.form.values()
    for i in text:
        text = i
        break
    
    text = preprocess(text)
    text = vectorize(text)
    
    predictor = pickle.load(open('classifier.pkl', 'rb'))
    prob = predictor.predict_proba(text)
    cls = predictor.predict(text)
    
    if cls[0] == 'fake':
        a = round(prob[0][0], 4)
    else:
        a = round(prob[0][1], 4)
    a=a*100
    if(a>50):
        cls[0]="FAKE and unauthenticated"
    else:
        cls[0]="REAL and authenticated"
    return render_template('predictor.html', probability="Given text is {} ".format(cls[0]))

if __name__ == '__main__':
    app.secret_key = "^A%DJAJU^JJ123"
    app.run(debug=True)