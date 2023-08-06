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
import numpy as np
import pandas as pd

class cvae_hi(object):
    def __init__(self, train_data, scale_type=2, fill_dict={np.nan:0}, used_vars=[],
                learning_rate = 0.001, batch_size = 128, num_epochs = 10, num_hidden_1=12, num_latent=4, num_classes=2, y='fpd_k4'):
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
        num_hidden_1 (int) : 默认为12， 隐藏层1节点数
        num_latent (int) : 默认为4
        num_classes (int) : 分类数
        y (string) : 默认为'fpd_k4'，目标变量
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
        self.num_latent = num_latent
        self.num_classes = num_classes
        self.y = y

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

        dataset = UDFDataset(data_x.values, data[self.y].values)

        loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
        for features, targets in loader:
            print(features.shape)
            print(targets.shape)
            break
        return data_x, dataset, loader

    def train(self):
        device = torch.device('cpu')
        data_x, dataset, loader = self._preprocess(self.train_data, self.batch_size, True, True)
        model = ConditionalVariationalAutoencoder(data_x.shape[1],
                                                 self.num_hidden_1, self.num_latent, self.num_classes, device)
        self.model = model.to(device)
        ##########################
        ### COST AND OPTIMIZER
        ##########################

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)  
        for epoch in range(self.num_epochs):
            self.model.train()
            
            for batch_idx, (features, targets) in enumerate(loader):
                features = features.to(device)
                targets = targets.to(device)
                z_mean, z_log_var, encoded, decoded = self.model(features, targets)
                kl_divergence = (.5 * (z_mean ** 2 + torch.exp(z_log_var) - z_log_var - 1)).sum()
                
                x_con = torch.cat((features, to_onehot(targets, 2, device)), dim=1)
                pixelwise_bce = F.binary_cross_entropy(decoded, x_con, reduction='sum')
                loss = kl_divergence + pixelwise_bce
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                if not batch_idx % 100:
                    print('Epoch %03d/%03d |loss %.2f' % (epoch + 1, self.num_epochs, loss))
            print('Epoch %03d/%03d |loss %.2f' % (epoch + 1, self.num_epochs, loss))

        self.train_data = None
        return self

    def predict(self, oot_data, output_method=1):
        device = torch.device('cpu')
        data_x, dataset, loader = self._preprocess(oot_data, oot_data.shape[0], False, False)
        lbe = 0
        self.model.eval()
        with torch.set_grad_enabled(False):
            for features, _ in loader:
                features = features.to(device)
                targets = torch.tensor([lbe] * features.size(0)).to(device)
                z_mean, z_log_var, encoded, decoded = self.model.forward_predict(features, targets)
                #decoded = self.model.decoder(features, targets)
                x_con = torch.cat((features, to_onehot(targets, 2, device)), dim=1)
                loss0 = torch.mean(torch.abs(x_con - decoded), dim=1)
                loss_kl = torch.mean((.5 * (z_mean ** 2 + torch.exp(z_log_var) - z_log_var - 1)), dim=1)
                
        lbe = 1
        self.model.eval()
        with torch.set_grad_enabled(False):
            for features, _ in loader:
                features = features.to(device)
                targets = torch.tensor([lbe] * features.size(0)).to(device)
                z_mean, z_log_var, encoded, decoded = self.model.forward_predict(features, targets)
                #decoded = self.model.decoder(features, targets)
                x_con = torch.cat((features, to_onehot(targets, 2, device)), dim=1)
                loss1 = torch.mean(torch.abs(x_con - decoded), dim=1)
        if output_method == 1:
                
            loss = loss0
        elif output_method == 2:
            loss = loss0 + loss_kl
        scored = pd.DataFrame(index=oot_data.index)

        scored['Loss_mae'] = loss.detach().numpy()
        result = pd.concat([scored, oot_data], axis=1)
        return result


class UDFDataset(Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __getitem__(self, index):
        features = self.x[index]
        labels = self.y[index]
        features = torch.tensor(features, dtype=torch.float32)
        labels = torch.tensor(labels, dtype=torch.int64)
        
        return features, labels
        
    def __len__(self):
        return self.y.shape[0]


def to_onehot(labels, num_classes, device):

    labels_onehot = torch.zeros(labels.size()[0], num_classes, dtype=torch.int64).to(device)
    labels = torch.tensor(labels, dtype=torch.int64)
    labels_onehot.scatter_(1, labels.view(-1, 1), 1)

    return labels_onehot


class ConditionalVariationalAutoencoder(torch.nn.Module):

    def __init__(self, num_features, num_hidden_1, num_latent, num_classes, device):
        super(ConditionalVariationalAutoencoder, self).__init__()
        
        self.num_classes = num_classes
        self.device = device
        
        ### ENCODER
        self.hidden_1 = torch.nn.Linear(num_features+num_classes, num_hidden_1)
        self.z_mean = torch.nn.Linear(num_hidden_1, num_latent)
        # in the original paper (Kingma & Welling 2015, we use
        # have a z_mean and z_var, but the problem is that
        # the z_var can be negative, which would cause issues
        # in the log later. Hence we assume that latent vector
        # has a z_mean and z_log_var component, and when we need
        # the regular variance or std_dev, we simply use 
        # an exponential function
        self.z_log_var = torch.nn.Linear(num_hidden_1, num_latent)
        
        
        ### DECODER
        self.linear_3 = torch.nn.Linear(num_latent+num_classes, num_hidden_1)
        self.linear_4 = torch.nn.Linear(num_hidden_1, num_features+num_classes)

    def reparameterize(self, z_mu, z_log_var):
        # Sample epsilon from standard normal distribution
        eps = torch.randn(z_mu.size(0), z_mu.size(1)).to(self.device)
        # note that log(x^2) = 2*log(x); hence divide by 2 to get std_dev
        # i.e., std_dev = exp(log(std_dev^2)/2) = exp(log(var)/2)
        z = z_mu + eps * torch.exp(z_log_var/2.) 
        return z
        
    def encoder(self, features, targets):
        ### Add condition
        onehot_targets = to_onehot(targets, self.num_classes, self.device)
        x = torch.cat((features, onehot_targets), dim=1)

        ### ENCODER
        x = self.hidden_1(x)
        x = F.leaky_relu(x)
        z_mean = self.z_mean(x)
        z_log_var = self.z_log_var(x)
        encoded = self.reparameterize(z_mean, z_log_var)
        return z_mean, z_log_var, encoded
    
    def decoder(self, encoded, targets):
        ### Add condition
        onehot_targets = to_onehot(targets, self.num_classes, self.device)
        encoded = torch.cat((encoded, onehot_targets), dim=1)        
        
        ### DECODER
        x = self.linear_3(encoded)
        x = F.leaky_relu(x)
        x = self.linear_4(x)
        decoded = torch.sigmoid(x)
        return decoded

    def forward(self, features, targets):
        
        z_mean, z_log_var, encoded = self.encoder(features, targets)
        decoded = self.decoder(encoded, targets)
        
        return z_mean, z_log_var, encoded, decoded
    
    def reparameterize_predict(self, z_mu, z_log_var):
        # Sample epsilon from standard normal distribution
        eps = torch.randn(z_mu.size(0), z_mu.size(1)).to(self.device)
        # note that log(x^2) = 2*log(x); hence divide by 2 to get std_dev
        # i.e., std_dev = exp(log(std_dev^2)/2) = exp(log(var)/2)
        z = z_mu 
        return z
        
    def encoder_predict(self, features, targets):
        ### Add condition
        onehot_targets = to_onehot(targets, self.num_classes, self.device)
        x = torch.cat((features, onehot_targets), dim=1)

        ### ENCODER
        x = self.hidden_1(x)
        x = F.leaky_relu(x)
        z_mean = self.z_mean(x)
        z_log_var = self.z_log_var(x)
        encoded = self.reparameterize_predict(z_mean, z_log_var)
        return z_mean, z_log_var, encoded

    def forward_predict(self, features, targets):
        
        z_mean, z_log_var, encoded = self.encoder_predict(features, targets)
        decoded = self.decoder(encoded, targets)
        
        return z_mean, z_log_var, encoded, decoded

