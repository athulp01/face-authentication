import tensorflow as tf
import imageio 
import numpy as np
import argparse
import os
import sys
import math
import pickle
import re

class Classify():
    def __init__(self):
        tf.logging.set_verbosity(tf.logging.ERROR)
        self.sess = tf.Session().__enter__()
        self.load_model("./model/")
        self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        self.embedding_size = self.embeddings.get_shape()[1]
        self.emb_array = np.zeros((1, self.embedding_size))

        classifier_filename_exp = os.path.expanduser("classifier.pk")
        with open(classifier_filename_exp, 'rb') as infile:
            (self.model, self.class_names) = pickle.load(infile)

    def __del__(self):
        self.sess.close()

    def predict(self, path):
        image = self.load_image(path)
        self.feed_dict = { self.images_placeholder:image, self.phase_train_placeholder:False }
        self.emb_array[0,:] = self.sess.run(self.embeddings, feed_dict=self.feed_dict)
        predictions = self.model.predict_proba(self.emb_array)
        best_class_indices = np.argmax(predictions, axis=1)
        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
        
        if best_class_probabilities[0] < 0.8:
            return "Unknown face"
        else:
            return (self.class_names[best_class_indices[0]])

    def prewhiten(self, x):
        mean = np.mean(x)
        std = np.std(x)
        std_adj = np.maximum(std, 1.0/np.sqrt(x.size))
        y = np.multiply(np.subtract(x, mean), 1/std_adj)
        return y  
    
    def load_image(self, image_path):
        image = np.zeros((1, 160, 160, 3))
        img = imageio.imread(image_path)
        img = self.prewhiten(img)
        image[0,:,:,:] = img
        return image

    def load_model(self, model="./model"):
        model_exp = os.path.expanduser(model)
        print('Model directory: %s' % model_exp)
        meta_file, ckpt_file = self.get_model_filenames(model_exp)
        
        print('Metagraph file: %s' % meta_file)
        print('Checkpoint file: %s' % ckpt_file)
      
        self.saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file), input_map=None)
        self.saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))

    def get_model_filenames(self, model_dir):
        files = os.listdir(model_dir)
        meta_files = [s for s in files if s.endswith('.meta')]
        if len(meta_files)==0:
            raise ValueError('No meta file found in the model directory (%s)' % model_dir)
        elif len(meta_files)>1:
            raise ValueError('There should not be more than one meta file in the model directory (%s)' % model_dir)
        meta_file = meta_files[0]
        ckpt = tf.train.get_checkpoint_state(model_dir)
        if ckpt and ckpt.model_checkpoint_path:
            ckpt_file = os.path.basename(ckpt.model_checkpoint_path)
            return meta_file, ckpt_file

        meta_files = [s for s in files if '.ckpt' in s]
        max_step = -1
        for f in files:
            step_str = re.match(r'(^model-[\w\- ]+.ckpt-(\d+))', f)
            if step_str is not None and len(step_str.groups())>=2:
                step = int(step_str.groups()[1])
                if step > max_step:
                    max_step = step
                    ckpt_file = step_str.groups()[0]
        return meta_file, ckpt_file






