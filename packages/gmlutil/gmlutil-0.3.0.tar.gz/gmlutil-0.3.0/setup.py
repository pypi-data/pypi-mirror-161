from setuptools import setup

setup(
    name='gmlutil',
    version='0.3.0',    
    description='General Machine Learning Utility Package',
    url='https://github.com/Phillip1982/gmlutil',
    author='Phillip Kim',
    author_email='phillip.kim@ejgallo.com',
    license='BSD 2-clause', ## Change this
    packages=['gmlutil'],
    install_requires=[
		'aiobotocore==2.1.1',
		'awscli==1.22.24',
		'boto3==1.20.24', 
		'botocore==1.23.24', 
		'boto==2.49.0',
		'cx-Oracle==8.3.0',
		'dash==2.0.0',
		'datetime==4.3',
		'fuzzywuzzy==0.18.0',
		'hana-ml==2.11.22020900',
		'imbalanced-learn==0.8.0',
		'jupyter_dash==0.4.0',
		'kmodes==0.11.0',
		'minio==4.0.6',
		'numpy==1.19.5',
		'pandas==1.1.5',
		'plotly==5.4.0',
		'psycopg2-binary==2.9.1',
		'pyhdb==0.3.4',
		'pymssql==2.2.1',
		'pytrends==4.7.3',
		'sqlalchemy-redshift==0.8.6',
		's3transfer==0.5.0',
		'typing_extensions>=4.0'
		'umap-learn==0.5.1'
		'xgboost==1.3.3'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
		'Operating System :: MacOS',
		'Operating System :: Microsoft :: Windows :: Windows XP',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
)
