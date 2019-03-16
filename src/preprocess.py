from scipy import misc
import tensorflow as tf
import numpy as np
import detect_face


class PreProcessor():
    def __init__(self):
        with tf.Graph().as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.85)
            self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            with self.sess.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(self.sess, None)

            self.minsize = 20 # minimum size of face
            self.threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
            self.factor = 0.709 # scale factor

    def align(self,image_path, margin=44, image_size=160):
        img = misc.imread(image_path)
        img = img[:,:,0:3]
        bounding_boxes, _ = detect_face.detect_face(img, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)
        nrof_faces = bounding_boxes.shape[0]
        bb = np.zeros(4, dtype=np.int32)
        if nrof_faces>0:
            det = bounding_boxes[:,0:4]
            img_size = np.asarray(img.shape)[0:2]
            if nrof_faces>1:
                bounding_box_size = (det[:,2]-det[:,0])*(det[:,3]-det[:,1])
                img_center = img_size / 2
                offsets = np.vstack([ (det[:,0]+det[:,2])/2-img_center[1], (det[:,1]+det[:,3])/2-img_center[0] ])
                offset_dist_squared = np.sum(np.power(offsets,2.0),0)
                index = np.argmax(bounding_box_size-offset_dist_squared*2.0) # some extra weight on the centering
                det = (det[index,:])
        else:
            return bb
    
        det = np.squeeze(det)
        bb[0] = np.maximum(det[0]-margin/2, 0)
        bb[1] = np.maximum(det[1]-margin/2, 0)
        bb[2] = np.minimum(det[2]+margin/2, img_size[1])
        bb[3] = np.minimum(det[3]+margin/2, img_size[0])
        cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
        scaled = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
        misc.imsave("temp.png", scaled)
        return bb