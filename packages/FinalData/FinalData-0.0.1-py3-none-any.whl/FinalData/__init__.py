# defining first function as  

def data_doctor(a,b,c,d,l1=[],l2=[]):
    
    
    '''''  This function is for filling the NAN values in the columns, dropping some rows if the NAN values in % is less
    than minimum specified %, dropping some of the columns if NAN values % in such columns are greater than the maximum 
    specified % limit, getting dummy variables of all categorical variables and then dropping those categorical variables,
    converting categorical target column to numeric type and dropping some unwanted columns also.
    
    keywords:
    
         a : is Data file in csv format 
    
         b: is minimum percentage for dropping the rows having NAN values 
        
        c : is the maximum percentage for dropping rows and columns respectively for NAN values
        
        l1 : is the list of columns which are need to be removed and are of no use in predicting the result,
                if there are no such columns then give empty list
        
        l2 : is the list of columns which should be numeric type but they are originally given object type,
               if there are no such columns then give the empty list 
        
        d : is the target output column name in string format 
    
    
    NOTE: All these three functions are for regression and binary classification problems in which the data does'nt contain
        any column for duration, time, date etc. 
        ex-- 21/9/2021, 2h31m, 2:30 etc.''''' 
            
    #importing required module 
    import pandas as pd
    #preparing the dataframe 
    df=pd.read_csv(a)
    
    #for dropping the columns which are of no use and should be identified before using this function  
    df.drop(l1,axis=1,inplace=True)
    
    #for converting column from object to numeric type 
    for c in l2:
        df[c]=pd.to_numeric(df[c],errors='coerce')
        
    #By default this work for numeric datatype columns and not for other columns and will drop columns having NAN values % < b
    if max((df.isnull().sum()/len(df)).values*100)<=b:
        df.dropna(how='any',inplace=True)
    
    # If NAN values % is >b & <c then we will replace all NAN value by '0' 
    elif b<max((df.isnull().sum()/len(df)).values*100)<=c:
        df.fillna(0)
     
    #If in any column % of NAN values is > c then we will drop those colums 
    else:
        for i in dict(df.isnull().sum()/len(df)).keys():
            if dict(df.isnull().sum()/len(df))[i]*100>40:
                df.drop(columns=[i],axis=1,inplace=True)
     
    #for onehotencoding of all the categorical columns 
    #This the list of all object datatype columns 
    l_object=list(df.select_dtypes(include=['object','category']).columns )
    
    #for classification problem if the target column is object type then for converting it into numeric type 
    for i in l_object:
        if i==d:
            df[i]=pd.factorize(df[i])[0]
            
    #Now we will convert all categorical variables to dummy variables
    df1=pd.get_dummies(df)
    
    return df1
    

# second function for balancing the data

def data_balance_split(a,v1,v2,c,d,e):
    
    ''''' This function is used for balancing the unbalanced dataset if this function is used for classification
    problem, NO balancing is required in case of Regression problem also this function is used for train and test split 
    of dataset.
    
    keywords:
    
    v1 and v2 are the lower and the upper limits for the ratio of binary outputs of target column for classification problem.
    
    a : is the dataframe which is obtained using first function and by giving all required i/p arguments by the function.
    
    c : is the target column in string form.
     
    d : is the size of test dataset.
     
    e : for type of problem(Regression or Classification(binary)).
    
    NOTE: Make sure that the target output column is in axis otherwise you get error (Not found in axis)
    when you run this function.'''''
    
    from sklearn.model_selection import train_test_split
    
    #input features 'x'
    x=a.drop(c,axis=1)
    #output target column 
    y=a[c]
    
    if e=='Classification':
        
        if len(y.value_counts())==2:
            
            a1,a2=100*a[c].value_counts()/len(a[c])
            
            #a1 and a2 are the count of output which are present in the target column for binary classification problem 
    
        #getting the ratio of a1 and a2, v1<=(a1/a2)<=v2 than the dataset is called balanced otherwise not
        #so for unbalanced data we will do balancing using SMOTEENN as 
     
        #if dataset is balanced than doing train and test split as
        
            if v1<=a1/a2<=v2:
                #means dataset is balanced 
                x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=d)
        
            else:
                
                #means dataset is not balanced and we will balance it using 
                from imblearn.combine import SMOTEENN
                sm = SMOTEENN()
                X_resampled1, y_resampled1 = sm.fit_resample(x,y)
            
                #train and test split 
                x_train,x_test,y_train,y_test=train_test_split(X_resampled1, y_resampled1,test_size=d)
                
                
        else:
            x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=d)
        
            
    else:
        x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=d)
        
        
    return x_train,x_test,y_train,y_test
    
 
# Third function for getting the pandas profile report after and before the complete EDA process done using function 1 
# And saving these reports in HTML format file as

def data_report(a,b):
     
    '''' This function is for getting the pandas profile report of both raw initial data set and final refined dataset 
    which we get from first function as output and also saving the two profile reports in HTML file.
    
    keywords:
    
    a : is the dataframe which is obtained as output of first function after providing all the required input arguments by the function.
    
    b : is the original raw dataframe file in csv format for getting the profile report of original dataframe and also final 
    dataframe and we can also compair the difference between the two profile report.
    
    Before using this function make sure that pandas profile is installed in your system or notebook and if the latest 
    version in not working properly then in case you can installed any old version like
    
    !pip install pandas-profiling==2.7.1.
    
    But no need to import the profile report as it is already imported in this function you only have to intall pandas
    profile like
    
    from pandas_profile import ProfileReport '''''
    
    import pandas as pd
    #getting the dataframe of raw initial data as 
    df=pd.read_csv(b)
    
    from pandas_profiling import ProfileReport
    
    #generating profile report of raw initial data 
    pr_initial=ProfileReport(df,title='Pandas Profiling Report of raw initial data')
    pr1=pr_initial.to_widgets()
    #saving the html file of profile report 
    pr_initial.to_file('Initial_profile_report.html')
    
    
    #getting the profile report of the final dataframe which is obtained from the first function 
    pr_final=ProfileReport(a,title='Pandas Profiling Report of final cleaned data')
    pr2=pr_final.to_widgets()
    #saving the html file of final profile report 
    pr_final.to_file('Final_profile_report.html')
    
    return pr1,pr2
