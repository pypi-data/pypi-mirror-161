import numpy as np
from sklearn.preprocessing import *

label_encoder=[] # 放置每一列的encoder
#TODO：练2
def encode_data(df):
    data = np.empty(df.shape)
    j = 0
    for i in df.columns:
        encoder=None
        if df[i].dtype==object: # 字符型数据
            encoder=LabelEncoder()
            data[:, j]=encoder.fit_transform(df[i])
            j = j + 1
        else:  # 数值型数据
            data[:, j] = df[i]
            j = j + 1
        label_encoder.append(encoder)
    return data

def encode_pred(t_word):
    t_word2 = np.empty(t_word.shape)
    j = 0
    for i in t_word.columns:
        encoder = None
        if t_word[i].dtype==object: # 字符型数据
            encoder = label_encoder[j]
            t_word2[:, j] = encoder.transform(t_word[i])
            j = j + 1
        else:  # 数值型数据
            t_word2[:, j] = t_word[i]
            j = j + 1
    return t_word2