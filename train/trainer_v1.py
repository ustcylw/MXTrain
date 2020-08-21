#! /usr/bin/env python
# coding: utf-8
import os, sys
import numpy as np
import cv2 as cv
import mxnet as mx
import matplotlib.pyplot as plt
import glob
import mxnet.metric
import warnings
# import logging
# logging.getLogger().setLevel(logging.DEBUG)  # logging to stdout
from logger.logger_v4 import Log
logging = Log()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataset.image_folder_dataset import ImageFolderDataIter, ImageFolderDataset, ImageFolderDataLoader
from utils.file_func import get_class_name, get_function_name
from model_zoo.mobilenet_v2 import MobileNetV20Transform



class Config(object):
    def __init__(
        self,
        with_fit=True,
        gpus='0,1',
        min_epoch=0,
        max_epoch=10,
        checkpoint_dir=r'../checkpoints',
        pretrained_prefix='./model/eye-hole',
        pretrained_epoch=0,
        batch_size=24,
        log_interval=30
    ):
        self.checkpoint_dir = checkpoint_dir
        self.log_interval = log_interval
        self.gpus = gpus
        self.min_epoch = min_epoch
        self.max_epoch = max_epoch
        self.batch_size = batch_size
        self.pretrained_prefix = pretrained_prefix
        self.pretrained_epoch = pretrained_epoch
        self.with_fit = with_fit

class Config1(object):
    def __init__(
        self,
        with_fit=True,
        gpus='0,1',
        min_epoch=0,
        max_epoch=10,
        checkpoint_dir=r'../checkpoints',
        pretrained_prefix='./model/eye-hole',
        pretrained_epoch=0,
        batch_size=24,
        log_interval=30,
        num_class=2,
        image_dir=r'/home/intellif/Desktop/北京活体检测/20200806/test',
        weight_decay=1e-4,
        learning_rate=1e-3
    ):
        super(Config1, self).__init__(
            with_fit=with_fit,
            gpus=gpus,
            min_epoch=min_epoch,
            max_epoch=max_epoch,
            checkpoint_dir=checkpoint_dir,
            pretrained_prefix=pretrained_prefix,
            pretrained_epoch=pretrained_epoch,
            batch_size=batch_size,
            log_interval=log_interval
        )
        self.num_class = 2
        self.image_dir = r'/home/intellif/Desktop/北京活体检测/20200806/test'
        self.weight_decay = 1e-4
        self.learning_rate = 1e-3


class Trainer():

    def __init__(self, config):
        assert not isinstance(config, Config), f'config file is not correct!!!'
        self.config = config

        self.ctxs = [mx.gpu(int(i)) for i in config.gpus.split(',')]

        if self.config.with_fit:
            self.train_iter = ImageFolderDataIter(
                root=self.config.image_dir,
                data_shape=(3, 128, 128),
                label_shape=(2,),
                data_names=['data'],
                label_names=['softmax_label'],
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label),
                batch_size=self.config.batch_size
            )
            # data_iter = iter(self.train_iter)
            # batch = next(data_iter)
            # logging.info(f'[] label: {batch.label}')
            # # sys.exit(0)
            # self.train_dataset = ImageFolderDataset(
            #     root=config.image_dir,
            #     flag=1,
            #     transform=lambda data, label: (data.astype(np.float32)/255, label)
            # )
            # self.train_dataloader = mx.gluon.data.DataLoader(
            #     dataset=self.train_dataset,
            #     batch_size=self.config.batch_size,
            #     shuffle=True
            # )
            # self.eval_dataset = ImageFolderDataset(
            #     root=config.image_dir,
            #     flag=1,
            #     transform=lambda data, label: (data.astype(np.float32)/255, label)
            # )
            # self.eval_dataloader = mx.gluon.data.DataLoader(
            #     dataset=self.eval_dataset,
            #     batch_size=self.config.batch_size,
            #     shuffle=True
            # )
            # self.train_iter = mx.contrib.io.DataLoaderIter(self.train_dataloader)

        else:
            self.net = MobileNetV20Transform().download_model(
                num_class=self.config.num_class,
                prefix=self.config.pretrained_name,
                epoch=self.config.pretrained_epoch
            )
            self.net.collect_params().reset_ctx(self.ctxs)

            self.trainer = mx.gluon.Trainer(
                self.net.collect_params(),
                'sgd',
                {'learning_rate': config.learning_rate, 'wd': config.weight_decay}
            )

            self.train_dataset = ImageFolderDataset(
                root=config.image_dir,
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label)
            )
            self.train_dataloader = mx.gluon.data.DataLoader(
                dataset=self.train_dataset,
                batch_size=self.config.batch_size,
                shuffle=True
            )
            self.eval_dataset = ImageFolderDataset(
                root=config.image_dir,
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label)
            )
            self.eval_dataloader = mx.gluon.data.DataLoader(
                dataset=self.eval_dataset,
                batch_size=self.config.batch_size,
                shuffle=True
            )

        self.sec_loss = mx.gluon.loss.SoftmaxCrossEntropyLoss()

        self.train_acc = mx.metric.Accuracy()
        self.eval_acc = mx.metric.Accuracy()

    def dataset(self):
        if self.config.with_fit:
            self.train_iter = ImageFolderDataIter(
                root=self.config.image_dir,
                data_shape=(3, 128, 128),
                label_shape=(2,),
                data_names=['data'],
                label_names=['softmax_label'],
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label),
                batch_size=self.config.batch_size
            )
            # data_iter = iter(self.train_iter)
            # batch = next(data_iter)
            # logging.info(f'[] label: {batch.label}')
            # # sys.exit(0)
            # self.train_dataset = ImageFolderDataset(
            #     root=config.image_dir,
            #     flag=1,
            #     transform=lambda data, label: (data.astype(np.float32)/255, label)
            # )
            # self.train_dataloader = mx.gluon.data.DataLoader(
            #     dataset=self.train_dataset,
            #     batch_size=self.config.batch_size,
            #     shuffle=True
            # )
            # self.eval_dataset = ImageFolderDataset(
            #     root=config.image_dir,
            #     flag=1,
            #     transform=lambda data, label: (data.astype(np.float32)/255, label)
            # )
            # self.eval_dataloader = mx.gluon.data.DataLoader(
            #     dataset=self.eval_dataset,
            #     batch_size=self.config.batch_size,
            #     shuffle=True
            # )
            # self.train_iter = mx.contrib.io.DataLoaderIter(self.train_dataloader)

        else:
            self.train_dataset = ImageFolderDataset(
                root=config.image_dir,
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label)
            )
            self.train_dataloader = mx.gluon.data.DataLoader(
                dataset=self.train_dataset,
                batch_size=self.config.batch_size,
                shuffle=True
            )
            self.eval_dataset = ImageFolderDataset(
                root=config.image_dir,
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label)
            )
            self.eval_dataloader = mx.gluon.data.DataLoader(
                dataset=self.eval_dataset,
                batch_size=self.config.batch_size,
                shuffle=True
            )

    def train_with_fit(self):
        sym, arg_params, aux_params = MobileNetV20Transform().load_checkpoints(
            prefix=self.config.pretrained_name+'-sym',
            epoch=self.config.pretrained_epoch
        )
        model = mx.mod.Module(
            symbol=sym,
            context=self.ctxs,
        )
        logging.info(f'[0] {model.output_names}')
        logging.info(f'[0] {model.label_names}')
        logging.info(f'[0] {model.data_names}')
        logging.info(f'[0] {self.train_iter.provide_data}')
        logging.info(f'[0] {self.train_iter.provide_label}')
        logging.info(f'[0] model.data_names: {model.data_names}')
        logging.info(f'[0] model.label_names: {model.label_names}')
        data_shapes = [('data', (self.config.batch_size, 3, 128, 128))]
        label_shapes = [('softmax_label', (self.config.batch_size, ))]
        logging.info(f'[0] data_shapes: {data_shapes}')
        logging.info(f'[0] label_shapes: {label_shapes}')
        model.bind(
            # data_shapes=self.train_iter.provide_data,  # [('data', (self.config.batch_size, 3, 128, 128))],
            # label_shapes=self.train_iter.provide_label,  # [('softmax_label', (self.config.batch_size, self.config.num_class))],
            # data_shapes=self.train_iter.provide_data,  # [('data', (self.config.batch_size, 3, 128, 128))],
            # label_shapes=self.train_iter.provide_label  # [('softmax_label', (self.config.batch_size, self.config.num_class))],
            data_shapes=data_shapes,
            label_shapes=label_shapes,
        )
        logging.info(f'[1] {model.output_names}')
        logging.info(f'[1] {model.label_names}')
        logging.info(f'[1] {model.label_names}  {model.label_shapes}')
        logging.info(f'[1] {model.data_names}  {model.data_shapes}')
        model.set_params(arg_params=arg_params, aux_params=aux_params, allow_missing=False)
        model.fit(
            train_data=self.train_iter,
            optimizer='sgd',
            optimizer_params={'learning_rate': self.config.learning_rate, 'wd': self.config.weight_decay},
            num_epoch=self.config.max_epoch,
            batch_end_callback=[
                mx.callback.Speedometer(self.config.batch_size, 1),
            ],
            epoch_end_callback=mx.callback.do_checkpoint(self.config.pretrained_name, 1),
            eval_metric='acc'
        )

    def train(self):
        if self.config.with_fit:
            self.train_with_fit()
        else:
            self.train_epoch()

    def train_epoch(self):

        for epoch in range(self.config.min_epoch, self.config.max_epoch):
            total_loss = 0
            for idx, (feature, label) in enumerate(self.train_dataloader):
                gpu_datas = mx.gluon.utils.split_and_load(feature, self.ctxs)
                gpu_labels = mx.gluon.utils.split_and_load(label, self.ctxs)
                with mx.autograd.record():
                    # losses = [self.sec_loss(self.net(x), y) for x, y in zip(gpu_datas, gpu_labels)]
                    losses = []
                    for x, y in zip(gpu_datas, gpu_labels):
                        logging.info(f'[train] x: {x.shape}  y: {y.shape}  {x.context}')
                        preds = self.net(x)
                        loss = self.sec_loss(preds, y)
                        logging.info(f'loss: {loss.context}')
                        losses.append(loss)
                    cur_loss = sum([loss.sum().asscalar() for loss in losses])
                    total_loss += cur_loss
                for loss in losses:
                    loss.backward()
                self.trainer.step(self.config.batch_size)
                mx.nd.waitall()
                if idx % self.config.log_interval == 0:
                    logging.info(f'[TRAIN] [{epoch}/{idx}]  loss: {total_loss:8f} / {cur_loss:8f}')
            # self.save_model(self.config.pretrained_name, epoch+1)
            MobileNetV20Transform.export(self.net, self.net, prefix=self.config.pretrained_name, epoch=epoch+1)

            eval_loss = 0
            for idx, (feature, label) in enumerate(self.eval_dataloader):
                gpu_datas = mx.gluon.utils.split_and_load(feature, self.ctxs)
                gpu_labels = mx.gluon.utils.split_and_load(label, self.ctxs)
                # losses = [self.sec_loss(self.net(x), y) for x, y in zip(gpu_datas, gpu_labels)]
                for x, y in zip(gpu_datas, gpu_labels):
                    preds = self.net(x)
                    losses.append(self.sec_loss(preds, y))
                    self.eval_acc.update(y, preds)
                cur_loss = sum([loss.sum().asscalar() for loss in losses])
                eval_loss += cur_loss
                if idx % self.config.log_interval == 0:
                    logging.info(f'[EVAL] [{epoch}/{idx}]  {self.eval_acc.get()[0]}:{self.eval_acc.get()[1]:8f}  {self.eval_acc.get()[0]}:{self.eval_acc.get()[1]:8f}  loss: {eval_loss:8f} / {cur_loss:8f}')

    def eval(self):
        pass





class Trainer1():

    def __init__(self, config):
        assert not isinstance(config, Config), f'config file is not correct!!!'
        self.config = config

        self.ctxs = [mx.gpu(int(i)) for i in config.gpus.split(',')]

        if self.config.with_fit:
            pass
        else:
            self.net = MobileNetV20Transform().download_model(
                num_class=self.config.num_class,
                prefix=self.config.pretrained_name,
                epoch=self.config.pretrained_epoch
            )
            self.net.collect_params().reset_ctx(self.ctxs)

            self.trainer = mx.gluon.Trainer(
                self.net.collect_params(),
                'sgd',
                {'learning_rate': config.learning_rate, 'wd': config.weight_decay}
            )


        self.sec_loss = mx.gluon.loss.SoftmaxCrossEntropyLoss()

        self.train_acc = mx.metric.Accuracy()
        self.eval_acc = mx.metric.Accuracy()

    def collect_data(self):
        if self.config.with_fit:
            self.train_iter = ImageFolderDataIter(
                root=self.config.image_dir,
                data_shape=(3, 128, 128),
                label_shape=(2,),
                data_names=['data'],
                label_names=['softmax_label'],
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label),
                batch_size=self.config.batch_size
            )
            # data_iter = iter(self.train_iter)
            # batch = next(data_iter)
            # logging.info(f'[] label: {batch.label}')
            # # sys.exit(0)
            # self.train_dataset = ImageFolderDataset(
            #     root=config.image_dir,
            #     flag=1,
            #     transform=lambda data, label: (data.astype(np.float32)/255, label)
            # )
            # self.train_dataloader = mx.gluon.data.DataLoader(
            #     dataset=self.train_dataset,
            #     batch_size=self.config.batch_size,
            #     shuffle=True
            # )
            # self.eval_dataset = ImageFolderDataset(
            #     root=config.image_dir,
            #     flag=1,
            #     transform=lambda data, label: (data.astype(np.float32)/255, label)
            # )
            # self.eval_dataloader = mx.gluon.data.DataLoader(
            #     dataset=self.eval_dataset,
            #     batch_size=self.config.batch_size,
            #     shuffle=True
            # )
            # self.train_iter = mx.contrib.io.DataLoaderIter(self.train_dataloader)

        else:
            self.train_dataset = ImageFolderDataset(
                root=config.image_dir,
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label)
            )
            self.train_dataloader = mx.gluon.data.DataLoader(
                dataset=self.train_dataset,
                batch_size=self.config.batch_size,
                shuffle=True
            )
            self.eval_dataset = ImageFolderDataset(
                root=config.image_dir,
                flag=1,
                transform=lambda data, label: (data.astype(np.float32)/255, label)
            )
            self.eval_dataloader = mx.gluon.data.DataLoader(
                dataset=self.eval_dataset,
                batch_size=self.config.batch_size,
                shuffle=True
            )

    def train_with_fit(self):
        sym, arg_params, aux_params = MobileNetV20Transform().load_checkpoints(
            prefix=self.config.pretrained_name+'-sym',
            epoch=self.config.pretrained_epoch
        )
        model = mx.mod.Module(
            symbol=sym,
            context=self.ctxs,
        )
        logging.info(f'[0] {model.output_names}')
        logging.info(f'[0] {model.label_names}')
        logging.info(f'[0] {model.data_names}')
        logging.info(f'[0] {self.train_iter.provide_data}')
        logging.info(f'[0] {self.train_iter.provide_label}')
        logging.info(f'[0] model.data_names: {model.data_names}')
        logging.info(f'[0] model.label_names: {model.label_names}')
        data_shapes = [('data', (self.config.batch_size, 3, 128, 128))]
        label_shapes = [('softmax_label', (self.config.batch_size, ))]
        logging.info(f'[0] data_shapes: {data_shapes}')
        logging.info(f'[0] label_shapes: {label_shapes}')
        model.bind(
            # data_shapes=self.train_iter.provide_data,  # [('data', (self.config.batch_size, 3, 128, 128))],
            # label_shapes=self.train_iter.provide_label,  # [('softmax_label', (self.config.batch_size, self.config.num_class))],
            # data_shapes=self.train_iter.provide_data,  # [('data', (self.config.batch_size, 3, 128, 128))],
            # label_shapes=self.train_iter.provide_label  # [('softmax_label', (self.config.batch_size, self.config.num_class))],
            data_shapes=data_shapes,
            label_shapes=label_shapes,
        )
        logging.info(f'[1] {model.output_names}')
        logging.info(f'[1] {model.label_names}')
        logging.info(f'[1] {model.label_names}  {model.label_shapes}')
        logging.info(f'[1] {model.data_names}  {model.data_shapes}')
        model.set_params(arg_params=arg_params, aux_params=aux_params, allow_missing=False)
        model.fit(
            train_data=self.train_iter,
            optimizer='sgd',
            optimizer_params={'learning_rate': self.config.learning_rate, 'wd': self.config.weight_decay},
            num_epoch=self.config.max_epoch,
            batch_end_callback=[
                mx.callback.Speedometer(self.config.batch_size, 1),
            ],
            epoch_end_callback=mx.callback.do_checkpoint(self.config.pretrained_name, 1),
            eval_metric='acc'
        )

    def train(self):
        if self.config.with_fit:
            self.train_with_fit()
        else:
            self.train_epoch()

    def train_epoch(self):

        for epoch in range(self.config.min_epoch, self.config.max_epoch):
            total_loss = 0
            for idx, (feature, label) in enumerate(self.train_dataloader):
                gpu_datas = mx.gluon.utils.split_and_load(feature, self.ctxs)
                gpu_labels = mx.gluon.utils.split_and_load(label, self.ctxs)
                with mx.autograd.record():
                    # losses = [self.sec_loss(self.net(x), y) for x, y in zip(gpu_datas, gpu_labels)]
                    losses = []
                    for x, y in zip(gpu_datas, gpu_labels):
                        logging.info(f'[train] x: {x.shape}  y: {y.shape}  {x.context}')
                        preds = self.net(x)
                        loss = self.sec_loss(preds, y)
                        logging.info(f'loss: {loss.context}')
                        losses.append(loss)
                    cur_loss = sum([loss.sum().asscalar() for loss in losses])
                    total_loss += cur_loss
                for loss in losses:
                    loss.backward()
                self.trainer.step(self.config.batch_size)
                mx.nd.waitall()
                if idx % self.config.log_interval == 0:
                    logging.info(f'[TRAIN] [{epoch}/{idx}]  loss: {total_loss:8f} / {cur_loss:8f}')
            # self.save_model(self.config.pretrained_name, epoch+1)
            MobileNetV20Transform.export(self.net, self.net, prefix=self.config.pretrained_name, epoch=epoch+1)

            eval_loss = 0
            for idx, (feature, label) in enumerate(self.eval_dataloader):
                gpu_datas = mx.gluon.utils.split_and_load(feature, self.ctxs)
                gpu_labels = mx.gluon.utils.split_and_load(label, self.ctxs)
                # losses = [self.sec_loss(self.net(x), y) for x, y in zip(gpu_datas, gpu_labels)]
                for x, y in zip(gpu_datas, gpu_labels):
                    preds = self.net(x)
                    losses.append(self.sec_loss(preds, y))
                    self.eval_acc.update(y, preds)
                cur_loss = sum([loss.sum().asscalar() for loss in losses])
                eval_loss += cur_loss
                if idx % self.config.log_interval == 0:
                    logging.info(f'[EVAL] [{epoch}/{idx}]  {self.eval_acc.get()[0]}:{self.eval_acc.get()[1]:8f}  {self.eval_acc.get()[0]}:{self.eval_acc.get()[1]:8f}  loss: {eval_loss:8f} / {cur_loss:8f}')

    def eval(self):
        pass




if __name__ == '__main__':

    config = Config1()

    MobileNetV20Transform().transform(
        num_class=config.num_class,
        prefix=config.pretrained_name,
        epoch=config.pretrained_epoch
    )

    trainer = Trainer(config)

    trainer.train()