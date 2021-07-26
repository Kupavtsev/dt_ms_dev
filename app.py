import psycopg2.extras


import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
# =================================================================================
# from flask_cors import CORS #comment this on deployment
# =================================================================================


import config as config
from config import PG_LOGIN, PG_PASSWORD
from app_yandex import get_data

# # __init__.py
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(APP_DIR, 'static_html/js/') # Where your webpack build output folder is
TEMPLATE_FOLDER = os.path.join(APP_DIR, 'static_html/') # Where your index.html file is located


# from models import Sender



# BASE Connection
# try:
#     engine = create_engine(
#         f'postgresql://{PG_LOGIN}:{PG_PASSWORD}@localhost:5432/antipodpiska')           # Development
#         # f'postgresql://{PG_LOGIN}:{PG_PASSWORD}@db:5432/antipodpiska')                # Production
# except:
#     print("Can't create 'engine")




app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
# app = Flask(__name__)
# =================================================================================
# CORS(app) #comment this on deployment
# =================================================================================
app.config.from_object(config)
db = SQLAlchemy(app)
# from models import *





@app.route('/', methods=['GET'])
def index():
    
    # We use 'sqlalchemy' to get data from DB
    # with engine.connect() as connection:
    #     result = connection.execute(text("SELECT * from public.anti;"))
    #     # result = connection.execute(text("SELECT sender from public.anti;"))
    #     result_dict = {}
    #     c = 1
    #     for row in result:
    #         # print(row)
    #         # print("sender:", row['sender'])
    #         dict_key = {}
    #         dict_key["sender"] = row['email']
    #         dict_key["Subscription"] = row['subscription']
    #         c += 1
    #         result_dict[c] = dict_key
   
    # return jsonify({
    #      'sender': [p.to_dict() for p in senders],
    #  })
        # print(result_dict)
    # return jsonify(result_dict)
    return render_template('index.html')



@app.route('/account', methods=['POST'])
def post():
    data = request.get_json()
    mail_service = data['mail_service']
    login = data['login']
    password = data['password']
    keys_list = data['keyWords']
    keys_list = keys_list.split()

    
    # from sqlalchemy_engine.account import mail_service, login, password
    get_data(mail_service, login, password, keys_list)

    

    try:
        return {'status': 'ok'}, 200
    except:
        return {'status': 'fail'}, 400


@app.route('/check', methods=['GET'])
def execute_SQL():
    # We use 'sqlalchemy' to get data from DB
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM public.anti WHERE ctid NOT IN (SELECT max(ctid) FROM public.anti GROUP BY public.anti.*);"))
        result = connection.execute(text("SELECT * from public.anti;"))

        # result = connection.execute(text("SELECT sender from public.anti;"))
        
        # ------------ Logic for Dict ---------------
        # result_dict = {}
        # c = 0
        # for row in result:
        #     # print(row)
        #     # print("sender:", row['sender'])
        #     dict_key = {}
        #     dict_key["sender"] = row['email']
        #     dict_key["Subscription"] = row['subscription']
        #     c += 1
        #     result_dict[c] = dict_key
        # print(result_dict)
        # print(type(result))
    # return result_dict
        
        # --------------- Logic for Array ----------------
        result_list = []
        for row in result:
            dict_key = {}
            dict_key["Send Date"] = row['send_date']
            dict_key["sender"] = row['email']
            dict_key["Subscription"] = row['subscription']
            # dict_key["Recipient"] = row['recipient']
            result_list.append(dict_key)
       
    return jsonify(result_list)




@app.route('/senders', methods=['GET'])
def get_latest_sender():

    user = request.args.get('login')
    # user = request.args['login']
    # print(user)

    try:
        conn = psycopg2.connect(
            user = PG_LOGIN,
            password = PG_PASSWORD,                           
            database = 'antipodpiska',
            host = 'localhost',                          # Development
            # host = 'db',                                # Production
            port = 5432,    
        )
    except Exception as ex:
        print(' /// ----- I am unable to connect to the database ----- ///', ex)
        raise ex

    
    # cur = conn.cursor()
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    # cur.execute('DELETE FROM public.anti;')

    # This sql delete all equal rows!
    cur.execute("DELETE FROM public.anti WHERE ctid NOT IN (SELECT max(ctid) FROM public.anti GROUP BY public.anti.*);")
    cur.execute(
        f"""
        SELECT send_date, email, subscription, recipient from public.anti WHERE subscription > 0 AND recipient='{user}';
        """
        )
    result = cur.fetchall()

    result_list = []
    for row in result:
        dict_key = {}
        dict_key["Send Date"] = row['send_date']
        dict_key["sender"] = row["email"]
        dict_key["Subscription"] = row["subscription"]
        dict_key["Recipient"] = row['recipient']
        result_list.append(dict_key)
    

    cur.close()
    conn.close()

    return jsonify(result_list)



if __name__ == '__main__':


    app.run(port=5000, host='0.0.0.0')
    # app.run(host='34.141.12.119', port=5000 )

