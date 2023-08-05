from setuptools import setup,find_packages


setup(
    install_requires=['astunparse==1.6.3','attr==0.3.2','attrs==19.3.0','cachetools==3.1.1','certifi==2022.6.15','charset-normalizer==2.1.0','colorama==0.4.5','gast==0.3.3','google-auth==2.9.1','google-auth-oauthlib==0.4.6','google-pasta==0.2.0','googleapis-common-protos==1.56.4','grpcio==1.29.0','gviz-api==1.10.0','h5py==2.10.0','idna==3.3','importlib-metadata==4.12.0','importlib-resources==5.9.0','joblib==1.1.0','keras-nightly==2.10.0.dev2022051807','Keras-Preprocessing==1.1.2','Markdown==3.4.1','MarkupSafe==2.1.1','mpmath==1.2.1','nest-asyncio==1.5.5','numpy>=1.18.5','oauthlib==3.2.0','opt-einsum==3.3.0','pandas==1.3.5','Pillow==9.2.0','portpicker==1.3.9','promise==2.3','protobuf==3.19.4','pyasn1==0.4.8','pyasn1-modules==0.2.8','python-dateutil==2.8.2','pytz==2022.1','requests==2.28.1','requests-oauthlib==1.3.1','retrying==1.3.3','rsa==4.9','scikit-learn==1.0.2','scipy==1.7.3','semantic-version==2.8.5','six==1.16.0','tb-nightly==2.10.0a20220508','tensorboard==2.9.1','tensorboard-data-server==0.6.1','tensorboard-plugin-profile==2.8.0','tensorboard-plugin-wit==1.8.1','tensorflow>=2.3.4','tensorflow-addons>=0.11.2','tensorflow-datasets==4.6.0','tensorflow-estimator==2.3.0','tensorflow-federated==0.17.0','tensorflow-metadata==1.9.0','tensorflow-model-optimization==0.4.1','tensorflow-privacy==0.5.2','termcolor==1.1.0','threadpoolctl==3.1.0','toml==0.10.2','tqdm==4.64.0','typeguard==2.13.3','typing_extensions==4.3.0','urllib3==1.26.10','Werkzeug==2.2.0','wrapt==1.14.1','zipp==3.8.1'],
    name='data_conversion_tff',
    version='1.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/divya034/tff_data_converter',
    license='',
    author='Divya Reddy Polaka',
    author_email='polakadivya.reddy2019@vitstudent.ac.in',
    description='Federated learning library to convert the csv, image or text datasets into federated datasets for clients to run their edge models.'
)
