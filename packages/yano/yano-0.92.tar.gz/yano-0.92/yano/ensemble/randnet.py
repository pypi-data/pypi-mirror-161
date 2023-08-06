import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K

import os
import numpy as np
import time

from sklearn.metrics import roc_auc_score

from tqdm import tqdm

from .dean import DEAN

from .densedrop import densedrop


class RandNet(DEAN):
    def __init__(s,*args,pth="./RandNet/",max_epochs=300,alpha=0.5,validation_split=0.1,lr=0.01,**kwargs):
        super().__init__(*args,pth=pth,max_epochs=max_epochs,validation_split=validation_split,lr=lr,**kwargs)
        s.alpha=alpha

    def build_one_model(s,index=0):
        s._seed(index)
        def genlayer(dim,act=s.act):
            return densedrop(dim,activation=act),keras.layers.Dense(dim,activation=act)
        def genlayers(dims):
            layers=[]
            for dim in dims[:-1]:
                layers.append(genlayer(dim))
            layers.append(genlayer(dims[-1],act="linear"))
            return layers
        def genmodel(inp,inp2,layers):
            q=inp
            q2=inp2
            for layer in layers:
                q=layer[0](q)
                q2=layer[1](q2)
            return keras.models.Model(inp,q),keras.models.Model(inp2,q2)

        dim0=int(s.data.shape[1])
        dims=[]
        for i in range(s.depth):
            dims.append(s.alpha**(i+1))
        for i in list(range(s.depth))[::-1]:
            dims.append(s.alpha**i)
        dims=[max([3,int(zw*dim0)]) for zw in dims]


        inp=keras.layers.Input(shape=s.data.shape[1:])
        inp2=keras.layers.Input(shape=s.data.shape[1:])
        layers=genlayers(dims)
        model,model2=genmodel(inp,inp2,layers)

        model.compile(optimizer=keras.optimizers.Adam(lr=s.lr),loss="mse")
        model2.compile(optimizer=keras.optimizers.Adam(lr=s.lr),loss="mse")

        return layers,model,model2



    def train_one(s,index=0):
        pth=s.index_path(index)
        
        data=s.data
        layers,model,model2=s.build_one_model(index)

        t1=time.perf_counter()

        model.fit(data,data,
                  epochs=s.max_epochs,
                  batch_size=s.batch,
                  validation_split=s.validation_split,
                  verbose=s.verbose,
                  shuffle=True)

        t2=time.perf_counter()

        x=data
        px=model.predict(x)
        dx=(px-x)**2
        dx=np.mean(dx,axis=1)
        div=np.std(dx)

        wei=model.get_weights()
        alts=[lay[0].get_matrix() for lay in layers]
        for i,w in enumerate(wei):
            if str(alts[0].shape)==str(w.shape):
                wei[i]=alts.pop(0)
                if len(alts)==0:
                    break
        model2.set_weights(wei)

        model2.save(pth+"model.h5")

        scores=[]
        auc=-1.0
        if not s.test_data is None:
            tx=s.test_data
            p=model2.predict(tx)
            d=(p-tx)**2
            d=np.mean(d,axis=1)
            scores=d
            if not s.test_labels is None:
                auc=roc_auc_score(s.test_labels,scores)

        dt=t2-t1

        if s.verbose:
            print("RandNet:",index,":",dt,":",auc)

        np.savez_compressed(pth+"results.npz",s=scores,auc=auc,dt=dt,div=div)

        return scores/div
    
    def ensemble_merge(s,scores):
        return np.median(np.array(scores)**2 ,axis=0)



