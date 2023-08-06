import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K

import os
import numpy as np
import time

from sklearn.metrics import roc_auc_score

from tqdm import tqdm

class DEAN(object):
    

    def __init__(s,task,data,test_data=None, test_labels=None,lr=0.03,batch=100,depth=3,bag=128,pth="./DEAN/",
            act="relu",reg=None,use_bias=False,goal_mean=1.0,verbose=1,patience=5,max_epochs=500,validation_split=0.2):

        s.task = task
        s.data = data
        s.test_data = test_data
        s.test_labels = test_labels
        s.lr = lr
        s.batch = batch
        s.depth = depth
        s.bag = bag
        s.pth = pth+task+"/"
        os.makedirs(s.pth,exist_ok=True)
        s.act = act
        s.reg = reg
        s.use_bias = use_bias
        s.goal_mean = goal_mean
        s.verbose = verbose
        s.patience = patience
        s.max_epochs = max_epochs
        s.validation_split = validation_split


    def build_one_model(s,index=0):
        np.random.seed(index)
        tf.random.set_seed(index)

        inn=keras.layers.Input(shape=(s.bag,))
        q=inn

        dims=[s.bag for i in range(s.depth)]
        for aq in dims[1:-1]:
            q=keras.layers.Dense(aq,activation=s.act,use_bias=s.use_bias,
                                  kernel_regularizer=s.reg)(q)
        q=keras.layers.Dense(dims[-1],activation="linear",use_bias=s.use_bias,
                                kernel_regularizer=s.reg)(q)
    
        model=keras.Model(inn,q)

        comp=K.ones_like(q)*s.goal_mean
        loss=keras.losses.msle(q,comp)
        loss=K.mean(loss)
        model.add_loss(loss)

        model.compile(optimizer=keras.optimizers.Adam(s.lr))
        return model

    def data_dex(s,index=0):
        ps=np.random.randint(0,2**31)
        np.random.seed(index)
        to_use=np.random.choice(s.data.shape[1],s.bag,replace=False)
        np.random.seed(ps)
        return to_use

    def data_trafo(s,data,to_use=None):
        if type(to_use) is int:
            to_use=s.data_dex(to_use)
        assert not to_use is None
        return np.concatenate([np.expand_dims(data[:,use],axis=1) for use in to_use],axis=1)

    def sub_data(s,index=0):
        to_use=s.data_dex(index)
        return s.data_trafo(s.data,to_use)

    def _seed(s,index=0):
        np.random.seed(index)
        tf.random.set_seed(index)
    
    def index_path(s,index=0):
        pth=f"{s.pth}/{index}/"
        os.makedirs(pth,exist_ok=True)
        return pth

    def train_one(s,index=0):
        pth=s.index_path(index)
        s._seed(index)

        to_use=s.data_dex(index)
        data=s.data_trafo(s.data,to_use)

        model=s.build_one_model(index)

        if s.verbose:
            model.summary()

        cb=[keras.callbacks.EarlyStopping(monitor="val_loss",patience=s.patience,verbose=s.verbose,restore_best_weights=True)]
        cb.append(keras.callbacks.TerminateOnNaN())
        cb.append(keras.callbacks.ModelCheckpoint(pth+"model.h5",monitor="val_loss",verbose=s.verbose,save_best_only=True,save_weights_only=True))

        t1=time.perf_counter()

        model.fit(data,None,
                epochs=s.max_epochs,
                batch_size=s.batch,
                validation_split=s.validation_split,
                verbose=s.verbose,
                callbacks=cb)

        t2=time.perf_counter()

        p=model.predict(data)
        m=np.mean(p)

        scores=[]
        auc=-1.0
        if not s.test_data is None:
            test_data=s.data_trafo(s.test_data,to_use)
            test_p=model.predict(test_data)
            test_p=np.mean(test_p,axis=-1)
            scores=(test_p-m)**2
            if not s.test_labels is None:
                auc=roc_auc_score(s.test_labels,scores)

        dt=t2-t1

        if s.verbose:
            print(f"{index} {auc:.4f} {dt:.4f}")

        np.savez_compressed(pth+"results.npz",m=m,s=scores,auc=auc,dt=dt,to_use=to_use)



        return scores

    def ensemble_merge(s,scores):
        return np.sqrt(np.mean(np.array(scores)**2,axis=0))

    def ensemble_eval(s,scores):
        assert not s.test_labels is None
        return roc_auc_score(s.test_labels,s.ensemble_merge(scores))

    def train_many(s,i0=0,i1=100):
        scores=[]
        aucs=[]
        tq=tqdm(range(i0,i1))
        for i in tq:
            scores.append(s.train_one(i))
            aucs.append(s.ensemble_eval(scores))
            tq.set_description(f"{i} {aucs[-1]:.4f}")

        return scores,aucs















