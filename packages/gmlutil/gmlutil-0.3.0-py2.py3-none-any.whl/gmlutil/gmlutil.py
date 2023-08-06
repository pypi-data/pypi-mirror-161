# from pandas.core.strings import str_count
import boto3
import datetime
import hana_ml
import io
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import sqlalchemy as sa
import sys
import time
import umap.umap_ as umap
from fuzzywuzzy import fuzz
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline
from io import BufferedReader, TextIOWrapper
from kmodes.kmodes import KModes
from kmodes.kprototypes import KPrototypes
from minio import Minio
from minio.error import ResponseError
from numpy import mean
from numpy import std
from pytrends.request import TrendReq
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, PowerTransformer, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, RepeatedStratifiedKFold
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, StackingClassifier
from sklearn.metrics import classification_report, confusion_matrix, plot_confusion_matrix
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, SpectralClustering, AgglomerativeClustering, DBSCAN, Birch
from sklearn.manifold import TSNE
from sklearn.mixture import GaussianMixture
from sqlalchemy import Table, MetaData, select, delete
from statsmodels.tsa.stattools import adfuller
from types import SimpleNamespace
from xgboost import XGBClassifier

limit = np.int64(10**9 * 2.1)
sys.setrecursionlimit(limit)

run_mode = "cloud"
if run_mode == "local":
	path_to_folder = '../'
	sys.path.append(path_to_folder)
	import credentials as cred
else:
	def credf(keys):
		client = boto3.client('secretsmanager', region_name = 'us-west-2')
		if keys == "redshift":
			response = client.get_secret_value(SecretId='ejgallo-prophet-redshift')
			database_secrets = json.loads(response['SecretString'])
			cred = SimpleNamespace(**database_secrets)
		else:
			response = client.get_secret_value(SecretId='ejgallo-prophet-dev-masterkeys')
			database_secrets = json.loads(response['SecretString'])
			cred = SimpleNamespace(**database_secrets)
		return cred
	cred = credf('master')
	credr = credf('redshift')


########################### Data Extraction ###########################
class data_extraction:
	def __init__(self):
		pass

	def hana_connection(self):
		conn = hana_ml.dataframe.ConnectionContext(
			address= cred.HANA_ADDRESS,
			port=cred.HANA_PORT,
			user=cred.HANA_USER,
			password=cred.HANA_PASSWORD
			)
		return conn

	def sg_upload_to_s3(self, df, bucket_name, file_name):
		role = get_execution_role()
		sess = sagemaker.Session()
		region = boto3.session.Session().region_name
		sm = boto3.Session().client('sagemaker')
		df.to_csv('{}'.format(file_name, index=None))
		data_location = sess.upload_data(path='data', bucket=bucket_name, key_prefix='data')
		print("Uploading is successful...")

	def sg_reading_in_from_s3(self, bucket_name, file_name,dtypes = None):
		role = get_execution_role()
		data_location = 's3://{}/{}'.format(bucket_name, file_name)
		df = pd.read_csv(data_location, low_memory=False, dtype = dtypes) # , on_bad_lines='skip')
		return df

	def lc_upload_to_s3(self, df, bucket_name, file_name):
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		KEY = '{}'.format(file_name)
		df.to_csv('buffer')
		s3c.upload_file(Bucket = bucket_name, Filename = 'buffer', Key = KEY)
		print("Uploading is successful...")

#     def lc_reading_in_from_s3(self, bucket_name, file_name, dtypes = None):
#         s3c = boto3.client(
#                 's3', 
#                 region_name = cred.AWS_DEV_REGION_NAME,
#                 aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
#                 aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
#             )
#         KEY = '{}'.format(file_name)
#         obj = s3c.get_object(Bucket=bucket_name, Key = KEY)                         
#         df = pd.read_csv(io.BytesIO(obj['Body'].read()) , encoding='utf8', low_memory=False, dtype = dtypes) # , on_bad_lines='skip')
#         return df

	def lc_reading_in_from_s3(self, bucket_name, file_name, dtypes = None):
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		KEY = '{}'.format(file_name)
		obj = s3c.get_object(Bucket=bucket_name, Key = KEY)
		streaming_body = obj['Body']
		content_len = obj['ContentLength']
		buffered_io = S3StreamingBodyIO(streaming_body._raw_stream, content_len)
		df = pd.read_csv(io.BytesIO(buffered_io.read()), encoding='utf8', low_memory=False, dtype = dtypes) # on_bad_lines='skip')
		return df

	def lcm_upload_to_s3(self, bucket, file_name):
		client = Minio("s3.amazonaws.com",
					   access_key= cred.AWS_DEV_ACCESS_KEY,
					   secret_key= cred.AWS_DEV_SECRET_KEY,
					   secure=True)
		print("Saving... data in {} at {}".format(bucket, file_name))
		print()
		try:
			client.fput_object(bucket, file_name, file_name, content_type="application/csv")
			return True
		except ResponseError as err:
			print(err)
			return False

	def lcm_reading_in_from_s3(self, bucket, file_name):
		client = Minio("s3.amazonaws.com",
					   access_key= cred.AWS_DEV_ACCESS_KEY,
					   secret_key= cred.AWS_DEV_SECRET_KEY,
					   secure=True)
		print("Loading... data from {} at {}".format(bucket, file_name))
		print()
		try:
			client.fget_object(bucket, file_name, file_name)
			return True
		except ResponseError as err:
			print(err)
			return False

	def rs_data_connection(self):
		engine_string = 'redshift+psycopg2://{}:{}@data-lake.cwjgbxpbqebs.us-west-2.redshift.amazonaws.com:5439/prophet'.format(credr.username, credr.password)
		conn = sa.create_engine(engine_string)
		return conn

	def rs_data_extraction_str(self, table_name, schema_name='prophet'):
		metadata = MetaData()
		conn = self.rs_data_connection()
		dt = Table(table_name, metadata, autoload=True, autoload_with=conn, schema=schema_name)
		df_columns = dt.columns.keys()
		return dt, conn, df_columns

	def rs_data_insertion(self, df, table_name, schema_name='prophet'):
		conn = self.rs_data_connection()
		df_length = len(df)
		cindex = 0
		nindex = 100
		while cindex < df_length:
			if cindex < df_length:
				if nindex >= df_length:
					nindex = df_length
				df_portion = df[cindex:nindex]
				print("Inserting {}-{}th data rows...".format(cindex, nindex))
				df_portion.to_sql(table_name, conn, index=False, if_exists='append', schema=schema_name) ##### change to append
				cindex += 100
				nindex += 100   
		print("Data successfully inserted...")

	def rs_data_deletion(self, table_name, schema_name='prophet'):
		metadata = MetaData()
		conn = self.rs_data_connection()
		dt = Table(table_name, metadata, autoload=True, autoload_with=conn, schema=schema_name)
		delete_stmt = dt.delete()
		results = conn.execute(delete_stmt)
		print("The number of rows deleted are {}...".format(results.rowcount))    
	
	def lambda_function(self, bucket_name, number):
		today = datetime.datetime.now()
		today = today.strftime("%m%d%Y")
		file_name = "prophet/lambda_cues/lambda_{}/".format(number) + today + ".csv"
		df = pd.DataFrame([])
		self.lc_upload_to_s3(df, bucket_name, file_name) ##### change this to SageMaker
		print("Finished the Lambda {} Process...".format(number))
		print()
	
	# PYTRENDS FUNCTION THAT GETS TRENDING CITIES BASED ON KEYWORD(BRAND)
	def get_google_city(self, keyword):
		"""generates the google trends piece from a keyword that is entered(benchmark)
		Args:
			keyword (str): planning brand that is entered in order to generate city list
		Returns:
			df: cities that are trending for the keyword
		"""
		print('gathering google trends data')
		pytrends = TrendReq(hl='en-US')
		# Building our payload for the trends query
		cat = '71'
		geo = 'US'
		gprop = ''
		keywords = [keyword]
		timeframe = 'today 3-m'
		# Pytrends function to get google data
		pytrends.build_payload(keywords, cat,
						   timeframe,
						   geo,
						   gprop)
		try:
			output= pytrends.interest_by_region(resolution='DMA', inc_low_vol=True, inc_geo_code=True)
			city_queries = output[output[keywords[0]] > 30]
			city_queries['Google'] = 'Y'
			city_queries = city_queries[['geoCode','Google']]
		except:
			city_queries = pd.DataFrame([], columns=['geoCode','Google'])
		time.sleep(1)
		return city_queries

	# READING IN ACV DATA
	def read_acv(self):
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		"""gets our acv curves from s3 in order to run the distributor path option for upcs
		Returns:
			 df: acv_df is the accounts with the respective net list running percent for each category and tier 
		"""
		bucket='ejgallo-lake-sales-dev'
		key = '2021/benchmark/data/acv_curves.csv'
		obj = s3c.get_object(Bucket= bucket , Key = key)
		acv_df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8',low_memory = False)
		columns = ['9L VOLUME','PHYS VOLUME','NET LIST DOLLARS']
		for column in columns:
			acv_df[column] = round(acv_df[column],2)
		columns = ['nl_percent','nl_running_percent']
		for column in columns:
			acv_df[column] = round(acv_df[column],4)
		acv_df['Rtl_Acct_ID'] = acv_df['Rtl_Acct_ID'].astype(int)
		acv_df['geoCode'] = acv_df['geoCode'].astype(str)
		acv_df['concat'] = acv_df['Mkt_Grp_State'] + ' ' + acv_df['Acct_City']
		acv_df['concat'] = acv_df['concat'].astype(str)
		unique_citystates = acv_df[['Mkt_Grp_State','Acct_City','concat']].drop_duplicates()
		# Read in geocodes and fuzzy match them--> need to do ts cause some cities have different spellings from the hana side
		bucket='ejgallo-lake-sales-dev'
		key = '2021/benchmark/data/geo_codes.csv'
		obj = s3c.get_object(Bucket= bucket , Key = key)
		geo_codes = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8',low_memory = False)
		geo_codes['concat'] =geo_codes['Mkt_Grp_State'] + ' ' + geo_codes['City']
		matchers = {}
		for j in unique_citystates['concat']:
			for i in geo_codes['concat']:
				if (j[:2] == i[:2]):
					if fuzz.ratio(i,j) > 90:
						matchers[j] = i
		acv_df['new_concat'] = acv_df['concat'].map(matchers)
		acv_df_new = acv_df.merge(geo_codes[['geoCode','concat']],left_on = 'new_concat',right_on = 'concat',how='left')
		acv_df_new['new_concat'] = acv_df_new['new_concat'].astype(str)
		acv_df_new = acv_df_new.drop(['geoCode_x','concat_x','concat_y','new_concat','geoCode_x'],axis = 1)
		acv_df_new = acv_df_new.rename(columns = {'geoCode_y':'geoCode'})
		acv_df_new['geoCode'] =acv_df_new['geoCode'].astype(str)
		acv_df_new['State'] = np.where(acv_df_new['State'] == 'New Mexico','New_Mexico',acv_df_new['State'])
		acv_df_new['State'] = np.where(acv_df_new['State'] == 'DC','District of Columbia',acv_df_new['State'])
		return acv_df_new

	# GETTING OUR UPCS DF WCH CONTAINS CATEGORY AND PRICE TIER FOR INDIVIDUAL ITEMS
	def read_upc_df(self):
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		"""gets our upc df: a dataframe with all upcs and thier corresponding price tier and category
		Returns:
			[df]: [upc_df is all upcs and their corresponding price tier and category: to be merged onto acv df]
		"""
		bucket='ejgallo-lake-sales-dev'
		key = '2021/benchmark/data/UPC_Tier_Dict.csv'
		obj = s3c.get_object(Bucket= bucket , Key = key)
		upc_df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8',low_memory = False)
		# Add leading zeros to UPC to match Gallo data
		upc_df['UPC'] = upc_df['UPC'].astype(int)
		upc_df['UPC'] = upc_df['UPC'].astype(str).str.rjust(12, "0")
		return upc_df


########################### Buffer Streaming Processing ###########################

class S3StreamingBodyIO(BufferedReader):
	def __init__(self, buffer, content_len):
		self.buffer = buffer
		self.content_len = content_len
	def read(self, *args):
		MAX_SSL_CONTENT_LENGTH = limit
		size = self.content_len
		if size > MAX_SSL_CONTENT_LENGTH:
			data_out = bytearray()
			remaining_size = size
			i = 1
			while remaining_size > 0:
				print("iteration {} and remaining size {}...".format(str(i), remaining_size))
				chunk_size = min(remaining_size, MAX_SSL_CONTENT_LENGTH)
				data_out += self.buffer.read(chunk_size)
				remaining_size = remaining_size - chunk_size
				i += 1
			return data_out
		else:
			return self.buffer.read(size)


########################### Prime Directive Processing ###########################

class prime_directive:
	def __init__(self, change_names = {'FINE_WINE':'Fine_Wine_Acct_Flag', 'INFLUENCER':'Fine_Wine_Inflncr_Acct_Flag','ICON':'Fine_Wine_Icon_Acct_Flag'}):
		self.change_names = change_names

	def search_func(self, upc_value, platform='cloud', bucket_name='ejgallo-lake-sales-dev', file_name='2021/prime_directive/off_brand_standards_Q2.csv'):
		de = data_extraction()
		if platform == "sagemaker":
			brand_standards = de.sg_reading_in_from_s3(bucket_name, file_name,dtypes = {'UPC':str})
		elif platform == "local":
			brand_standards = pd.read_csv("../data/off_brand_standards.csv", low_memory=False, dtypes = {'UPC':str})
		else:
			brand_standards = de.lc_reading_in_from_s3(bucket_name, file_name, dtypes = {'UPC':str})
		brand_standards['UPC'] = brand_standards['UPC'].astype(str).str.zfill(12)
		upc_search = brand_standards[brand_standards['UPC'] == upc_value].drop_duplicates()
		try:
			upc_search = upc_search.rename(columns = self.change_names)
			upc_search.columns = map(str.lower, upc_search.columns)
		except:
			print("No such columns exist...")
			print()
		search_dict = upc_search.to_dict('records')[0]
		return search_dict

	def standards_check(self, dictionary, zone, channel, icon, influencer, finewine, gsp):
		#zone checker
		check_value = 0
		if dictionary['segmentation'] == 'BROAD':
			return 'Y'
		else:
			check_value += int(dictionary[zone.lower()])
			#channel of dist checker
			check_value += int(dictionary[channel.lower()])
			#icon checker
			#influencer checker
			if dictionary['fine_wine_acct_flag'] == 1:
				check_value += finewine
			elif dictionary['fine_wine_inflncr_acct_flag'] == 1:
				check_value += influencer
			#fine wine checker
			elif dictionary['fine_wine_icon_acct_flag'] == 1:
				check_value += icon
			#we're going to vet liquor items
			if (dictionary['gsp'] == 1) and (dictionary['not_gsp'] == 1) :
				check_value += 1
			elif dictionary['gsp'] == 1:
				check_value += gsp
			elif dictionary['not_gsp'] == 1:
				check_value -= gsp
			if (dictionary['segmentation'] == 'GSP') and (check_value == 3) and (gsp == 1):
				return 'Y'
			else:
				if check_value == 4:
					return 'Y'
				else:
					return 'N'

	def create_score(self, check_value):
		if check_value == 'Y':
			return 1
		elif check_value == 'N':
			return 0
		elif  check_value in ['Gold','Silver']:
			return 1
		else:
			return 0

	def brand_standard_process(self, df):
		if len(df) != 0:
			#what Patrick is changing
#             df.columns = df.columns.str.lower()
			df['UPC'] = df['UPC'].astype(str).str.zfill(12)
			try:
				upc_list = list(set(df['UPC']))
			except:
				upc_list = list(set(df['UPC']))
			brand_standard_list = []
			standard_change = ['Fine_Wine_Acct_Flag','Fine_Wine_Inflncr_Acct_Flag', 'Fine_Wine_Icon_Acct_Flag',
				   'Prem_Spirit_Acct_Flag', 'Whiskey_Segment']
			standard_change = [element.lower() for element in standard_change]
			store_list = ['GROCERY','LIQUOR','CONVENIENCE','DRUG','MASS MERCHANDISER','ALL OTHER-OFF SALE','DOLLAR','CLUB']
			for upc in upc_list:
				try:
					search_dict = self.search_func(upc)
					upc_df = df[df['UPC']==upc]
					upc_df = upc_df.rename(columns = self.change_names)
					upc_df.columns = map(str.lower, upc_df.columns)
					for i in standard_change:
						upc_df[i] = upc_df[i].apply(lambda x: self.create_score(x))
					upc_df['gsp'] = np.where((upc_df['prem_spirit_acct_flag'] ==1) | (upc_df['whiskey_segment'] == 1),1,0)
					upc_df['zone_check'] = np.where(upc_df['key_acct_zone'].str.contains('1|2|3'),'zone1_3','zone4_5')
					upc_df = upc_df[upc_df['channel_of_distribution'].isin(store_list)]
					upc_df['standards_check'] = upc_df.apply(lambda x: self.standards_check(search_dict,x['zone_check'],x['channel_of_distribution'],
																   x['fine_wine_icon_acct_flag'],x['fine_wine_inflncr_acct_flag'],
																  x['fine_wine_acct_flag'],x['gsp']), axis = 1)
					upc_df = upc_df[upc_df['standards_check'] == 'Y']
				except Exception as err:
					# print('passing this upc {}... {}...'.format(upc, err))
					continue
				brand_standard_list.append(upc_df)
			try:
				brand_standard_df = pd.concat(brand_standard_list)
			except:
				print("Concat failed...")
				brand_standard_df = pd.DataFrame([], columns=df.columns)
		else:
			print("Data Empty...")
			brand_standard_df = df.copy()
		return brand_standard_df

########################### Data Cleaning ###########################
class data_cleaning:
	def __init__(self):
		pass
	def dec_to_perc(self, num):
		perc = str(round(num * 100, 2)) + "%"
		return perc
	def remove_decimal(self, word):
		new_word =  re.sub('(\.0+)','',word)
		return new_word
	def oned_cross_merging(self, df1, df2):
		df1['key'] = 1
		df2['key'] = 1
		df = pd.merge(df1, df2, on ='key').drop("key", 1)
		return df
	def clean_upc(self, upc):
		"""need to clean some upcs in order to account for zfill and other objects 
		Args:
			upc ([str]): [unique identifier of item]
		Returns:
			[str]: [refurbished upc item]
		"""
		if upc[0] != '0':
			upc = '0' + upc[:-1]
			return upc
		else:
			return upc

########################### Data Conversion to Numerical Data ###########################
class data_conversion:
	def __init__(self, categorical_list, numerical_list):
		self.categorical_list = categorical_list
		self.numerical_list = numerical_list
		self.bucket_name = 'ejgallo-lake-sales-dev'
		self.dictionary_name = 'prophet/model_weights/labels'

	def load_labels(self, label_name):
		bucket_name = self.bucket_name
		directory_name = self.dictionary_name
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		KEY = '{}/labels_{}.pickle'.format(self.dictionary_name, label_name)
		try:
			obj = s3c.get_object(Bucket=bucket_name, Key = KEY)
			label_dict = pickle.loads(obj['Body'].read())
		except Exception as err:
			print("Label does not exist for {}...".format(label_name))
			print()
			label_dict = {}
		return label_dict

	def save_labels(self, label_dict, label_name):
		bucket_name = self.bucket_name
		directory_name = self.dictionary_name
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		KEY = '{}/labels_{}.pickle'.format(self.dictionary_name, label_name)
		try:
			serialized_df = pickle.dumps(label_dict)
			s3c.put_object(Bucket=bucket_name, Key=KEY, Body=serialized_df)
			print("Label successfully saved for {}...".format(label_name))
			print()
		except Exception as err:
			print("Error while saving a label file for {}...".format(str(err)))
			print()         

	def data_conversion_cat(self, df, label_name):
		df_num = df[self.numerical_list]
		label_dict = self.load_labels(label_name)
		if self.categorical_list != []:
			print("Detected categorical list for sustainable growth...")
			df_cat = df[self.categorical_list]
			if label_dict == {}:
				for category in self.categorical_list:
					label_encoder = LabelEncoder()
					df_cat.loc[:,category] = label_encoder.fit_transform(df_cat.loc[:,category]) # use label_encoder.inverse_transform(data) to go back to original labels
					label_dict[category] = label_encoder
				self.save_labels(label_dict, label_name)
			else:
				for category in self.categorical_list:
					label_encoder = label_dict[category]
					df_cat.loc[:,category] = label_encoder.transform(df_cat.loc[:,category])
			df = pd.concat([df_cat, df_num], axis=1)
		else:
			print("There is no categorical list for sustainable growth...")
			df = df_num
		return df, label_dict

	def data_conversion_cat_onehot(self, df):
		df_num = df[self.numerical_list]
		if self.categorical_list != []:
			df_cat = df[self.categorical_list]
			df_cat = pd.get_dummies(df_cat)
			df = pd.concat([df_cat, df_num], axis=1)
		else:
			df = df_num
		return df

	def data_conversion_num(self, df, scaler_type = "minmax"):
		categorical_list = list(df.columns)
		categorical_list = [category for category in categorical_list if category not in self.numerical_list]
		df_cat = df[categorical_list]
		df_num = df[self.numerical_list]
		for variable in self.numerical_list:
			if scaler_type == "minmax":
				scaler = MinMaxScaler()
			elif scaler_type == "power":
				scaler = PowerTransformer()
			else:
				scaler = StandardScaler()
			df_num.loc[:,variable] = scaler.fit_transform(np.array(df_num.loc[:,variable]).reshape(-1, 1))
		df = pd.concat([df_cat, df_num], axis=1)
		return df

########################### Data Preparation ###########################
class data_preparation:
	def __init__(self):
		pass

	def train_testsets(self, df, target_label, test_size=0.3, oversampling="no", oversampling_strategy="minority", undersampling="no", undersampling_strategy="majority"):
		y = df[target_label]
		X = df.drop(columns=[target_label])
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
		if oversampling.lower() == "yes":
			if oversampling_strategy == "minority":
				over = SMOTE(sampling_strategy='minority')
			else:
				over = SMOTE(sampling_strategy='auto')
		if undersampling.lower() == "yes":
			if undersampling_strategy == "majority":
				under = RandomUnderSampler(sampling_strategy = 'majority')
			else:
				under = RandomUnderSampler(sampling_strategy = 'auto')
		if oversampling.lower() == "yes" and undersampling.lower() == "yes":
			steps = [('o', over), ('u', under)]
			pipeline = Pipeline(steps=steps)
			X_train, y_train = pipeline.fit_resample(X_train, y_train)
		elif oversampling.lower() == "yes" and undersampling.lower() != "yes":
			steps = [('o', over)]
			pipeline = Pipeline(steps=steps)
			X_train, y_train = pipeline.fit_resample(X_train, y_train)
		elif oversampling.lower() != "yes" and undersampling.lower() == "yes":
			steps = [('u', under)]
			pipeline = Pipeline(steps=steps)
			X_train, y_train = pipeline.fit_resample(X_train, y_train)
		return X_train, X_test, y_train, y_test

########################### Data Visualization ###########################
class data_visualization:
	def __init__(self):
		pass

	def plot_confusion(self, model, X, y, class_names, normalized='true'):
		titles_options = [("Confusion matrix, without normalization", None),
						  ("Normalized confusion matrix", normalized)]
		for title, normalize in titles_options:
			display = plot_confusion_matrix(model, X, y,
										 display_labels=class_names,
										 cmap=plt.cm.Blues,
										 normalize=normalize)
			display.ax_.set_title(title)
			print(title)
			print(display.confusion_matrix)
		plt.show()

	def data_visualization(self, df, column_list, removal_list, title, x_axis):
		try:
			df = df.drop(removal_list, axis=1)
		except:
			pass
		sqrt_num = int(math.sqrt(len(column_list)))
		if sqrt_num ** 2 < len(column_list):
			plot_size = sqrt_num + 1
		else:
			plot_size = sqrt_num
		fig, axes = plt.subplots(plot_size, plot_size, figsize=(len(column_list)*5, len(column_list)*5))
		fig.suptitle(title)
		i, j = 0, 0
		for column in column_list:
			df[column] = df[column].astype(int)
			df[x_axis] = df[x_axis].astype(int)
			x = x_axis
			axes[i, j].set_title(column)
			sns.lineplot(ax=axes[i, j],data=df,x=x,y=column,lw=1)
	#         sns.lineplot(ax=axes[i, j],data=df,x='Month_Day_Time',y=column,
	#                      hue='City',lw=1)
	#         sns.lineplot(ax=axes[i, j],data=df,x='Month_Day_Time',y=column,
	#                      hue="chain_store",estimator=None)
			i += 1
			if i == plot_size:
				i = 0
				j += 1

	def elbow_graph(self, df, model_name='KMEANS', range_start=1, range_end=11):
		distortions = []
		for i in range(1,11):
			print("Fitting cluster {}...".format(i))
			if model_name == "KMEANS":
				km = KMeans(n_clusters=i, init='random',n_init=10,max_iter=100,tol=1e-04)
				km.fit(df)
				distortions.append(km.inertia_)
			elif model_name == "KPROTO":
				km = KPrototypes(n_clusters=i, init='Huang',n_init=10,max_iter=100,n_jobs=-1)
				km.fit(df, categorical=list(range(len(categorical_list))))
				distortions.append(km.cost_)
		plt.plot(range(range_start,range_end), distortions, marker='o')
		plt.xlabel('Number of clusters')
		plt.ylabel('Distortion')
		plt.show()

	def pca_graph(self, df, pca_percent=0.99):
		df = df.fillna(0)
		model_pca = PCA(pca_percent)
		pca_transformed = model_pca.fit_transform(df)
		components = model_pca.components_
		colors = ["C" + str(index) for index,_ in enumerate(components[0])]
		print("Explained Variance Ratios for PC1 and PC2: ", model_pca.explained_variance_ratio_)
		print()
		labels = {
			str(i): f"PC {i+1} ({var:.1f}%)"
			for i, var in enumerate(model_pca.explained_variance_ratio_ * 100)
		}
		fig = px.scatter_matrix(
			pca_transformed,
			labels=labels,
			dimensions=components,
			color=colors)
		fig.update_traces(diagonal_visible=False)
		fig.show()

	def tsne_graph(self, df):
		model_tsne = TSNE(learning_rate=100)
		model_name = "TSNE"
		transformed = model_tsne.fit_transform(df)
		x_axis = transformed[:, 0]
		y_axis = transformed[:, 1]
		plt.scatter(x_axis, y_axis)
		print(model_name)
		plt.show()

	def umap_graph(self, df):
		numerical_df = df.select_dtypes(exclude='object')
		for c in numerical.columns:
			pt = PowerTransformer()
			numerical_df.loc[:, c] = pt.fit_transform(np.array(numerical_df[c]).reshape(-1, 1))
		categorical_df = df.select_dtypes(include='object')
		categorical_df = pd.get_dummies(categorical)
		categorical_weight = len(df.select_dtypes(include='object').columns) / len(df.columns)
		fit1 = umap.UMAP(metric='l2').fit(numerical_df)
		fit2 = umap.UMAP(metric='dice').fit(categorical_df)
		intersection = umap.general_simplicial_set_intersection(fit1.graph_, fit2.graph_, weight=categorical_weight)
		intersection = umap.reset_local_connectivity(intersection)
		embedding = umap.simplicial_set_embedding(fit1._raw_data, intersection, fit1.n_components, 
														fit1._initial_alpha, fit1._a, fit1._b, 
														fit1.repulsion_strength, fit1.negative_sample_rate, 
														200, 'random', np.random, fit1.metric, 
														fit1._metric_kwds, False)
		plt.figure(figsize=(20, 10))
		plt.scatter(*embedding.T, s=2, cmap='Spectral', alpha=1.0)
		plt.show()
	

########################### Model Training ###########################
class model_training:
	def __init__(self):
		self.bucket_name = 'ejgallo-lake-sales-dev'
		self.dictionary_name = 'prophet/model_weights/models'

	def load_model_trained(self, model_name, label_name):
		bucket_name = self.bucket_name
		directory_name = self.dictionary_name
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		KEY = '{}/{}_model_trained_{}.pickle'.format(directory_name, model_name, label_name)
		try:
			obj = s3c.get_object(Bucket=bucket_name, Key = KEY)
			model_trained = pickle.loads(obj['Body'].read())
			return model_trained
		except Exception as err:
			print("Loading failed for {}...".format(str(err)))
			print()
	def save_model_trained(self, model_trained, model_name, label_name):
		bucket_name = self.bucket_name
		directory_name = self.dictionary_name
		s3c = boto3.client(
				's3', 
				region_name = cred.AWS_DEV_REGION_NAME,
				aws_access_key_id = cred.AWS_DEV_ACCESS_KEY,
				aws_secret_access_key = cred.AWS_DEV_SECRET_KEY
			)
		KEY = '{}/{}_model_trained_{}.pickle'.format(directory_name, model_name, label_name)
		try:
			serialized_df = pickle.dumps(model_trained)
			s3c.put_object(Bucket=bucket_name, Key=KEY, Body=serialized_df)
			print("Model Successfully Saved...")
			print()
		except Exception as err:
			print("Error while saving a pickle file for {}...".format(str(err)))
			print()

	def ba_model(self, X_train, X_test, y_train, y_test):
		model_trained = BaggingClassifier()
		cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=2)
		n_scores = cross_val_score(model_trained, X_train, y_train, scoring='accuracy', cv=cv, error_score='raise')
		print('> Bagging Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
		print()
		model_trained.fit(X_train, y_train)
		prediction = model_trained.predict(X_test)
		print(classification_report(y_test, prediction))
		return model_trained

	def rf_model(self, X_train, X_test, y_train, y_test):
		model_trained = RandomForestClassifier()
		cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
		n_scores = cross_val_score(model_trained, X_train, y_train, scoring='accuracy', cv=cv, error_score='raise')
		print('> Random Forest Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
		print()
		model_trained.fit(X_train, y_train)
		prediction = model_trained.predict(X_test)
		print(classification_report(y_test, prediction))
		return model_trained

	def build_stacking(self):
		level0 = list()
		level0.append(('lr', LogisticRegression()))
		level0.append(('knn', KNeighborsClassifier()))
		level0.append(('cart', DecisionTreeClassifier()))
		level0.append(('svm', SVC()))
		level0.append(('bayes', GaussianNB()))
		level1 = LogisticRegression()
		model = StackingClassifier(estimators=level0, final_estimator=level1, cv=5)
		return model

	def model_stacking(self):
		models = dict()
		models['lr'] = LogisticRegression(max_iter=1000)
		models['knn'] = KNeighborsClassifier()
		models['cart'] = DecisionTreeClassifier()
		models['svm'] = SVC()
		models['bayes'] = GaussianNB()
		models['stacking'] = self.build_stacking()
		return models

	def evaluate_stacking(self, model, X, y):
		cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
		scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, error_score='raise')
		return scores

	def st_model(self, X_train, X_test, y_train, y_test):
		models = self.model_stacking()
		model_name = "Stacking"
		results, names = list(), list()
		for name, model in models.items():
			scores = self.evaluate_stacking(model, X_train, y_train)
			results.append(scores)
			names.append(name)
			print('> %s %.3f (%.3f)' % (name, mean(scores), std(scores)))
		print()
		plt.boxplot(results, labels=names, showmeans=True)
		plt.show()
		model_trained = models['stacking']
		model_trained.fit(X_train, y_train)
		print()
		prediction = model_trained.predict(X_test)
		print(classification_report(y_test, prediction))
		return model_trained

	def xgb_model(self, X_train, X_test, y_train, y_test):
		model_trained = XGBClassifier()
		model_name = "XGB"
		cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
		n_scores = cross_val_score(model_trained, X_train, y_train, scoring='accuracy', cv=cv)
		print('> XGB Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
		print()
		model_trained.fit(X_train, y_train)
		print()
		prediction = model_trained.predict(X_test)
		print(classification_report(y_test, prediction))
		return model_trained

	def xgb_feature(self, model, column_names):
		column_names = list(column_names)
		importance = model.feature_importances_
		print()
		max_importance_index = {}
		for i,v in enumerate(importance):
			print('Feature: {}, Score: {}'.format(column_names[int(i)],round(v,5)))
			max_importance_index[i] = v
		max_importance_index = dict(sorted(max_importance_index.items(), key=lambda item: item[1], reverse=True))
		plt.bar([x for x in range(len(importance))], importance)
		plt.show()
		return max_importance_index

	def kmeans_model(self, df, n_clusters=4, algorithm='elkan'):
		model_trained = KMeans(algorithm=algorithm, n_clusters=n_clusters)
		model_trained.fit(df)
		return model_trained

	def birch_model(self, df, threshold=0.01, n_clusters=4):
		model_trained = Birch(threshold=threshold, n_clusters=n_clusters)
		model_trained.fit(df)
		return model_trained

	def db_model(self, df):
		model_trained = DBSCAN()
		model_trained.fit(df)
		for i in range(0, df.shape[0]):
			if model_trained.labels_[i] == 0:
				c1 = plt.scatter(df[i, 0], df[i, 1], c='r', marker='+')
			elif model_trained.labels_[i] == 1:
				c2 = plt.scatter(df[i, 0], df[i, 1], c='g', marker='o')
			elif model_trained.labels_[i] == -1:
				c3 = plt.scatter(df[i, 0], df[i, 1], c='b', marker='*')
		plt.legend([c1, c2, c3], ['Cluster 1', 'Cluster 2', 'Noise'])
		plt.title('DBSCAN finds 2 clusters and Noise')
		plt.show()
		return model_trained

	def kp_model(self, df, n_clusters=4, init='Cao'):
		categorical_columns = df.select_dtypes(include='object').columns
		categorical_list = []
		for col_name in categorical_list:    
			index_no = df.columns.get_loc(col_name)
			categorical_list.append(index_no)
		model_trained = KPrototypes(n_clusters=n_clusters, init=init)
		model_trained.fit(df, categorical=categorical_list)
		return model_trained


########################### Time Series Models ###########################
class time_series_models:
	def __init__(self):
		pass

	def arima_stationarity_test(self, df,column):
		pre_result = adfuller(df[column].dropna())
		k = pre_result[2]
		if pre_result[1] >= 0.05:
			significant_list = {}
			for i in range(1,k): 
				df['Seasonal First Difference'] = df[column] - df[column].shift(i)
				result=adfuller(df['Seasonal First Difference'].dropna())        
				if result[1] < 0.05:
					significant_list[i] = result[1]
			if significant_list != {}:
				best_key = min(significant_list, key=significant_list.get)
				print(significant_list)
				df['Seasonal First Difference'] = df[column] - df[column].shift(best_key)
				results=adfuller(df['Seasonal First Difference'].dropna()) 
				labels = ['ADF Test Statistic','p-value','#Lags Used','Number of Observations']
				for value,label in zip(results,labels):
					print(label+' : '+str(value))
				print("Best shift happened at : {}".format(best_key))
				print()
				df['Seasonal First Difference'].plot(x=df['Month_x'], y=df[column])
				print()
			else:
				print()
				print("Seasonality couldn't be removed with the given parameters...")
				print()
		else:
			print("There is no trend or seasonality found in this dataset...")
			print()

