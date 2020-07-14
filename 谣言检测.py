#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import re


# # 导入词向量模型，https://github.com/Embedding/Chinese-Word-Vectors

# In[2]:


from gensim.models import KeyedVectors


# In[3]:


cn_model = KeyedVectors.load_word2vec_format('./embeddings/sgns.weibo.bigram', 
                                             binary=False,
                                             unicode_errors="ignore")


# In[46]:


print(cn_model.vocab['心情'].index)
print(cn_model.vectors[666].shape)
print(cn_model.vectors[666])


# # 读取数据

# In[4]:


from tensorflow.python.keras.preprocessing.text import Tokenizer
from tensorflow.python.keras.preprocessing.sequence import pad_sequences


# In[5]:


weibo = pd.read_csv('./data/all_data.txt',sep='\t', names=['is_not_rumor','content'],encoding='utf-8')
print(weibo.head())

# In[6]:


content = weibo.content.values.tolist()
label=weibo.is_not_rumor.values.tolist()


# In[33]:


print(str(label[0])+'\t'+content[0])


# # 分词和tokenize，https://github.com/lancopku/PKUSeg-python

# In[7]:


import pkuseg


# In[8]:


stopwords=pd.read_csv("./stopwords/stopwords.txt",index_col=False,sep="\t",quoting=3,names=['stopword'], encoding='utf-8')
stopwords = stopwords.stopword.values.tolist()


# In[9]:


seg = pkuseg.pkuseg(model_name='web')


# In[10]:


train_tokens = []
for text in content:
    text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "",text)
    cut_list = seg.cut(text)
    cut_list_clean=[]
    for word in cut_list:
        if word in stopwords:
            continue
        cut_list_clean.append(word)
    
    #索引化
    for i, word in enumerate(cut_list_clean):
        try:
            # 将词转换为索引index
            cut_list_clean[i] = cn_model.vocab[word].index
        except KeyError:
            # 如果词不在字典中，则输出0
            cut_list_clean[i] = 0
    train_tokens.append(cut_list_clean)


# In[11]:


# 获得所有tokens的长度
num_tokens = [len(tokens) for tokens in train_tokens]
num_tokens = np.array(num_tokens)
# 取tokens平均值并加上两个tokens的标准差，
max_tokens = np.mean(num_tokens) + 2 * np.std(num_tokens)
max_tokens = int(max_tokens)
print(max_tokens)


# In[12]:


train_pad = pad_sequences(train_tokens, maxlen=max_tokens,
                            padding='pre', truncating='pre')


# In[34]:


print(train_pad)


# # 生成词向量

# In[13]:


num_words = 50000 #选择使用前50k个使用频率最高的词
embedding_dim=300 #每一个词汇都用一个长度为300的向量表示
embedding_matrix = np.zeros((num_words, embedding_dim))
for i in range(num_words):
    embedding_matrix[i,:] = cn_model[cn_model.index2word[i]]#前50000个index对应的词的词向量
embedding_matrix = embedding_matrix.astype('float32')


# In[14]:


train_pad[train_pad>=num_words ] = 0
train_target = np.array(label)


# # 训练

# In[15]:


import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, GRU, Embedding, LSTM, Bidirectional
from tensorflow.python.keras.optimizers import RMSprop
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau


# In[16]:


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(train_pad,
                                                    train_target,
                                                    test_size=0.1,
                                                    random_state=12)


# In[17]:


#序贯(Sequential)模型
model = Sequential()
# 嵌入层
model.add(Embedding(num_words,
                    embedding_dim,
                    weights=[embedding_matrix],
                    input_length=max_tokens,
                    trainable=False))
#Bidirectional包装器:双向RNN包装器
model.add(Bidirectional(LSTM(units=64, return_sequences=True)))
model.add(Bidirectional(LSTM(units=32, return_sequences=False)))
#全连接层
model.add(Dense(64, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
optimizer=Adam(lr=1e-3)


# In[18]:


import os


# In[19]:


# 建立一个权重的存储点
checkpoint_save_path="./checkpoint/rumor_LSTM.ckpt"
if os.path.exists(checkpoint_save_path+'.index'):
    print('----------load the model----------')
    model.load_weights(checkpoint_save_path)


# In[20]:


#保存参数和模型
checkpoint = ModelCheckpoint(filepath=checkpoint_save_path, monitor='val_loss',
                                      verbose=1, save_weights_only=True,
                                      save_best_only=True)


# In[21]:


# 5个epoch内validation loss没有改善则停止训练
earlystopping = EarlyStopping(monitor='val_loss', patience=5, verbose=1)

# 自动降低learning rate
lr_reduction = ReduceLROnPlateau(monitor='val_loss',
                                       factor=0.1, min_lr=1e-8, patience=0,
                                       verbose=1)
# 定义callback函数
callbacks = [
    earlystopping, 
#    checkpoint,
    lr_reduction
]


# In[22]:


model.compile(optimizer=optimizer,
              loss='binary_crossentropy',
              metrics=['accuracy'])


# In[23]:


model.fit(X_train, y_train,validation_split=0.1,epochs=20,batch_size=128,callbacks=callbacks)


# # 保存模型

# In[24]:


model.save('LSTM_rumor_model_58.h5')


# In[25]:


result = model.evaluate(X_test, y_test)
print('Accuracy:{0:.2%}'.format(result[1]))


# In[26]:


def predict_rumor_LSTM(text,label):
    print(text)
    text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "",text)
    cut = seg.cut(text)

    cut_clean=[]
    for word in cut:
        if word in stopwords:
            continue
        cut_clean.append(word)

    for i, word in enumerate(cut_clean):
        try:
            cut_clean[i] = cn_model.vocab[word].index
            if cut_clean[i] >= 50000:
                cut_clean[i] = 0
        except KeyError:
            cut_clean[i] = 0

    tokens_pad = pad_sequences([cut_clean], maxlen=max_tokens,
                           padding='pre', truncating='pre')

    dic={0:'谣言',1:'非谣言'}
    result = model.predict(x=tokens_pad)
    coef = result[0][0]
    if coef >= 0.5:
        print('真实是'+dic[label],'预测是非谣言','output=%.2f'%coef)
    else:
        print('真实是'+dic[label],'预测是谣言','output=%.2f'%coef)
    print('---------------------------------------------')


# In[27]:


test_list = [
    '兴仁县今天抢小孩没抢走，把孩子母亲捅了一刀，看见这车的注意了，真事，车牌号辽HFM055！！！！！赶紧散播！ 都别带孩子出去瞎转悠了 尤其别让老人自己带孩子出去 太危险了 注意了！！！！辽HFM055北京现代朗动，在各学校门口抢小孩！！！110已经 证实！！全市通缉！！',
    '重庆真实新闻:2016年6月1日在重庆梁平县袁驿镇发生一起抢儿童事件，做案人三个中年男人，在三中学校到镇街上的一条小路上，把小孩直接弄晕(儿童是袁驿新幼儿园中班的一名学生)，正准备带走时被家长及时发现用棒子赶走了做案人，故此获救！请各位同胞们以此引起非常重视，希望大家有爱心的人传递下',
    '@尾熊C 要提前预习育儿知识的话，建议看一些小巫写的书，嘻嘻',
]
test_label=[0,0,1]
for i in range(len(test_list)):
    predict_rumor_LSTM(test_list[i],test_label[i])

