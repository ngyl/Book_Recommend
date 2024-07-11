import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from keras.models import load_model
import pandas as pd
import numpy as np
import warnings
from tensorflow.keras.callbacks import EarlyStopping
import math

warnings.filterwarnings('ignore')


def evaluation(y_true, y_pred):
    '''
    模型评估：获取准确率、精准度、召回率、F1-score值
    y_true：正确标签
    y_pred：预测标签
    '''
    accuracy = round(classification_report(y_true, y_pred, output_dict=True)['accuracy'], 3)  # 准确率
    s = classification_report(y_true, y_pred, output_dict=True)['weighted avg']
    precision = round(s['precision'], 3)  # 精准度
    recall = round(s['recall'], 3)  # 召回率
    f1_score = round(s['f1-score'], 3)  # F1-score
    print(
        '神经网络协同推荐(NCF):准确率是{},精准度是{},召回率是{},F1值是{}'.format(accuracy, precision, recall, f1_score))
    return accuracy, precision, recall, f1_score


def get_data_fit(users_vector, book_ratings_vector, books_vector):
    '''
    数据训练，得到模型
    '''
    scaler = 5  # 特征标准化：最高分为5，需要归一化到0~1
    book_ratings_vector['rating'] = book_ratings_vector['rating'] / scaler
    df_vector = pd.merge(book_ratings_vector, users_vector[['user_id', 'ip']], on='user_id', how='left')
    merged_df = pd.merge(df_vector, books_vector, left_on='book_id', right_on='isbn', how='left')
    df_vector = merged_df.drop(['isbn', 'title'], axis=1)
    dataset = df_vector  # 已向量化的数据集
    print('输入数据集形式为：')
    print(dataset.head())

    # 使用LabelEncoder将字符串标签转换为整数标签
    user_encoder = LabelEncoder()
    book_encoder = LabelEncoder()
    ip_encoder = LabelEncoder()
    author_encoder = LabelEncoder()
    publisher_encoder = LabelEncoder()

    user_encoder.fit_transform(users_df['user_id'])
    book_encoder.fit_transform(book_ratings_df['book_id'])
    ip_encoder.fit_transform(users_df['ip'])
    author_encoder.fit_transform(books_df['author'])
    publisher_encoder.fit_transform(books_df['publisher'])

    joblib.dump(user_encoder, 'user_encoder.pkl')  # 保存用户标签
    joblib.dump(book_encoder, 'book_encoder.pkl')  # 保存图书标签
    joblib.dump(ip_encoder, 'ip_encoder.pkl')  # 保存ip标签
    joblib.dump(author_encoder, 'author_encoder.pkl')  # 保存作者标签
    joblib.dump(publisher_encoder, 'publisher_encoder.pkl')  # 保存出版社标签

    # 加载标签
    user_encoder = joblib.load('user_encoder.pkl')
    book_encoder = joblib.load('book_encoder.pkl')
    ip_encoder = joblib.load('ip_encoder.pkl')
    author_encoder = joblib.load('author_encoder.pkl')
    publisher_encoder = joblib.load('publisher_encoder.pkl')
    # 此处用transform
    dataset['user_id'] = user_encoder.transform(dataset['user_id'])
    dataset['book_id'] = book_encoder.transform(dataset['book_id'])
    dataset['ip'] = ip_encoder.transform(dataset['ip'])
    dataset['author'] = author_encoder.transform(dataset['author'])
    dataset['publisher'] = publisher_encoder.transform(dataset['publisher'])

    scaler1 = MinMaxScaler()
    year = dataset['year'].values.reshape(-1, 1)
    dataset['year'] = scaler1.fit_transform(year)
    print('转换后数据集形式为：')
    print(dataset.head())

    # Split the dataset into train and test sets
    train, test = train_test_split(dataset, test_size=0.2, random_state=20)  # 划分训练集与测试集
    # train = dataset
    print(train.head())
    # Model hyperparameters
    num_users = len(dataset['user_id'].unique())
    num_books = len(dataset['book_id'].unique())
    num_author = len(dataset['author'].unique())
    num_publisher = len(dataset['publisher'].unique())
    print(num_users)
    print(num_books)
    print(num_author)
    print(num_publisher)

    # 计算嵌入维度
    def calculate_embedding_dim(num_categories):
        return min(50, int(math.ceil(num_categories ** 0.25)))

    user_embedding_dim = calculate_embedding_dim(num_users)
    book_embedding_dim = calculate_embedding_dim(num_books)
    author_embedding_dim = calculate_embedding_dim(num_author)
    publisher_embedding_dim = calculate_embedding_dim(num_publisher)

    print("User Embedding Dim:", user_embedding_dim)
    print("Book Embedding Dim:", book_embedding_dim)
    print("Author Embedding Dim:", author_embedding_dim)
    print("Publisher Embedding Dim:", publisher_embedding_dim)

    embedding_dim = 64
    num_user_features = 1  # 用户特征的数量 ip
    num_book_features = 4  # 图书特征的数量

    # 创建NCF模型
    # 用户输入层及嵌入层
    user_input = tf.keras.layers.Input(shape=(1,), name='user_input')
    user_embedding = tf.keras.layers.Embedding(input_dim=num_users, output_dim=64, name='user_embedding')(
        user_input)
    flatten_user = tf.keras.layers.Flatten()(user_embedding)
    # 书籍输入层及嵌入层
    book_input = tf.keras.layers.Input(shape=(1,), name='book_input')
    book_embedding = tf.keras.layers.Embedding(input_dim=num_books, output_dim=64, name='book_embedding')(
        book_input)
    flatten_book = tf.keras.layers.Flatten()(book_embedding)

    # 用户特征输入
    user_features_input = tf.keras.layers.Input(shape=(num_user_features,), name='user_features_input')  # (1,)

    # 书籍特征输入层及嵌入层
    author_input = tf.keras.layers.Input(shape=(1,), name='author_input')
    publisher_input = tf.keras.layers.Input(shape=(1,), name='publisher_input')
    year_input = tf.keras.layers.Input(shape=(1,), name='year_input')
    genre_input = tf.keras.layers.Input(shape=(1,), name='genre_input')

    author_embedding = tf.keras.layers.Embedding(input_dim=num_author, output_dim=64, name='author_embedding')(
        author_input)

    publisher_embedding = tf.keras.layers.Embedding(input_dim=num_publisher, output_dim=64, name='publisher_embedding')(
        publisher_input)
    #
    flatten_author = tf.keras.layers.Flatten()(author_embedding)
    flatten_publisher = tf.keras.layers.Flatten()(publisher_embedding)

    # # 增加 genre 特征的权重
    # genre_weight = 2.0
    # weighted_genre_input = tf.keras.layers.Lambda(lambda x: x * genre_weight)(genre_input)

    # 合并用户和书籍的嵌入向量
    # concat = tf.keras.layers.Concatenate()([flatten_user, flatten_book])
    # 合并所有输入层的输出
    concat = tf.keras.layers.Concatenate()([
        flatten_user, flatten_book, user_features_input,
        flatten_author, flatten_publisher, year_input, genre_input
        # flatten_publisher,year_input,genre_input

    ])

    # 添加全连接层
    fc1 = tf.keras.layers.Dense(64, activation='relu')(concat)
    fc2 = tf.keras.layers.Dense(32, activation='relu')(fc1)
    # fc3 = tf.keras.layers.Dense(32, activation='relu')(fc2)
    output = tf.keras.layers.Dense(1, activation='sigmoid')(fc2)

    # 创建并编译模型
    model = tf.keras.models.Model(inputs=[
        user_input, book_input, user_features_input, author_input, publisher_input, year_input, genre_input
        # ,publisher_input,year_input,genre_input
    ],
        outputs=output)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # 使用早停法
    early_stopping = EarlyStopping(monitor='mae', patience=5, restore_best_weights=True)
    # 模型训练
    model.fit(
        [train['user_id'].values, train['book_id'].values, train['ip'].values,
         train['author'].values, train['publisher'].values, train['year'].values, train['genre'].values],
        # , train['publisher'].values, train['year'].values, train['genre'].values],
        train['rating'].values,
        batch_size=30,
        epochs=100,
        callbacks=[early_stopping],
        verbose=0
        # validation_split=0.1,
    )

    # 打印模型摘要
    model.summary()

    # # 获取所有独特的用户ID和书籍ID todo
    # unique_users = dataset['user_id'].unique()
    # unique_books = dataset['book_id'].unique()
    # # 获取每个用户的评分数据
    # result_df = {}
    # for user_id in unique_users:
    #     user_rate = dataset[dataset['user_id'] == user_id]
    #     print(user_rate)
    #     if user_rate.empty:
    #         # 用户如果没有评分过任何一本图书则跳过循环
    #         continue
    #     user_label = f'user_{user_id}'
    #     result_df[user_label] = {}
    #     for book_id in unique_books:
    #         book_label = f'book_{book_id}'
    #         pred_user_id = user_encoder.transform([user_id])
    #         pred_book_id = book_encoder.transform([book_id])
    #         result = model.predict(x=[pred_user_id, pred_book_id], verbose=0)
    #         result_df[user_label][book_label] = result[0][0]
    #
    # result_df = pd.DataFrame(result_df).T
    # result_df *= scaler
    #
    # print('全部用户预测结果', result_df)

    # 预测测试集并转成整形列表
    print((model.predict(x=[test['user_id'], test['book_id'], test['ip'],
                            test['author'], test['publisher'], test['year'], test['genre']], verbose=0) * scaler)
          .tolist())
    y_pred_ = np.floor(model.predict(x=[test['user_id'], test['book_id'], test['ip'],
                                        test['author'], test['publisher'], test['year'], test['genre']],
                                     verbose=0) * scaler).tolist()
    y_pred = []
    for y in y_pred_:
        y_pred.append(y[0])
    y_true = (test['rating'] * scaler).tolist()

    evaluation(y_true, y_pred)  # 模型评估
    model.save('ncf.dat')  # 模型保存


def get_ncf_recommend(user_id, n=10):
    '''
    # 获取推荐
    user_id:用户id
    n:只取前十个推荐结果
    '''
    scaler = 5  # 特征标准化：最高分为5，需要归一化到0~1
    scaler1 = MinMaxScaler()
    # 此处归一化取决于数据集 默认为完整数据集 todo 记得与训练时的scaler1对齐
    year = books_df['year'].values.reshape(-1, 1)
    books_df['year'] = scaler1.fit_transform(year)
    model = load_model('ncf.dat')  # 加载模型
    # 加载标签
    user_encoder = joblib.load('user_encoder.pkl')
    book_encoder = joblib.load('book_encoder.pkl')
    ip_encoder = joblib.load('ip_encoder.pkl')
    author_encoder = joblib.load('author_encoder.pkl')
    publisher_encoder = joblib.load('publisher_encoder.pkl')

    result_df = {}
    # 获取所有独特的书籍ID
    book_rates = book_ratings_df['book_id'].unique()
    user = f'{user_id}'
    pred_user_id = user_encoder.transform([user])
    print(pred_user_id)
    # user特征
    user_ip = users_df[users_df['user_id'] == user_id]['ip']
    print(user_ip)
    user_feature = ip_encoder.transform([user_ip])

    for book in book_rates:
        book_id = book
        # book = f'{book_id}'
        pred_book_id = book_encoder.transform([book_id])
        book_features = books_df[books_df['isbn'] == book_id]
        # if len(book_features) > 1:
        #     book_features = book_features.iloc[0,1]
        # else:
        #     book_features = book_features['author']
        # print(book_features)
        print(book_features)
        if len(book_features) > 1:
            # 初始化一个变量来存储当前书籍的最高评分
            max_score = float('-inf')
            book_author = author_encoder.transform([book_features.iloc[0, 2]])
            book_publisher = publisher_encoder.transform([book_features.iloc[0, 4]])
            book_year = np.array([book_features.iloc[0, 3]])
            for genre in book_features['genre']:
                book_genre = np.array([genre])
                result = model.predict(
                    x=[pred_user_id, pred_book_id, user_feature, book_author, book_publisher, book_year, book_genre],
                    verbose=0)

                score = result[0][0] * scaler
                if score > max_score:
                    max_score = score
        else:
            book_author = author_encoder.transform([book_features['author']])
            book_publisher = publisher_encoder.transform([book_features['publisher']])
            book_year = book_features['year']
            book_genre = book_features['genre']
            pred_book_id = book_encoder.transform([book_id])
            result = model.predict(
                x=[pred_user_id, pred_book_id, user_feature, book_author, book_publisher, book_year, book_genre],
                verbose=0)
            max_score = result[0][0] * scaler
        if not ((book_ratings_df['user_id'] == user_id) & (book_ratings_df['book_id'] == book_id)).any():
            # 过滤掉用户已评分过的
            result_df[book_id] = max_score

    result_df_sort = sorted(result_df.items(), key=lambda x: x[1], reverse=True)  # 推荐结果按照评分降序排列
    print('预测结果', result_df_sort)
    recommend_ids = []
    for rds in result_df_sort[:n]:
        recommend_ids.append(rds[0])
    print(f'前{n}个推荐结果', recommend_ids)
    return recommend_ids


if __name__ == '__main__':
    # df_vector = get_data_vector(data_pd)  # 数据向量化
    users_df = pd.read_csv('DB_dataset/Users1k.csv', on_bad_lines='warn', encoding="utf-8")
    book_ratings_df = pd.read_csv('DB_dataset/Book_Ratings2k.csv', on_bad_lines='warn', encoding="utf-8")
    books_df = pd.read_csv('DB_dataset/book/book_encoded.csv', on_bad_lines='warn', encoding="utf-8")
    data_recommend = get_data_fit(users_df, book_ratings_df, books_df)  # 获取数据训练模型
    user_id = 1000739  # 1000030
    recommend_ids = get_ncf_recommend(user_id)  # 获取指定用户的推荐结果