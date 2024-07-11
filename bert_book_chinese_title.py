# 导入所需库
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizer
from torch import nn
from transformers import BertModel
from torch.optim import Adam
from tqdm import tqdm
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"




# 定义一个类
class CustomDataset(Dataset):
    def __init__(self, df):
        self.labels = df['genre']
        self.texts = [tokenizer(text,
                                padding='max_length',
                                max_length=512,
                                truncation=True,
                                return_tensors="pt")
                      for text in df['title']]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        batch_texts = self.get_batch_texts(idx)
        batch_y = self.get_batch_labels(idx)
        return batch_texts, batch_y

    def classes(self):
        # 返回文本标签
        return self.labels

    def get_batch_labels(self, idx):
        # 获取标签
        return np.array(self.labels[idx])

    def get_batch_texts(self, idx):
        # 获取inputs
        return self.texts[idx]





# 构建实际模型
class BertClassifier(nn.Module):
    def __init__(self, dropout=0.5):
        super(BertClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert_chinese')
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, 18)
        self.relu = nn.ReLU()

    def forward(self, input_id, mask):
        _, pooled_output = self.bert(input_ids=input_id,
                                     attention_mask=mask,
                                     return_dict=False)
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        final_layer = self.relu(linear_output)
        return final_layer





def train(model, train_data, val_data, learning_rate, epochs, save_path):
    ##处理数据
    # 通过Dataset类获取训练和验证集
    train = CustomDataset(train_data)
    val = CustomDataset(val_data)

    # DataLoader根据batch_size获取数据，训练时选择打乱样本
    train_dataloader = DataLoader(train,
                                  batch_size=2,
                                  shuffle=True)
    val_dataloader = DataLoader(val, batch_size=2)

    # 判断是否使用GPU
    use_cuda = torch.cuda.is_available()

    device = torch.device("cuda" if use_cuda else "cpu")

    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=learning_rate)

    if use_cuda:
        model = model.cuda()
        criterion = criterion.cuda()

    # 开始进入训练循环
    for epoch_num in range(epochs):
        # 定义两个变量，用于存储训练集的准确率和损失
        total_acc_train = 0
        total_loss_train = 0
        # 进度条函数tqdm
        for train_input, train_label in tqdm(train_dataloader):
            train_label = train_label.to(device)
            mask = train_input['attention_mask'].to(device)
            input_id = train_input['input_ids'].squeeze(1).to(device)
            # 通过模型得到输出
            output = model(input_id, mask)


            # 检查标签的范围
            assert train_label.max().item() < output.size(1), \
                f"标签值 {train_label.max().item()} 超出输出的类别范围 {output.size(1)}"
            # 计算损失
            batch_loss = criterion(output, train_label)

            total_loss_train += batch_loss.item()
            # 计算精度
            acc = (output.argmax(dim=1) == train_label).sum().item()
            total_acc_train += acc
            # 模型更新
            model.zero_grad()
            batch_loss.backward()
            optimizer.step()
        # ------ 验证模型 -----------
        # 定义两个变量，用于存储验证集的准确率和损失
        total_acc_val = 0
        total_loss_val = 0
        # 不需要计算梯度
        with torch.no_grad():
            # 循环获取数据集，并用训练好的模型进行验证
            for val_input, val_label in val_dataloader:
                # 如果有GPU，则使用GPU，接下来的操作同训练
                val_label = val_label.to(device)
                mask = val_input['attention_mask'].to(device)
                input_id = val_input['input_ids'].squeeze(1).to(device)

                output = model(input_id, mask)

                batch_loss = criterion(output, val_label)
                total_loss_val += batch_loss.item()

                acc = (output.argmax(dim=1) == val_label).sum().item()
                total_acc_val += acc

        print(
            f'''Epochs: {epoch_num + 1} 
              | Train Loss: {total_loss_train / len(train_data): .3f} 
              | Train Accuracy: {total_acc_train / len(train_data): .3f} 
              | Val Loss: {total_loss_val / len(val_data): .3f} 
              | Val Accuracy: {total_acc_val / len(val_data): .3f}''')

    # 保存模型
    torch.save(model.state_dict(), save_path)
    print(f"模型已保存到 {save_path}")
    # 获得数据集，并拆分为训练集和测试集


def evaluate(model, test_data):
    test = Dataset(test_data)
    test_dataloader = torch.utils.data.DataLoader(test, batch_size=3)
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    if use_cuda:
        model = model.cuda()

    total_acc_test = 0
    with torch.no_grad():
        for test_input, test_label in test_dataloader:
            test_label = test_label.to(device)
            mask = test_input['attention_mask'].to(device)
            input_id = test_input['input_ids'].squeeze(1).to(device)
            output = model(input_id, mask)
            acc = (output.argmax(dim=1) == test_label).sum().item()
            total_acc_test += acc
    print(f'Test Accuracy: {total_acc_test / len(test_data): .3f}')




# 先准备分词器和标签
tokenizer = BertTokenizer.from_pretrained('bert_chinese')
import warnings
warnings.filterwarnings('ignore')

_train = pd.read_csv(
    'top_100_books.csv', on_bad_lines='warn',encoding="utf-8")
_val = pd.read_csv(
    'next_50_books.csv', on_bad_lines='warn',encoding="utf-8")
# _test = pd.read_csv(
#     'C:\\Users\\xie zhou yao\\bert\\data\\test.csv')
# _test_handout = pd.read_csv(
#     'C:\\Users\\xie zhou yao\\bert\\data\\test_handout.csv')

# _train = _train[0:500]
# _val = _val[0:500]
# _test = _test[0:500]
# _test_handout = _test_handout[0:500]
# 训练模型
EPOCHS = 10
model = BertClassifier()

LR = 1e-5
train(model, _train, _val, LR, EPOCHS, save_path='trained_model.pth')

# # 评估模型
# model.load_state_dict(torch.load('trained_model.pth'))