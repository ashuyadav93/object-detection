#!/usr/bin/env python3
import tensorflow as tf
import os
import tarfile
import numpy as np
from PIL import Image
from models.research.object_detection.utils import label_map_util
from flask import Flask, request
from models.research.object_detection.utils import visualization_utils as vis_util
import json, time
import base64
import io

app = Flask(__name__)

# What model to download.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
MODEL_FILE = MODEL_NAME + '.tar.gz'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('models', 'research', 'object_detection','data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90


# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

PATH_TO_TEST_IMAGES_DIR = 'test_images'
TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'abc.png'.format(i)) for i in range(1, 3) ]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

def load_graph():
	detection_graph = tf.Graph()
	with detection_graph.as_default():
	    od_graph_def = tf.GraphDef()
	    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
		    serialized_graph = fid.read()
		    od_graph_def.ParseFromString(serialized_graph)
		    tf.import_graph_def(od_graph_def, name='')
	return detection_graph
# 
@app.route('/')
def index():
    return "Hello, World!"

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

@app.route('/api/predict', methods=['POST'])
def detect_object():
	# start = time.time()
	data = request.data.decode("utf-8")
	# return data
	# params = json.loads(data)
	imgdata = base64.b64decode(data)
	print (len(imgdata))

	# start = time.time()
	# detection_graph = tf.Graph()
	# with detection_graph.as_default():
	#     od_graph_def = tf.GraphDef()
	#     with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
	# 	    serialized_graph = fid.read()
	# 	    od_graph_def.ParseFromString(serialized_graph)
	# 	    tf.import_graph_def(od_graph_def, name='')
	# print (time.time() - start)
	with detection_graph.as_default():
	  with tf.Session(graph=detection_graph) as sess:
	    image = Image.open(io.BytesIO(imgdata))
	    image_np = load_image_into_numpy_array(image)
	    # Definite input and output Tensors for detection_graph
	    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
	    # Each box represents a part of the image where a particular object was detected.
	    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
	    # Each score represent how level of confidence for each of the objects.
	    # Score is shown on the result image, together with the class label.
	    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
	    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
	    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
	    # for image_path in TEST_IMAGE_PATHS:
	    # image = Image.open(image_path)
	    # the array based representation of the image will be used later in order to prepare the
	    # result image with boxes and labels on it.
	    # image_np = load_image_into_numpy_array(image)
	      # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
	    image_np_expanded = np.expand_dims(image_np, axis=0)
	      # Actual detection.
	    (boxes, scores, classes, num) = sess.run(
	          [detection_boxes, detection_scores, detection_classes, num_detections],
	          feed_dict={image_tensor: image_np_expanded})
	      # Visualization of the results of a detection.
	    vis_util.visualize_boxes_and_labels_on_image_array(
	          image_np,
	          np.squeeze(boxes),
	          np.squeeze(classes).astype(np.int32),
	          np.squeeze(scores),
	          category_index,
	          use_normalized_coordinates=True,
	          line_thickness=8)
	      
	      #json_data =  json.dumps({'image': image_np.tolist()})

	      # with open('/Users/ashishyadav/Desktop/out.txt', 'w') as outfile:
	      # 	json.dump(json_data, outfile)

	      #return json_data
	    # print (image_np.tobytes())
	    im = Image.fromarray(image_np)
	    imbyte = io.BytesIO()
	    im.save(imbyte, format='PNG')
	    return base64.b64encode(imbyte.getvalue())
	    # with open("result.png", "rb") as image_file:
	    #     encoded_string = base64.b64encode(image_file.read())
	    #     print (type(image_file.read()))
	    # print (time.time() - start)

	    #return encoded_string
	      #data# = base64.b64encode(im.tobytes())
	      # return data
	      # with open('/Users/ashishyadav/oshw/test_images/def.png', 'wb') as file:
	      #    file.write(imdata)


if __name__ == "__main__":
	# detect_object()
	detection_graph = load_graph()
	app.run(debug=True, host= '0.0.0.0', processes=3)

	# with detection_graph.as_default():
	# 	detection_graph = tf.Graph()
	# 	od_graph_def = tf.GraphDef()
	# 	with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
	# 		serialized_graph = fid.read()
	# 		od_graph_def.ParseFromString(serialized_graph)
	# 		tf.import_graph_def(od_graph_def, name='')
	# 	sess = tf.Session(graph=detection_graph)
	



