from flask import Flask, render_template, request
from dispatcher import dispatcher

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('form.html')


@app.route('/sendQuery', methods=['GET'])
def query():
    query_text = request.args.get('QueryField', '')
    reply = dispatcher(query_text)
    return reply


# if __name__ == '__main__':
    # execute only if run as the entry point into the program
#    main()

# command line
# export FLASK_DEBUG=1
# export FLASK_APP=main.py
# python -m flask run
