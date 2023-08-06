import os
import uuid
import datetime
import json

from tqdm import tqdm
import tensorflow as tf

from dioptra.api import Logger
from dioptra.supported_types import SupportedTypes

class DioptraClassifierCallback(tf.keras.callbacks.Callback):
    
    def __init__(self,
            model_id,
            model_type,
            class_names=None,
            gt_class_names=None,
            dataset_id=None,
            benchmark_id=None,
            evaluation_data=None,
            evaluation_metadata=None,
            **kwargs):
        super().__init__(**kwargs)
        
        dioptra_api_key = os.environ['DIOPTRA_API_KEY']
        dioptra_url = os.environ.get('DIOPTRA_URL', 'https://api/dioptra/ai')
        
        if not dioptra_api_key:
            raise RuntimeError('No API key setup for dioptra. Set the env var DIOPTRA_API_KEY')
            
        if evaluation_data and evaluation_metadata and evaluation_data.n != len(evaluation_metadata):
            raise RuntimeError('evaluation_data and evaluation_metadata should have the same length')

        self.model_id = model_id
        self.model_type = SupportedTypes(model_type)
        self.dataset_id = dataset_id
        self.benchmark_id = benchmark_id
        self.class_names = class_names
        self.gt_class_names = gt_class_names if gt_class_names else class_names
        self.evaluation_data = evaluation_data
        self.evaluation_metadata = evaluation_metadata
        self.logger = Logger(api_key=dioptra_api_key, endpoint_url=dioptra_url, batch_size=5)
        self.logging_layer_names = ['embeddings', 'logits', 'confidences']
        
    def set_params(self, params):
        self.params = params

    def set_model(self, model):
        self.model = model
        
    def on_test_begin(self, logs=None):

        output_layers = {}
        for layer_name in self.logging_layer_names:
            try:                  
                output_layers[layer_name] = self.model.get_layer(layer_name).output
            except Exception as e:
                print(e)
                print(f'Didn\'t find layer named {layer_name}. Skipping ...')
        self.logging_model = tf.keras.Model(inputs=self.model.inputs, outputs=output_layers)
        
        if not output_layers:
            return

        batch_count = 0
        results = []
        
        try:
            self.evaluation_data.reset()
        except:
            # Not a generator...
            pass
        
        data_count = 0

        for x, y in tqdm(self.evaluation_data, desc='Computing stuff for Dioptra...'):
            
            if batch_count >= len(self.evaluation_data):
                break

            predictions = self.logging_model(x)
            
            if 'embeddings' in predictions:
                predictions['embeddings'] = tf.reshape(predictions['embeddings'], [len(x), -1])
            
            for prediction_name in predictions:
                predictions[prediction_name] = tf.cast(predictions[prediction_name], dtype=tf.float16).numpy().tolist()
                
            groundtruth = tf.math.argmax(y, axis=1).numpy()
            
            for i in range(len(x)):
                self.logger.add_to_batch_commit(**{
                    'validate_sample': False,
                    'request_id': str(uuid.uuid4()),
                    'model_type': self.model_type.value,
                    'benchmark_id': self.benchmark_id,
                    'dataset_id': self.dataset_id,
                    'model_id': self.model_id,
                    'groundtruth': self.gt_class_names[groundtruth[i]],
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    **(
                        {
                            'embeddings': predictions['embeddings'][i],
                        } if 'embeddings' in predictions else {}
                    ),
                    'prediction': {
                        **(
                            {
                                'confidence': predictions['confidences'][i]
                            } if 'confidences' in predictions else {}
                        ),
                        **(
                            {
                                'logits': predictions['logits'][i]
                            } if 'logits' in predictions else {}
                        ),
                        'class_name': self.class_names
                    },
                    **(
                        {
                            **self.evaluation_metadata[data_count]
                        } if self.evaluation_metadata and data_count < len(self.evaluation_metadata) else {}
                    )
                })
                data_count += 1
            batch_count += 1
        self.logger.submit_batch()


class DioptraObjectDetectionCallback(tf.keras.callbacks.Callback):

    def __init__(self,
            model_id,
            class_names=None,
            gt_class_names=None,
            dataset_id=None,
            benchmark_id=None,
            evaluation_data=None,
            evaluation_metadata=None,
            **kwargs):
        super().__init__(**kwargs)

        dioptra_api_key = os.environ['DIOPTRA_API_KEY']
        dioptra_url = os.environ.get('DIOPTRA_URL', 'https://api/dioptra/ai')

        if not dioptra_api_key:
            raise RuntimeError('No API key setup for dioptra. Set the env var DIOPTRA_API_KEY')

        if evaluation_data and evaluation_metadata and evaluation_data.n != len(evaluation_metadata):
            raise RuntimeError('evaluation_data and evaluation_metadata should have the same length')

        self.model_id = model_id
        self.model_type = SupportedTypes.OBJECT_DETECTION
        self.dataset_id = dataset_id
        self.benchmark_id = benchmark_id
        self.class_names = class_names
        self.gt_class_names = gt_class_names if gt_class_names else class_names
        self.evaluation_data = evaluation_data
        self.evaluation_metadata = evaluation_metadata
        self.logger = Logger(api_key=dioptra_api_key, endpoint_url=dioptra_url, batch_size=5)
        self.logging_layer_names = ['embeddings', 'nms']

    def set_params(self, params):
        self.params = params

    def set_model(self, model):
        self.model = model

    def on_test_begin(self, logs=None):

        output_layers = {}
        for layer_name in self.logging_layer_names:
            try:
                output_layers[layer_name] = self.model.get_layer(layer_name).output
            except Exception as e:
                print(e)
                print(f'Didn\'t find layer named {layer_name}. Skipping ...')
        self.logging_model = tf.keras.Model(inputs=self.model.inputs, outputs=output_layers)

        if not output_layers:
            return

        batch_count = 0
        results = []

        try:
            self.evaluation_data.reset()
        except:
            # Not a generator...
            pass

        data_count = 0

        for x in tqdm(self.evaluation_data, desc='Computing stuff for Dioptra...'):

            if batch_count >= len(self.evaluation_data):
                break

            predictions = self.logging_model(x['image'])
            groundtruth_boxes = x['objects']['bbox']
            groundtruth_filters = tf.reduce_sum(groundtruth_boxes, axis=-1) > 0
            groundtruth_class_names = tf.gather(self.class_names, x['objects']['label'])

            if 'embeddings' in predictions:
                predictions['embeddings'] = tf.cast(predictions['embeddings'], dtype=tf.float16)

            if 'nms' in predictions:
                boxes = predictions['nms'][0]
                prediction_filters = tf.reduce_sum(boxes, axis=-1) > 0
                confidences = predictions['nms'][1]
                class_names = tf.gather(self.class_names, tf.cast(predictions['nms'][2], dtype=tf.int32))

            for i in range(len(x)):
                self.logger.add_to_batch_commit(**{
                    'validate_sample': False,
                    'request_id': str(uuid.uuid4()),
                    'model_type': self.model_type.value,
                    'benchmark_id': self.benchmark_id,
                    'dataset_id': self.dataset_id,
                    'model_id': self.model_id,
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    **(
                        {
                            'embeddings': predictions['embeddings'][i].numpy().tolist(),
                        } if 'embeddings' in predictions else {}
                    ),
                    **(
                        {
                            'groundtruth': {
                                'boxes': groundtruth_boxes[i][groundtruth_filters[i]].numpy().tolist(),
                                'class_names': groundtruth_class_names[i][groundtruth_filters[i]].numpy().astype(np.str).tolist()
                                }
                        } if len(groundtruth_boxes[i]) else {}
                    ),
                    'prediction': {
                        **(
                            {
                                'boxes': boxes[i][prediction_filters[i]].numpy().tolist()
                            } if 'nms' in predictions else {}
                        ),
                        **(
                            {
                                'confidences': confidences[i][prediction_filters[i]].numpy().tolist()
                            } if 'nms' in predictions else {}
                        ),
                        **(
                            {
                                'classe_names': class_names[i][prediction_filters[i]].numpy().astype(np.str).tolist()
                            } if 'nms' in predictions else {}
                        )
                    },
                    **(
                        {
                            **self.evaluation_metadata[data_count]
                        } if self.evaluation_metadata and data_count < len(self.evaluation_metadata) else {}
                    )
                })
                data_count += 1
            batch_count += 1
        self.logger.submit_batch()
