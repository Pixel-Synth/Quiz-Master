from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/',methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/quiz')
def quiz():
    subject = request.args.get('subject')
    topic = request.args.get('topic')
    return render_template('quiz.html', subject=subject, topic=topic)

if (__name__ == '__main__'):
    app.run(debug=True)