#######################
## import modules 
#######################

from sklearn.preprocessing import MinMaxScaler, StandardScaler
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torchvision import datasets
from torch.utils.data import DataLoader
from torch.utils.data import Subset
from torch.utils.data import Dataset
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class ae_hi(object):
    def __init__(self, train_data, scale_type=2, fill_dict={np.nan:0}, used_vars=[],
                learning_rate = 0.001, batch_size = 128, num_epochs = 10, num_hidden_1=10, num_hidden_2=2):
        '''函数功能
        初始化AE类
        
        Args:
        train_data (pandas.DataFrame) : 建模数据集
        scale_type (int): 默认值为2，1--StandardScaler, 2--MinMaxScaler 0--将不进行归一化
        fill_dict (dict): 默认为{np.nan:0}，缺失值替换列表 
        used_vars (list) : 入模变量列表
        learning_rate (float) : 学习率
        batch_size (int) : 默认为128，批次数据
        num_epochs (int) : 默认为10，训练轮数
        num_hidden_1 (int) : 默认为10， 隐藏层1节点数
        num_hidden_2 (int) : 默认为2， 隐藏层1节点数
        '''
        self.train_data = train_data
        self.scale_type = scale_type
        self.fill_dict = fill_dict 
        self.st = None
        self.learning_rate = learning_rate 
        self.batch_size = batch_size 
        self.num_epochs = num_epochs 
        self.used_vars = used_vars
        self.num_hidden_1 = num_hidden_1
        self.num_hidden_2 = num_hidden_2

    def _preprocess(self, data, batch_size, shuffle, is_train):
        idx = data.index
        data_x = data[self.used_vars].replace(self.fill_dict)
        if is_train:
            if self.scale_type==1:
                self.st = StandardScaler()
            elif self.scale_type ==2:
                self.st = MinMaxScaler()
            if self.scale_type !=1 and self.scale_type!=2  and self.scale_type!=0:
                raise ValueError('scale_type must be 1--StandardScaler, 2--MinMaxScaler')
            if self.scale_type==1 or self.scale_type==2 :
                self.st.fit_transform(data_x) 
        if self.st is not None:
            data_x = self.st.transform(data_x)
        else:
            data_x = data_x.values

        data_x = pd.DataFrame(data_x, 
                       columns=self.used_vars,
                       index=idx)

        dataset = UDFDataset(data_x.values)

        loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
        for features in loader:
            print(features.shape)
            break
        return data_x, dataset, loader

    def train(self):
        device = torch.device('cpu')
        data_x, dataset, loader = self._preprocess(self.train_data, self.batch_size, True, True)
        model = Autoencoder(data_x.shape[1], self.num_hidden_1, self.num_hidden_2, device)
        self.model = model.to(device)
        ##########################
        ### COST AND OPTIMIZER
        ##########################

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)  
        loss_fn = nn.MSELoss()
        for epoch in range(self.num_epochs):
            self.model.train()
            
            for batch_idx, features in enumerate(loader):
                features = features.to(device)
                logits = self.model(features)
                loss = loss_fn(logits, features)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                if not batch_idx % 100:
                    print('Epoch %03d/%03d |loss %.4f' % (epoch + 1, self.num_epochs, loss))
            print('Epoch %03d/%03d |loss %.4f' % (epoch + 1, self.num_epochs, loss))
            
        self.train_data = None

        return self

    def predict(self, oot_data):
        device = torch.device('cpu')
        data_x, dataset, loader = self._preprocess(oot_data, oot_data.shape[0], False, False)
        self.model.eval()

        for features in loader:
            features = features.to(device)
            X_pred = self.model(features)
            X_pred = pd.DataFrame(X_pred)
            X_pred.index = oot_data.index
            scored = pd.DataFrame(index=oot_data.index)
            scored['Loss_mae'] = np.mean(np.abs(X_pred - features.detach().numpy()), axis=1)
            result = pd.concat([scored, oot_data], axis=1)
        return result


class UDFDataset(Dataset):
    def __init__(self, x):
        self.x = x
    
    def __getitem__(self, index):
        features = self.x[index]
        features = torch.tensor(features, dtype=torch.float32)

        return features
        
    def __len__(self):
        return self.x.shape[0]


class Autoencoder(torch.nn.Module):

    def __init__(self, num_features, num_hidden_1, num_hidden_2, device):
        super(Autoencoder, self).__init__()
        self.device = device
        
        ### ENCODER
        self.linear1 = nn.Linear(num_features, num_hidden_1)
        self.linear2 = nn.Linear(num_hidden_1, num_hidden_2)
     
        ### DECODER
        self.linear3 = torch.nn.Linear(num_hidden_2, num_hidden_1)
        self.linear4 = torch.nn.Linear(num_hidden_1, num_features)

    def forward(self, x):

        encoder = self.linear1(x)
        encoder = F.leaky_relu(encoder)

        encoder = self.linear2(encoder)
        encoder = F.leaky_relu(encoder)

        decoder = self.linear3(encoder)
        decoder = F.leaky_relu(decoder)
        decoder = self.linear4(decoder)
        #decoder = F.sigmoid(decoder)

        return decoder

