from flask import Flask, render_template, request, jsonify,Response
import pymysql
import threading
import datetime
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, GRU, Embedding, LSTM, Bidirectional
from tensorflow.python.keras.optimizers import RMSprop
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
from tensorflow.python.keras.preprocessing.text import Tokenizer
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
import re
import pkuseg
import pandas as pd
from gensim.models import KeyedVectors# gensim用来加载预训练词向量

max_tokens = 58
seg = pkuseg.pkuseg(model_name='web')  # 程序会自动下载所对应的细领域模型
#导入停用词
stopwords=pd.read_csv("D:/Work/大三下/大三暑假短学期/数据处理/stopwords/stopwords.txt",index_col=False,sep="\t",quoting=3,names=['stopword'], encoding='utf-8')
stopwords = stopwords.stopword.values.tolist()#转为list形式
cn_model = KeyedVectors.load_word2vec_format('D:/Work/大三下/大三暑假短学期/数据处理/embeddings/sgns.weibo.bigram',
                                             binary=False,
                                             unicode_errors="ignore")
model = tf.keras.models.load_model('D:/Work/大三下/大三暑假短学期/数据处理/LSTM_rumor_model_58.h5')

from flask_cors import *
app = Flask(__name__)
CORS(app, supports_credentials=True)
def predict_rumor_LSTM(text):
    print(text)
    # 去标点
    text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "",text)
    # 分词
    cut = seg.cut(text)
    #去除停用词
    cut_clean=[]
    for word in cut:
        if word in stopwords:
            continue
        cut_clean.append(word)
    # tokenize
    for i, word in enumerate(cut_clean):
        try:
            cut_clean[i] = cn_model.vocab[word].index
            if cut_clean[i] >= 50000:
                cut_clean[i] = 0
        except KeyError:
            cut_clean[i] = 0
    # padding
    tokens_pad = pad_sequences([cut_clean], maxlen=max_tokens,
                           padding='pre', truncating='pre')
    # 预测
    dic={0:'谣言',1:'真言'}
    result = model.predict(x=tokens_pad)
    coef = result[0][0]
    if coef >= 0.5:
        return dic[1]
    else:
        return dic[0]

#  显示用户言论列表
@app.route('/api/article/list', methods=['POST', 'GET'])
def getlist():
    data = eval(request.data.decode())
    Page = data['Page']
    Personal = data['Personal']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from article where personal_id = %s order by id DESC',Personal)  # 获取操作数据库的游标
    results = cursor.fetchall()
    alllist = []
    for i in range(len(results)):
        if(i<Page*10 and i >=Page*10-10):
            datalist = {"ID":results[i][0],"CreatedAt":results[i][1],"content":results[i][2],"Tags":results[i][3],"Pensonal":results[i][4],"Pensonalname":results[i][5],"Categories":results[i][6]}
            alllist.append(datalist)
    midlist = {"List":alllist,"Total":len(results)}
    finallist = {"Code":0, "Msg":"","Data":midlist,}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(finallist)

#  显示所有言论列表
@app.route('/api/article/allarticle', methods=['POST', 'GET'])
def getallarticle():
    data = eval(request.data.decode())
    Page = data['Page']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from article order by id DESC')  # 获取操作数据库的游标
    results = cursor.fetchall()
    alllist = []
    for i in range(len(results)):
        if(i<Page*10 and i >=Page*10-10):
            datalist = {"ID":results[i][0],"CreatedAt":results[i][1],"content":results[i][2],"Tags":results[i][3],"Pensonal":results[i][4],"Pensonalname":results[i][5],"Categories":results[i][6]}
            alllist.append(datalist)
    midlist = {"List":alllist,"Total":len(results)}
    finallist = {"Code":0, "Msg":"","Data":midlist,}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(finallist)

#  显示言论详情
@app.route('/api/article/fetch', methods=['POST', 'GET'])
def articleFetch():
    data = eval(request.data.decode())
    ID = data['ID']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from article where id = %s',ID)  # 获取操作数据库的游标
    results = cursor.fetchall()
    datalist = {}
    for i in range(len(results)):
        datalist = {"ID":results[i][0],"CreatedAt":results[i][1],"Content":results[i][2],"Tags":results[i][3],"Pensonal":results[i][4],"Title":results[i][5],"Categories":results[i][6],"GithubUrl": "http://localhost:12322/#/welcome/"+str(results[i][4])}
    finallist = {"Code":0, "Msg":"","Data":datalist,}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(finallist)

#  显示用户留言列表
@app.route('/api/article/comment', methods=['POST', 'GET'])
def getUserComment():
    data = eval(request.data.decode())
    Page = data['Page']
    Personal = data['Personal']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from user_comment where commented_id = %s',Personal)  # 获取操作数据库的游标
    results = cursor.fetchall()
    alllist = []
    for i in range(len(results)):
        if(i<Page*10 and i >=Page*10-10):
            datalist = {"ID":results[i][0],"CreatedAt":results[i][1],"content":results[i][2],"commented_id":results[i][3],"Pensonal":results[i][4],"Pensonalname":results[i][5]}
            alllist.append(datalist)
    midlist = {"List":alllist,"Total":len(results)}
    finallist = {"Code":0, "Msg":"","Data":midlist,}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(finallist)

#  显示言论的评论列表
@app.route('/api/comment/list', methods=['POST', 'GET'])
def getAtricleComment():
    data = eval(request.data.decode())
    articleId = data['ArticleID']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from article_comment where article_id = %s',articleId)  # 获取操作数据库的游标
    results = cursor.fetchall()
    alllist = []
    picture = ["http://pic2.zhimg.com/50/v2-d0e0847a32fbe01eb19e8a4834d60ecd_hd.jpg","https://pic4.zhimg.com/80/v2-8b03829610d7f875a931fe8c7ada4926_1440w.jpg?source=1940ef5c",
               "https://pic2.zhimg.com/80/v2-7cea67f01f6a3bfb14f0266ca875c77e_1440w.jpg?source=1940ef5c","https://pic2.zhimg.com/80/v2-c4a5d55093898b3bfe205447613f2055_1440w.jpg?source=1940ef5c",
               "https://pic2.zhimg.com/80/v2-9e082ad6373b8c1499a474230533ce7a_1440w.jpg?source=1940ef5c","https://pic2.zhimg.com/80/v2-3acf294099fb0b052b1a1ffd5c523dc9_1440w.jpg?source=1940ef5c",
               "https://pic1.zhimg.com/80/v2-78438adb9dd16cda8a8384e1662cbd74_1440w.jpg?source=1940ef5c","https://pic1.zhimg.com/80/v2-defdc3aee4c844bb0db09cd86e855cb0_1440w.jpg?source=1940ef5c"]
    for i in range(len(results)):
        datalist = {"ID":results[i][0],"CreatedAt":results[i][1],"Content":results[i][2],"ArticleID":results[i][3],"Pensonal":results[i][4],"Username":results[i][5],
                    "AvatarUrl": picture[i%8],"GithubUrl": "http://localhost:12322/#/welcome/"+str(results[i][4]),"GitUserID": 55419701}
        alllist.append(datalist)
    midlist = {"List":alllist,"Total":len(results)}
    finallist = {"Code":0, "Msg":"","Data":midlist}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(finallist)

#  显示标签列表
@app.route('/api/category/list', methods=['POST', 'GET'])
def getCategory():
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from category')  # 获取操作数据库的游标
    results = cursor.fetchall()
    alllist = []
    for i in range(len(results)):
        datalist = {"ID":results[i][0],"Name":results[i][1]}
        alllist.append(datalist)
    midlist = {"List":alllist,"Total":len(results)}
    finallist = {"Code":0, "Msg":"","Data":midlist,}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(finallist)

#  动态、留言板数量
@app.route('/api/article/count', methods=['POST', 'GET'])
def getcomments():
    data = eval(request.data.decode())
    Personal = data['Personal']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)

    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from article')  # 获取操作数据库的游标
    results = cursor.fetchall()
    Sum = len(results)   # 总数量

    count = cursor.execute('select * from article where personal_id = %s',Personal)  # 获取操作数据库的游标
    results = cursor.fetchall()
    articleSum = len(results)   # 动态数量

    count = cursor.execute('select * from user where userid = %s',Personal)  # 获取操作数据库的游标
    results = cursor.fetchall()
    Name = results[0][2]   # 姓名

    trueSum = 0
    for i in range(len(results)):
        if(results[i][3] == "真言"):
            trueSum = trueSum+1
    data = {"articleSum": articleSum,"commentSum": Sum,"true": trueSum,"false": len(results)-trueSum,"userName": Name}
    datalist = {"Code":0,"Msg":"","Data":data}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(datalist)

#  登陆
@app.route('/login', methods=['POST', 'GET'])
def login():
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    userId = request.form.get('userId')
    password = request.form.get('password')
    # print(userId,password)
    # 获取数据库的游标
    cursor = cur = db.cursor()
    # 获取操作数据库的游标
    count = cursor.execute('select * from user where userId = %s and password = %s',(userId,password))
    results = cursor.fetchall()

    if(count == 0):
        datalist = {"port":401, "message":"账号或密码错误!"}
    else:
        for i in range(len(results)):
            datalist = {"port":200,"userId":results[i][1],"password":results[i][3],"userName":results[i][2]}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(datalist)

#  注册
@app.route('/register', methods=['POST', 'GET'])
def register():
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    userId = request.form.get('userId')
    password = request.form.get('password')
    userName = request.form.get('userName')

    # 获取数据库的游标
    cursor = cur = db.cursor()
    # 获取操作数据库的游标
    count = cursor.execute("select * from user where userid = '" + userId+"'")
    count2 = cursor.execute("select * from user where username = '" + userName+"'")
    results = cursor.fetchall()
    if(count != 0):
        datalist = {"port": 401, "message": "账号已存在!"}
    elif(count2 != 0):
        datalist = {"port": 401, "message": "昵称已被占用!"}
    else:
        # 获取操作数据库的游标
        count = cursor.execute('insert into user(userid,password,username) VALUES(%s,%s,%s)',(userId,password,userName))
        results = cursor.fetchall()
        datalist = {"port": 200, "message": "注册成功!","userId": userId,"password": password,"userName": userName}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(datalist)

#  发表言论
@app.route('/api/article/save', methods=['POST', 'GET'])
def send():
    data = eval(request.data.decode())
    content = data['HostKey']
    categories = data['CategoryIDs']

    userID = data['userID']
    userName = data['userName']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)

    # 获取数据库的游标
    cursor = cur = db.cursor()
    # 获取操作数据库的游标
    count = cursor.execute('select * from category')
    results = cursor.fetchall()
    categories = results[int(categories)-1][1]
    tags = predict_rumor_LSTM(content)
    # 获取操作数据库的游标
    count = cursor.execute('insert into article(created_at,content,tags,personal_id,personal_name,categories) VALUES(%s,%s,%s,%s,%s,%s)',(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),content,tags,userID,userName,categories))
    results = cursor.fetchall()
    datalist = { "Code": 0,"Msg": "发表成功!"}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(datalist)

#  对言论进行评论
@app.route('/api/comment/save', methods=['POST', 'GET'])
def commentSave():
    data = eval(request.data.decode())
    content = data['Content']
    articleId = data['ArticleID']
    userID = data['Userid']
    userName = data['Username']
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)

    # 获取数据库的游标
    cursor = cur = db.cursor()
    # 获取操作数据库的游标
    count = cursor.execute('select * from category')
    results = cursor.fetchall()

    # 获取操作数据库的游标
    count = cursor.execute('insert into article_comment(created_at,content,article_id,user_id,username) VALUES(%s,%s,%s,%s,%s)',(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),content,articleId,userID,userName))
    results = cursor.fetchall()
    data = {"Data": {
        "comment": {
            "ID": 58,
            "CreatedAt": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Content": content,
            "ArticleID": articleId,
            "GitUserID": 55419701,
            "Username": userName,
            "AvatarUrl": "https://avatars2.githubusercontent.com/u/55419701?v=4",
            "GithubUrl": "https://github.com/zucc-Zs",
            "ArticleTitle": "2"
        }
    }}
    datalist = { "Code": 0,"Msg": "评论成功!","Data": data}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    return jsonify(datalist)

#  用户主页
@app.route('/api/user', methods=['POST', 'GET'])
def user():
    # lock.acquire()  # 上锁
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    userId = request.form.get('userId')
    cursor = cur = db.cursor()  # 获取数据库的游标
    count = cursor.execute('select * from comments where userId = '+userId)  # 获取操作数据库的游标
    results = cursor.fetchall()
    for i in range(len(results)):
        datalist = {"userId": results[i][1], "password": results[i][3], "userName": results[i][2]}

    # 提交，不然无法保存新建或者修改的数据
    db.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    db.close()
    # lock.release()  # 解锁
    return jsonify(datalist)



if __name__ == '__main__':
    lock = threading.Lock()
    db = pymysql.connect(host="127.0.0.1", user="root", password="yys981030", db="谣言", port=3306)
    app.run(debug=True,port=8848)
