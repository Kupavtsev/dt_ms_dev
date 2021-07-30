from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pkg_resources
import uvicorn

# ====== FLASK AND MAIN IMPORTS ======
import psycopg2.extras
from datetime import timedelta

import os
# =================================================================================
# from flask_cors import CORS #comment this on deployment
# =================================================================================


# import config as config
from config import PG_LOGIN, PG_PASSWORD
from app_yandex import get_data



# BASE Connection
# try:
#     engine = create_engine(
#         f'postgresql://{PG_LOGIN}:{PG_PASSWORD}@localhost:5432/antipodpiska')           # Development
#         # f'postgresql://{PG_LOGIN}:{PG_PASSWORD}@db:5432/antipodpiska')                # Production
# except:
#     print("Can't create 'engine")

# FAST API
app = FastAPI()
app.mount("/static_html", StaticFiles(directory=pkg_resources.resource_filename(__name__, 'static_html')), name="static_html")              # FASTAPI

# =================================================================================
# CORS(app) #comment this on deployment
# =================================================================================
# app.config.from_object(config)
# db = SQLAlchemy(app)


base_url = "/"                                      # FASTAPI

@app.get("/", include_in_schema=False)              # FASTAPI
async def index():                                   # FASTAPI
    
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
    # return render_template('index.html')
    return HTMLResponse(pkg_resources.resource_string(__name__, 'static_html/index.html'))   # FASTAPI


# class Item(BaseModel):
#     mail_service : str
#     login : str
#     password : str
#     keyWords : str


# @app.route('/account', methods=['POST'])
@app.post('/account')
async def post( data : dict):
    mail_service = data['mail_service']
    login = data['login']
    password = data['password']
    keys_list = data['keyWords']
    keys_list = keys_list.split()

    
    # from sqlalchemy_engine.account import mail_service, login, password
    # Возвращает словарь и помещает его в БД
    get_data(mail_service, login, password, keys_list)          # app_yandex.py

        

    try:
        return {'status': 'ok'}, 200
    except:
        return {'status': 'fail'}, 400


# @app.route('/check', methods=['GET'])
# def execute_SQL():
    # We use 'sqlalchemy' to get data from DB
    # with engine.connect() as connection:
    #     connection.execute(text("DELETE FROM public.anti WHERE ctid NOT IN (SELECT max(ctid) FROM public.anti GROUP BY public.anti.*);"))
        # result = connection.execute(text("SELECT * from public.anti;"))

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
    #     result_list = []
    #     for row in result:
    #         dict_key = {}
    #         dict_key["Send Date"] = row['send_date']
    #         dict_key["sender"] = row['email']
    #         dict_key["Subscription"] = row['subscription']
    #         # dict_key["Recipient"] = row['recipient']
    #         result_list.append(dict_key)
       
    # return jsonify(result_list)


TWONY_TWO_DAYS = timedelta(22)

# class Data(BaseModel):                                  # FASTAPI
#     login: str

@app.get('/senders/{user}')                                    # FASTAPI
async def get_latest_sender(user: str):                           # FASTAPI

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

    
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    # cur.execute('DELETE FROM public.anti;')

    # This sql delete all equal rows!
    cur.execute("DELETE FROM public.anti WHERE ctid NOT IN (SELECT max(ctid) FROM public.anti GROUP BY public.anti.*);")
    print(cur.execute(
        f"""
        SELECT send_date, email, subscription, recipient from public.anti WHERE subscription > 0 AND recipient='{user}';
        """
        ))
    result = cur.fetchall()

    result_list_total_data : list = []
    result_list : list = []
    result_list_periods : list = []
    for row in result:
        dict_key = {}
        dict_key["Send Date"] = row['send_date']
        # print(dict_key["Send Date"])
        dict_key["sender"] = row["email"]
        dict_key["Subscription"] = row["subscription"]
        dict_key["Recipient"] = row['recipient']
        result_list.append(dict_key)


    #   =============================================
    #   ====== Объеденяем даты по получателям =======
    #   =============================================
    # Словарь с отправителями из БД
    senders_periods_dict : dict = {}
   
    # Каждый словарь массива отправителей
    # 1
    for each_sender in range(len(result_list)):
        # print(result_list[each_sender])
        senders_periods_dict[result_list[each_sender]['sender']] = [[]]

    # Если ключ в senders_periods_dict равен значению sender в dict_key,
    # то поместить значение даты в массив значений senders_periods_dict
    for key, dates in sorted(senders_periods_dict.items()):
        for each_dict in range(len(result_list)):
            for each_sender in dates:
                if key == result_list[each_dict]['sender']:
                    each_sender.append(result_list[each_dict]['Send Date'])

     
    print('===================')
    # Проверка на периодичность
    quantity_of_periods = 0
    for k,v in senders_periods_dict.items():
        list_of_dates = v[0]
        
        if len((v[0])) > 1:
            # print('pass')
            if list_of_dates[0] - list_of_dates[1] > TWONY_TWO_DAYS:
                periods_dict_key = {}
                periods_dict_key['Sender of Subscription'] = k
                periods_dict_key['Last Send Date'] = list_of_dates[0]
                periods_dict_key['Periods'] = len(list_of_dates)
                # print('\n')
                # print(k, ' : ')
                # print(v)
                # print('Subscription')
                quantity_of_periods += 1
                result_list_periods.append(periods_dict_key)
            else:
                pass
 
    
    #   ========================================
    #   ====== Даты по получателям конец =======
    #   ========================================

    result_list_total_data.append(result_list)
    result_list_total_data.append(result_list_periods)


    cur.close()
    conn.close()

    # print(result_list)
    # print(result_list_total_data)
    # return result_list                            # this is for anykeys only
    return result_list_total_data 




if __name__ == '__main__':


    uvicorn.run('app:app', host='0.0.0.0', port=5000, reload=True)
    # app.run(port=5000, host='0.0.0.0')
    # app.run(host='34.141.12.119', port=5000 )
