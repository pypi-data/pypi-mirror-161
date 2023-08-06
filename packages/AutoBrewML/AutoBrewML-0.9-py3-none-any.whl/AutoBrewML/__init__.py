
# # %%
import warnings
warnings.filterwarnings('ignore')

# %%
# # DBTITLE 1,Pandas Version check:
def PandasVersion():
    import pandas as pd
    print("The in context Pandas version is:")
    print(pd.__version__)
#PandasVersion()




# %%
# # DBTITLE 1,Acquisition & DataTypeConversion:
def Acquisition_DataTypeConversion(filepath,col_dtype_dict):
    import pandas as pd
    import numpy as np
    df = pd.read_csv(filepath)
    print("Original datatypes:")
    print(df.dtypes)
    input_dataframe = df.astype(col_dtype_dict)
    print("Converted datatypes:")              
    print(input_dataframe.dtypes)
    input_dataframe['Index'] = np.arange(len(input_dataframe)) 
    print("Input dataframe:")
    print(input_dataframe.head())
    return(input_dataframe)

# #Function Call:
# filepath=r"C:\Users\srde\Downloads\Titanic.csv"
# col_dtype_dict={
#                     'PassengerId':'int'
#                     ,'Survived':'int'
#                     ,'Pclass':'int'
#                     ,'Name':'string'
#                     ,'Sex':'string'
#                     ,'Age':'float'
#                     ,'SibSp':'int'
#                     ,'Parch':'int'
#                     ,'Ticket':'string'
#                     ,'Fare':'float'
#                     ,'Cabin':'string'
#                     ,'Embarked':'string'
#                 }
# input_dataframe=Acquisition_DataTypeConversion(filepath,col_dtype_dict)




# %%
# DBTITLE 1,Data Profiler
#pip install pandas-profiling
def Data_Profiling_viaPandasProfiling(input_dataframe):
  #import time 
  #ts = int(time.time())
  #ts= "%s" % str(ts)
  #filepath="adl://<Your ADLS Name>.azuredatalakestore.net/DEV/EDAProfile_" + ts +".html"
  import pandas_profiling as pp
  profile = pp.ProfileReport(input_dataframe) 
  p = profile.to_html() 
  #profile.to_file('/dbfs/FileStore/EDAProfile.html')
  #dbutils.fs.cp ("/FileStore/EDAProfile.html", filepath, True)
  #print("EDA Report can be downloaded from path: ",filepath)
  return(p)
  #displayHTML(p)
  #return(df.describe())

# #Function Call
# # p=Data_Profiling_viaPandasProfiling(input_dataframe)
# displayHTML(p)





# %%
# Data Cleanser
# # DBTITLE 1,Data Cleanser -Fix Categorical Columns
def fixCategoricalColumns(input_dataframe):
  from sklearn.preprocessing import LabelEncoder 
  from sklearn.preprocessing import MinMaxScaler
  le = LabelEncoder()
  # Replace structural errors on categorical columns - Inconsistent capitalization and Label Encode Categorical Columns + MinMax Scaling
  print("\n","Categorical columns cleansing:")
  print("Fixing inconsistent capitalization and removing any white spaces.")
  for column in input_dataframe.columns.values:
    if str(input_dataframe[column].values.dtype) == 'object':
      for ind in input_dataframe.index:
        input_dataframe[column] = input_dataframe[column].astype(str).str.title()
        input_dataframe[column] = input_dataframe[column].str.replace(" ","")
    if str(input_dataframe[column].values.dtype) == 'object':
      for col in input_dataframe.columns:
        input_dataframe[col]=le.fit_transform(input_dataframe[col])
  print("Label Encoding on categorical columns.")
  
  
  print("MinMax scaling for Normalisation.")
  #scaler = MinMaxScaler()
  #print(scaler.fit(input_dataframe))
  #print(scaler.data_max_)
  #print(scaler.transform(input_dataframe))
  #Normalisation of data as K-Means clustering uses euclidean distance
  column_list=list(input_dataframe.columns)
  column_list_actual=column_list
  column_list.remove('Index')
  from sklearn.preprocessing import MinMaxScaler
  mms = MinMaxScaler()
  input_dataframe[column_list] = pd.DataFrame(mms.fit_transform(input_dataframe[column_list]),columns = column_list_actual )
  #print(scaler.transform([[2, 2]]))
  return input_dataframe                         



# DBTITLE 1,Data Cleanser -Imputation
def impute(input_dataframe):
  # Replace NaNs with the median or mode of the column depending on the column type
  #print("Standard deviation of dataframe before imputation is:\n",input_dataframe.std(axis = 0, skipna = True))
  NumCol=[]
  CatCol=[]
  for column in input_dataframe.columns:
    if(input_dataframe[column].dtype) not in ["object"]:
      NumCol.append(column)
      input_dataframe[column].fillna(input_dataframe[column].median(), inplace=True)
      
    else:
      CatCol.append(column)
      most_frequent = input_dataframe[column].mode() 
      if len(most_frequent) > 0:
        input_dataframe[column].fillna(input_dataframe[column].mode()[0], inplace=True)
        
      else:
        input_dataframe[column].fillna(method='bfill', inplace=True)
       
        input_dataframe[column].fillna(method='ffill', inplace=True)
        
  print("\n","Imputation of Columns:")
  print("Imputation of Numerical Column done using Median:")
  print(*NumCol, sep = ", ") 
  print("Imputation of Categorical Column done using Mode/bfill/ffill:")
  print(*CatCol, sep = ", ") 
  

  return input_dataframe

# COMMAND ----------

# DBTITLE 1,Data Cleanser -Impute/Drop NULL Rows
def cleanMissingValues(input_dataframe):
  import numpy as np
  
  print("\n","Impute/Drop NULL Rows:")
  print("Total rows in the Input dataframe:",len(input_dataframe.index)) #Total count of dataset
  totalCells = np.product(input_dataframe.shape)
  # Calculate total number of cells in dataframe
  print("Total number of cells in the input dataframe:",totalCells)
  input_dataframe = input_dataframe.replace(r'^\s+$', np.nan, regex=True) #replace white spaces with NaN except spaces in middle
  # Count number of missing values per column
  missingCount = input_dataframe.isnull().sum()
  print("Displaying number of missing records per column:")
  print(missingCount)
  # Calculate total number of missing values
  totalMissing = missingCount.sum()
  print("Total no. of missing values=",totalMissing)
  # Calculate percentage of missing values
  print("The dataset contains", round(((totalMissing/totalCells) * 100), 2), "%", "missing values.")
  cleaned_inputdf= input_dataframe   
  for col in input_dataframe.columns:
    if(missingCount[col]>0):
      print("Percent missing data in",col,"column =", (round(((missingCount[col] / input_dataframe.shape[0]) * 100), 2)))
      if((round(((missingCount[col] / input_dataframe.shape[0]) * 100), 2))>50):
        print("Dropping this column as it contains missing values in more than half of the dataset...")
        input_dataframe_CleanCols=input_dataframe.drop(col,axis=1,inplace=True)
        print("Total Columns in original dataset: %d \n" % input_dataframe.shape[1])
        print("Total Columns now with na's dropped: %d" % input_dataframe_CleanCols.shape[1])
        cleaned_inputdf=input_dataframe_CleanCols
        
      else:
        print("As percent of missing values is less than half, imputing this column based on the data type.")
        input_dataframe_imputed=impute(input_dataframe,'Auto Tune Model','Data Cleansing',col)
        cleaned_inputdf=input_dataframe_imputed
        
  return cleaned_inputdf

# COMMAND ----------

# DBTITLE 1,Data Cleanser Master
def autodatacleaner(input_dataframe):
    import pandas as pd
    inputdf_1=impute(input_dataframe)
    inputdf_2=cleanMissingValues(inputdf_1)
    inputdf_3=fixCategoricalColumns(inputdf_2)
    return inputdf_3












# %%
# DBTITLE 1,Sampling- Random Sampling:
def RandomSampling(input_dataframe):
  df_fin=input_dataframe
  import pandas as pd
  import numpy as np
  import math
  
  print("Random Sampling starting")

  #Imputation to avoid mixup in chi2 test with categorical values frequencies
  input_dataframe=impute(input_dataframe)

  #Getting ideal sample size by Solven's Formula assuming Confidence Level=95% i.e n = N / (1 + Ne²)
  total_records=len(df_fin.index)
  sample_size= round(total_records / (1 + total_records* (1-0.95)*(1-0.95)))

  #For chi2 test the two conditions are-
  #     1.The distinct unique values in the original v/s sample must be same. So force fill missing values with frequency=0 (absent in sample w.r.t. original)
  #     2.The sum of frequencies in both original & sample must be same. So scale up the sample frequency to match the sum of frequencies of original exactly- sample_count=sample_count*input_dataframe_count_sum/sample_count_sum. For the sum of frequencies to match exactly the scale up factor should be a whole number or this ratio of input_dataframe_count_sum/sample_count_sum should be a whole number. i.e. input_dataframe_count_sum should be a multiple of sample_count_sum (or sample_size)  
  sample_size=int(total_records/math.floor(total_records/sample_size))

  subsample=df_fin.sample(n=sample_size)
  
  #Hypothesis test to see if sample is accepted
  from scipy import stats
  pvalues = list()
  for col in subsample.columns:
    if (subsample[col].dtype) in ["int32","int64","float","float64"]: 
      # Numeric variable. Using Kolmogorov-Smirnov test
      pvalues.append(stats.ks_2samp(subsample[col],input_dataframe[col]))
        
    else:
      # Categorical variable. Using Pearson's Chi-square test
      from scipy import stats
      import pandas as pd
      #For chi2 test the two conditions are-
      # #     1.The distinct unique values in the original v/s sample must be same. So force fill missing values with frequency=0 (absent in sample w.r.t. original)
      sample_count=pd.DataFrame(subsample[col].value_counts())
      input_dataframe_count=pd.DataFrame(input_dataframe[col].value_counts())
      absent=input_dataframe_count-sample_count
      absent2=absent.loc[absent[col].isnull()]
      absent2[col]=0
      sample_count_final=pd.concat([absent2,sample_count]) 

      #     2.The sum of frequencies in both original & sample must be same. So scale up the sample frequency to match the sum of frequencies of original exactly- sample_count=sample_count*input_dataframe_count_sum/sample_count_sum. For the sum of frequencies to match exactly the scale up factor should be a whole number or this ratio of input_dataframe_count_sum/sample_count_sum should be a whole number. i.e. input_dataframe_count_sum should be a multiple of sample_count_sum (or sample_size)  
      sample_count_final_sum=sample_count_final.sum()
      input_dataframe_count_sum=input_dataframe_count.sum()
      sample_count_final=sample_count_final*input_dataframe_count_sum/sample_count_final_sum
      sample_count_final = sample_count_final.apply(np.ceil).astype(int)
      pvalues.append(stats.chisquare(sample_count_final.astype(int), input_dataframe_count.astype(int)))
  
  count=0
  length =  len(subsample.columns)
  pvalues_average=0
  for i in range(length): 
    if pvalues[i].pvalue >=0.05:
      count=count+1
      #print(pvalues[i].pvalue) 
      pvalues_average=pvalues_average+pvalues[i].pvalue 
  pvalues_average=pvalues_average/length
  #pvalues_average=pvalues_average[0]
  #atleast threashold% of columns pass the hypothesis then accept the sample else reject 
  threshold=0.5
  Len_Actualdataset=len(input_dataframe.index)
  Len_Sampleddataset=len(subsample.index)
  Sampling_Error=1/math.sqrt(Len_Sampleddataset) * 100
  print ("Volume of actual dataset = ",Len_Actualdataset)
  print ("Volume of Sampled dataset =",Len_Sampleddataset) 
  print('Sampling Error for actual_size={} sample_size={} is {:.3f}% '.format(Len_Actualdataset,Len_Sampleddataset,Sampling_Error))
    
  if count> threshold*len(input_dataframe.columns):
    print ("Random Sample accepted-via KS and Chi_square Null hypothesis")
    
    Len_Actualdataset= "%s" % str(Len_Actualdataset)
    Len_Sampleddataset= "%s" % str(Len_Sampleddataset)
    Sampling_Error= "%s" %  str(Sampling_Error)  
    
    
  else:
    print ("Random Sample rejected")
    
  #print(pvalues) 
  #P is the probability that there is no significant difference between sample and actual (Null hypothesis)
  print('Average p-value between sample and actual(the bigger the p-value the closer the two datasets are.)= ',pvalues_average)
  
  pvalues_average="%s" % str(pvalues_average)

    
  return(sample_size,pvalues_average,subsample)

# %%
# DBTITLE 1,Sampling- Systematic Sampling
def SystematicSampling(input_dataframe):
  df_fin=input_dataframe
  import pandas as pd
  import numpy as np
  import math
  
  #Imputation to avoid mixup in chi2 test with categorical values frequencies
  input_dataframe=impute(input_dataframe)
  
  #Getting ideal sample size by Solven's Formula assuming Confidence Level=95% i.e n = N / (1 + Ne²)
  total_records=len(df_fin.index)
  sample_size= round(total_records / (1 + total_records* (1-0.95)*(1-0.95)))

  #For chi2 test the two conditions are-
  #     1.The distinct unique values in the original v/s sample must be same. So force fill missing values with frequency=0 (absent in sample w.r.t. original)
  #     2.The sum of frequencies in both original & sample must be same. So scale up the sample frequency to match the sum of frequencies of original exactly- sample_count=sample_count*input_dataframe_count_sum/sample_count_sum. For the sum of frequencies to match exactly the scale up factor should be a whole number or this ratio of input_dataframe_count_sum/sample_count_sum should be a whole number. i.e. input_dataframe_count_sum should be a multiple of sample_count_sum (or sample_size)  
  sample_size=int(total_records/math.floor(total_records/sample_size))
 
  subsample = df_fin.loc[df_fin['Index'] % (round(total_records/sample_size)) ==0]
  
  #Hypothesis test to see if sample is accepted
  from scipy import stats
  pvalues = list()
  for col in subsample.columns:
    if (subsample[col].dtype) in ["int32","int64","float","float64"]: 
      # Numeric variable. Using Kolmogorov-Smirnov test
      pvalues.append(stats.ks_2samp(subsample[col],input_dataframe[col]))
        
    else:
      # Categorical variable. Using Pearson's Chi-square test
      from scipy import stats
      import pandas as pd
      #For chi2 test the two conditions are-
      # #     1.The distinct unique values in the original v/s sample must be same. So force fill missing values with frequency=0 (absent in sample w.r.t. original)
      sample_count=pd.DataFrame(subsample[col].value_counts())
      input_dataframe_count=pd.DataFrame(input_dataframe[col].value_counts())
      absent=input_dataframe_count-sample_count
      absent2=absent.loc[absent[col].isnull()]
      absent2[col]=0
      sample_count_final=pd.concat([absent2,sample_count]) 

      #     2.The sum of frequencies in both original & sample must be same. So scale up the sample frequency to match the sum of frequencies of original exactly- sample_count=sample_count*input_dataframe_count_sum/sample_count_sum. For the sum of frequencies to match exactly the scale up factor should be a whole number or this ratio of input_dataframe_count_sum/sample_count_sum should be a whole number. i.e. input_dataframe_count_sum should be a multiple of sample_count_sum (or sample_size)  
      sample_count_final_sum=sample_count_final.sum()
      input_dataframe_count_sum=input_dataframe_count.sum()
      sample_count_final=sample_count_final*input_dataframe_count_sum/sample_count_final_sum
      sample_count_final = sample_count_final.apply(np.ceil).astype(int)
      pvalues.append(stats.chisquare(sample_count_final.astype(int), input_dataframe_count.astype(int)))
  
  count=0
  length =  len(subsample.columns)
  pvalues_average=0
  for i in range(length): 
    if pvalues[i].pvalue >=0.05:
      count=count+1
      #print(pvalues[i].pvalue) 
      pvalues_average=pvalues_average+pvalues[i].pvalue 
  pvalues_average=pvalues_average/length
  #pvalues_average=pvalues_average[0]
  #atleast threashold% of columns pass the hypothesis then accept the sample else reject 
  threshold=0.5
  Len_Actualdataset=len(input_dataframe.index)
  Len_Sampleddataset=len(subsample.index)
  Sampling_Error=1/math.sqrt(Len_Sampleddataset) * 100
  print ("Volume of actual dataset = ",Len_Actualdataset)
  print ("Volume of Sampled dataset =",Len_Sampleddataset) 
  print('Sampling Error for actual_size={} sample_size={} is {:.3f}% '.format(Len_Actualdataset,Len_Sampleddataset,Sampling_Error))
    
  if count> threshold*len(input_dataframe.columns):
    print ("Random Sample accepted-via KS and Chi_square Null hypothesis")
    
    Len_Actualdataset= "%s" % str(Len_Actualdataset)
    Len_Sampleddataset= "%s" % str(Len_Sampleddataset)
    Sampling_Error= "%s" %  str(Sampling_Error)  
    
    
  else:
    print ("Random Sample rejected")
    
  #print(pvalues) 
  #P is the probability that there is no significant difference between sample and actual (Null hypothesis)
  print('Average p-value between sample and actual(the bigger the p-value the closer the two datasets are.)= ',pvalues_average)
  
  pvalues_average="%s" % str(pvalues_average)

    
  return(sample_size,pvalues_average,subsample)
 
    

# %%
# DBTITLE 1,Sampling- Stratified Sampling
def StratifiedSampling(input_dataframe_orig):
  
  #Imputation to avoid mixup in chi2 test with categorical values frequencies
  input_dataframe_orig=impute(input_dataframe_orig)
  #Deep=True (the default), a new object is produced with a copy of the calling object’s data and indices. Changes to the copy’s data or indices will not reflect the original object.
  df_fin=input_dataframe_orig.copy(deep=True)
  input_dataframe = input_dataframe_orig.copy(deep=True)
  
  import pandas as pd
  from collections import Counter

  import pandas as pd
  import numpy as np
  import math
  
  
  #Label encoder accepts only non nulls
  for column in df_fin.columns.values:
        try:
            df_fin[column].fillna(df_fin[column].mean(), inplace=True)
        except TypeError:
            df_fin[column].fillna(df_fin[column].mode()[0], inplace=True)
            
  #K means accept only numeric columns hence label encode
  from sklearn.preprocessing import LabelEncoder
  le = LabelEncoder()
  for col in df_fin.columns:
    if (df_fin[col].dtype) not in ["int32","int64","float","float64"]:
      df_fin[col]=le.fit_transform(df_fin[col])
  
  #Normalisation of data as K-Means clustering uses euclidean distance
  column_list=list(df_fin.columns)
  column_list_actual=column_list
  column_list.remove('Index')
  from sklearn.preprocessing import MinMaxScaler
  mms = MinMaxScaler()
  df_fin[column_list] = pd.DataFrame(mms.fit_transform(df_fin[column_list]),columns = column_list_actual )
    
     
  #Getting best k for K-Means using Silhoute max score k    
  from sklearn.cluster import KMeans
  Dic = {}
  for k in range(2,6):
    k_means = KMeans(n_clusters=k)
    model = k_means.fit(df_fin)
    y_hat = k_means.predict(df_fin)
    from sklearn import metrics
    labels = k_means.labels_
    Dic.update({k:metrics.silhouette_score(df_fin, labels, metric = 'euclidean')})
  Keymax = max(Dic, key=Dic.get) 
  #print(Keymax)
  
  #K-Means clustering using optimal k
  kmeans = KMeans(n_clusters=Keymax)
  y = kmeans.fit_predict(df_fin)
  df_fin['Cluster'] = y
  #print(df_fin.head())
  
  # summarize distribution actual
  print('Data Summary before sampling: ')
  y=df_fin['Cluster']
  counter = Counter(y)
  for k,v in counter.items():
      per = v / len(y) * 100
      print('Class=%d, n=%d (%.3f%%)' % (k, v, per))
    
  #Stratifying to get sample
  df_sample = pd.DataFrame()
  count_records_per_cluster= list()
  sample_records_per_cluster=list()
  total_records=len(df_fin.index)
  
  #Getting ideal sample size by Solven's Formula assuming Confidence Level=95% i.e n = N / (1 + Ne²)
  total_records=len(df_fin.index)
  sample_size= round(total_records / (1 + total_records* (1-0.95)*(1-0.95)))

  #For chi2 test the two conditions are-
  #     1.The distinct unique values in the original v/s sample must be same. So force fill missing values with frequency=0 (absent in sample w.r.t. original)
  #     2.The sum of frequencies in both original & sample must be same. So scale up the sample frequency to match the sum of frequencies of original exactly- sample_count=sample_count*input_dataframe_count_sum/sample_count_sum. For the sum of frequencies to match exactly the scale up factor should be a whole number or this ratio of input_dataframe_count_sum/sample_count_sum should be a whole number. i.e. input_dataframe_count_sum should be a multiple of sample_count_sum (or sample_size)  
  sample_size=int(total_records/math.floor(total_records/sample_size))


  for i in range(Keymax):
    df_fin_test=df_fin
    count_records_per_cluster.append(df_fin_test['Cluster'].value_counts()[i])
    sample_records_per_cluster.append(count_records_per_cluster[i]/total_records * sample_size)
    df_sample_per_cluster=df_fin_test[df_fin_test.Cluster==i]
    df_sample_per_cluster=df_sample_per_cluster.sample(int(sample_records_per_cluster[i]),replace=True)   
    df_sample=df_sample.append(df_sample_per_cluster, ignore_index = True)
  #df_sample.head()
  
  # summarize distribution sampled
  print('Data Summary after sampling: ')
  y=df_sample['Cluster']
  counter = Counter(y)
  for k,v in counter.items():
      per = v / len(y) * 100
      print('Class=%d, n=%d (%.3f%%)' % (k, v, per))
    
  #Remove Columns which are not present in input_dataframe
  df_sample.drop(['Cluster'], axis=1, inplace=True)
  subsample=df_sample

  

  #Hypothesis test to see if sample is accepted
  from scipy import stats
  pvalues = list()
  for col in subsample.columns:
    if (subsample[col].dtype) in ["int32","int64","float","float64"]: 
      # Numeric variable. Using Kolmogorov-Smirnov test
      pvalues.append(stats.ks_2samp(subsample[col],df_fin[col]))
        
    else:
      # Categorical variable. Using Pearson's Chi-square test
      from scipy import stats
      import pandas as pd
      #For chi2 test the two conditions are-
      # #     1.The distinct unique values in the original v/s sample must be same. So force fill missing values with frequency=0 (absent in sample w.r.t. original)
      sample_count=pd.DataFrame(subsample[col].value_counts())
      input_dataframe_count=pd.DataFrame(input_dataframe[col].value_counts())
      absent=input_dataframe_count-sample_count
      absent2=absent.loc[absent[col].isnull()]
      absent2[col]=0
      sample_count_final=pd.concat([absent2,sample_count]) 

      #     2.The sum of frequencies in both original & sample must be same. So scale up the sample frequency to match the sum of frequencies of original exactly- sample_count=sample_count*input_dataframe_count_sum/sample_count_sum. For the sum of frequencies to match exactly the scale up factor should be a whole number or this ratio of input_dataframe_count_sum/sample_count_sum should be a whole number. i.e. input_dataframe_count_sum should be a multiple of sample_count_sum (or sample_size)  
      sample_count_final_sum=sample_count_final.sum()
      input_dataframe_count_sum=input_dataframe_count.sum()
      sample_count_final=sample_count_final*input_dataframe_count_sum/sample_count_final_sum
      sample_count_final = sample_count_final.apply(np.ceil).astype(int)
      pvalues.append(stats.chisquare(sample_count_final.astype(int), input_dataframe_count.astype(int)))
  
  count=0
  length =  len(subsample.columns)
  pvalues_average=0
  for i in range(length): 
    if pvalues[i].pvalue >=0.05:
      count=count+1
      #print(pvalues[i].pvalue) 
      pvalues_average=pvalues_average+pvalues[i].pvalue 
  pvalues_average=pvalues_average/length
  #pvalues_average=pvalues_average[0]
  #atleast threashold% of columns pass the hypothesis then accept the sample else reject 
  threshold=0.5
  Len_Actualdataset=len(input_dataframe.index)
  Len_Sampleddataset=len(subsample.index)
  Sampling_Error=1/math.sqrt(Len_Sampleddataset) * 100
  print ("Volume of actual dataset = ",Len_Actualdataset)
  print ("Volume of Sampled dataset =",Len_Sampleddataset) 
  print('Sampling Error for actual_size={} sample_size={} is {:.3f}% '.format(Len_Actualdataset,Len_Sampleddataset,Sampling_Error))
    
  if count> threshold*len(input_dataframe.columns):
    print ("Random Sample accepted-via KS and Chi_square Null hypothesis")
    
    Len_Actualdataset= "%s" % str(Len_Actualdataset)
    Len_Sampleddataset= "%s" % str(Len_Sampleddataset)
    Sampling_Error= "%s" %  str(Sampling_Error)  
    
    
  else:
    print ("Random Sample rejected")
    
  #print(pvalues) 
  #P is the probability that there is no significant difference between sample and actual (Null hypothesis)
  print('Average p-value between sample and actual(the bigger the p-value the closer the two datasets are.)= ',pvalues_average)
  
  pvalues_average="%s" % str(pvalues_average)


  #Getting back Sample in original data form
  uniqueIndex = list(df_sample['Index'].unique())
  subsample_orig= input_dataframe_orig[input_dataframe_orig.Index.isin(uniqueIndex)]
    
  return(sample_size,pvalues_average,subsample_orig)


# %%
# DBTITLE 1,Sampling- Cluster Sampling (Oversampling SMOTE)
def ClusterSampling_Oversampling(input_dataframe,cluster_col):
  
  #Imputation to avoid mixup in chi2 test with categorical values frequencies
  input_dataframe=impute(input_dataframe)
  
  df_fin=input_dataframe
  df_fin['Y']=df_fin[cluster_col]
  print('Length of actual input data=', len(input_dataframe.index))
  
  from sklearn.preprocessing import LabelEncoder
  from collections import Counter
  import pandas as pd
  import numpy as np
  import math
  import imblearn
  
  print("Cluster sampling with SMOTE starting")
  
  
  # summarize distribution
  print('Data Summary before sampling')
  #y=df_fin['Y']

  #Convert text data to numeric before applying SMOTE
  from sklearn.preprocessing import LabelEncoder
  le = LabelEncoder()
  for col in df_fin.columns:
    if (df_fin[col].dtype) not in ["int32","int64","float","float64"]:
        df_fin[col]=le.fit_transform(df_fin[col])
  
  
  y=df_fin['Y']
  counter = Counter(y)
  Classes = []
  for k,v in counter.items():
    Classes.append(k)
    per = v / len(y) * 100
    print('Class=%d, n=%d (%.3f%%)' % (k, v, per))
  ### plot the distribution
  ##pyplot.bar(counter.keys(), counter.values())
  ##pyplot.show()
  #print("Classes:",Classes)
  
  #SMOTE 
  print('Data Summary after SMOTE')
  from imblearn.over_sampling import SMOTE
  # split into input and output elements
  y = df_fin.pop('Y')
  x = df_fin
  # transform the dataset
  oversample = SMOTE()
  x, y = oversample.fit_resample(x, y)
  # summarize distribution
  counter = Counter(y)
  for k,v in counter.items():
      per = v / len(y) * 100
      print('Class=%d, n=%d (%.3f%%)' % (k, v, per))
  
  df_fin=x
  df_fin['Y']=y
  df_fin.head()                                                           
  #df_fin.count()
  #sample_size,pvalues_average,subsample=StratifiedSampling(df_fin,'/dbfs/FileStore/SMOTE.csv',task_type,input_appname)
  subsample=df_fin
  
  #Hypothesis test to see if sample is accepted
  subsample.drop(['Y'], axis=1, inplace=True)

  from scipy import stats
  pvalues = list()
  for col in subsample.columns:
    if (subsample[col].dtype) in ["int32","int64","float","float64"]: 
      # Numeric variable. Using Kolmogorov-Smirnov test
      pvalues.append(stats.ks_2samp(subsample[col],input_dataframe[col]))
        
    else:
      # Categorical variable. Using Pearson's Chi-square test
      from scipy import stats
      import pandas as pd
      #For chi2 test the two conditions are-
      # #     1.The distinct unique values in the original v/s sample must be same. So force fill missing values with frequency=0 (absent in sample w.r.t. original)
      sample_count=pd.DataFrame(subsample[col].value_counts())
      input_dataframe_count=pd.DataFrame(input_dataframe[col].value_counts())
      absent=input_dataframe_count-sample_count
      absent2=absent.loc[absent[col].isnull()]
      absent2[col]=0
      sample_count_final=pd.concat([absent2,sample_count]) 

      #     2.The sum of frequencies in both original & sample must be same. So scale up the sample frequency to match the sum of frequencies of original exactly- sample_count=sample_count*input_dataframe_count_sum/sample_count_sum. For the sum of frequencies to match exactly the scale up factor should be a whole number or this ratio of input_dataframe_count_sum/sample_count_sum should be a whole number. i.e. input_dataframe_count_sum should be a multiple of sample_count_sum (or sample_size)  
      sample_count_final_sum=sample_count_final.sum()
      input_dataframe_count_sum=input_dataframe_count.sum()
      sample_count_final=sample_count_final*input_dataframe_count_sum/sample_count_final_sum
      sample_count_final = sample_count_final.apply(np.ceil).astype(int)
      pvalues.append(stats.chisquare(sample_count_final.astype(int), input_dataframe_count.astype(int)))
  
  count=0
  length =  len(subsample.columns)
  pvalues_average=0
  for i in range(length): 
    if pvalues[i].pvalue >=0.05:
      count=count+1
      #print(pvalues[i].pvalue) 
      pvalues_average=pvalues_average+pvalues[i].pvalue 
  pvalues_average=pvalues_average/length
  #pvalues_average=pvalues_average[0]
  #atleast threashold% of columns pass the hypothesis then accept the sample else reject 
  threshold=0.5
  Len_Actualdataset=len(input_dataframe.index)
  Len_Sampleddataset=len(subsample.index)
  Sampling_Error=1/math.sqrt(Len_Sampleddataset) * 100
  print ("Volume of actual dataset = ",Len_Actualdataset)
  print ("Volume of Sampled dataset =",Len_Sampleddataset) 
  print('Sampling Error for actual_size={} sample_size={} is {:.3f}% '.format(Len_Actualdataset,Len_Sampleddataset,Sampling_Error))
    
  if count> threshold*len(input_dataframe.columns):
    print ("Cluster Sample accepted-via KS and Chi_square Null hypothesis")
    
    Len_Actualdataset= "%s" % str(Len_Actualdataset)
    Len_Sampleddataset= "%s" % str(Len_Sampleddataset)
    Sampling_Error= "%s" %  str(Sampling_Error)  
    
    
  else:
    print ("Cluster Sample rejected")
    
  #print(pvalues) 
  #P is the probability that there is no significant difference between sample and actual (Null hypothesis)
  print('Average p-value between sample and actual(the bigger the p-value the closer the two datasets are.)= ',pvalues_average)
  
  pvalues_average="%s" % str(pvalues_average)

    
  return(Len_Sampleddataset,pvalues_average,subsample)



# %%
# DBTITLE 1,Best Sampling Estimator
def Sampling(input_dataframe,cluster_col):
  import pandas as pd
  subsample_StratifiedSampling = pd.DataFrame()
  subsample_RandomSampling = pd.DataFrame()
  subsample_SystematicSampling = pd.DataFrame()
  subsample_ClusterSampling_Oversampling = pd.DataFrame()

  input_dataframe_StratifiedSampling = input_dataframe
  input_dataframe_RandomSampling = input_dataframe
  input_dataframe_SystematicSampling = input_dataframe
  input_dataframe_ClusterSampling_Oversampling = input_dataframe
  
  print("\n","Stratified Sampling")
  sample_size_StratifiedSampling,pvalue_StratifiedSampling,subsample_StratifiedSampling= StratifiedSampling(input_dataframe_StratifiedSampling)
  
  
  print("\n","Random Sampling")
  sample_size_RandomSampling,pvalue_RandomSampling,subsample_RandomSampling= RandomSampling(input_dataframe_RandomSampling)
  
  
  print("\n","Systematic Sampling")
  sample_size_SystematicSampling,pvalue_SystematicSampling,subsample_SystematicSampling= SystematicSampling(input_dataframe_SystematicSampling)
  
  if cluster_col=="NULL":
    print("\n","No Cluster Sampling")
  else:
    print("\n","Cluster Sampling")
    sample_size_ClusterSampling_Oversampling,pvalue_ClusterSampling_Oversampling,subsample_ClusterSampling_Oversampling= ClusterSampling_Oversampling(input_dataframe_ClusterSampling_Oversampling,cluster_col)
  
  Dic = {}
  Dic.update({"StratifiedSampling":pvalue_StratifiedSampling})
  Dic.update({"RandomSampling":pvalue_RandomSampling})
  Dic.update({"SystematicSampling":pvalue_SystematicSampling})
  if cluster_col!="NULL":
    Dic.update({"ClusterSampling":pvalue_ClusterSampling_Oversampling})
  Keymax = max(Dic, key=Dic.get) 
  if Keymax=="StratifiedSampling":
    subsample_final=subsample_StratifiedSampling
  elif Keymax=="RandomSampling":
    subsample_final=subsample_RandomSampling
  elif Keymax=="SystematicSampling":
    subsample_final=subsample_SystematicSampling
  elif Keymax=="ClusterSampling":
    subsample_final=subsample_ClusterSampling_Oversampling
  print("\n","Best Suggested Sample is - ",Keymax)
  
  Keymax="%s" % Keymax

  
  return(subsample_final,subsample_StratifiedSampling,subsample_RandomSampling,subsample_SystematicSampling,subsample_ClusterSampling_Oversampling)






# ############################################# CALLING FUNCTIONS #############################################################################################################################################################################################################
# # %%
# # Function:Acquisition_DataTypeConversion
# filepath=r"C:\Users\srde\Downloads\Titanic.csv"
# col_dtype_dict={
#                     'PassengerId':'int'
#                     ,'Survived':'int'
#                     ,'Pclass':'int'
#                     ,'Name':'object'
#                     ,'Sex':'object'
#                     ,'Age':'float'
#                     ,'SibSp':'int'
#                     ,'Parch':'int'
#                     ,'Ticket':'object'
#                     ,'Fare':'float'
#                     ,'Cabin':'object'
#                     ,'Embarked':'object'
#                 }
# input_dataframe=Acquisition_DataTypeConversion(filepath,col_dtype_dict)

# # %%
# input_dataframe

# # %%
# # # Function:Exploratory Data Analysis
# p=Data_Profiling_viaPandasProfiling(input_dataframe)
# print(p)
# displayHTML(p)


# # %%
# # # Function:Data Cleanser
# Cleansed_data=autodatacleaner(input_dataframe)
# Cleansed_data.head()





#  %%
#  Function: Sampling
# print(df.head())
# sample_size,pvalues_average,subsample=RandomSampling(input_dataframe)
# sample_size,pvalues_average,subsample=SystematicSampling(input_dataframe)
# sample_size,pvalues_average,subsample=StratifiedSampling(input_dataframe)
# sample_size,pvalues_average,subsample=ClusterSampling_Oversampling(input_dataframe,'Sex')

# subsample_final,subsample_StratifiedSampling,subsample_RandomSampling,subsample_SystematicSampling,subsample_ClusterSampling_Oversampling=Sampling(input_dataframe,'Sex')


