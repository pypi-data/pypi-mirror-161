import tensorflow as tf

class RoIPooling(tf.keras.layers.Layer):
    """Reducing all feature maps to same size.
    Firstly cropping bounding boxes from the feature maps and then resizing it to the pooling size.
    inputs:
        feature_map = (batch_size, img_output_height, img_output_width, channels)
        roi_bboxes = (batch_size, train/test_nms_topn, [y1, x1, y2, x2])
    outputs:
        final_pooling_feature_map = (batch_size, train/test_nms_topn, pooling_size[0], pooling_size[1], channels)
            pooling_size usually (7, 7)
    """

    def __init__(self, hyper_params, **kwargs):
        super(RoIPooling, self).__init__(**kwargs)
        self.hyper_params = hyper_params

    def get_config(self):
        config = super(RoIPooling, self).get_config()
        config.update({'hyper_params': self.hyper_params})
        return config

    def convert_boxes(self, boxes):
        x1, y1, x2, y2 = tf.split(boxes, (1,1,1,1), axis=-1)
        bbox_y1x1y2x2 = tf.concat([y1, x1, y2, x2], axis=-1)
        return bbox_y1x1y2x2

    def call(self, inputs):
        feature_map = inputs[0]
        roi_bboxes = inputs[1]
        
        roi_bboxes = self.convert_boxes(roi_bboxes)
        
        
        pooling_size = self.hyper_params['pooling_size']
        batch_size, total_bboxes = tf.shape(roi_bboxes)[0], tf.shape(roi_bboxes)[1]
        #
        row_size = batch_size * total_bboxes
        # We need to arange bbox indices for each batch
        pooling_bbox_indices = tf.tile(tf.expand_dims(tf.range(batch_size), axis=1), (1, total_bboxes))
        pooling_bbox_indices = tf.reshape(pooling_bbox_indices, (-1, ))
        pooling_bboxes = tf.reshape(roi_bboxes, (row_size, 4))
        # Crop to bounding box size then resize to pooling size
        
        pooling_feature_map = tf.image.crop_and_resize(
            feature_map,
            pooling_bboxes,
            pooling_bbox_indices,
            pooling_size
        )
        final_pooling_feature_map = tf.reshape(pooling_feature_map, (batch_size, total_bboxes, pooling_feature_map.shape[1], pooling_feature_map.shape[2], pooling_feature_map.shape[3]))
        return final_pooling_feature_map
