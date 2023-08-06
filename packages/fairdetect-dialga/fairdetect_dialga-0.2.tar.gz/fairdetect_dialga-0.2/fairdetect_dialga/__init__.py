import matplotlib.pyplot as plt
from random import randrange
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
from tabulate import tabulate
from sklearn.metrics import confusion_matrix
from scipy.stats import chisquare
from sklearn.metrics import precision_score
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import xgboost
from IPython.display import display,Markdown

__version__ = '0.2'

class FairDetect:
    '''
    FairDetect class 
    ---------------
    This is Group D's FairDetect class improved version. This FairDetect class includes all the functions that will help you to run the bias analysis of your model.
    -----
    On this new version you are able to choose the varibles and run the model in 4 in simple steps.  The class works as follows:"
    '''
    affected_group=1
    affected_target=0
    def __init__(self):
        '''
        Initialization method
        ---------------------
        all tests are created'''
        self.data = 0
        self.categorical_variables=[]
        self.sensitive=''
        self.labels= ''
        self.X_train= []
        self.X_test= []
        self.y_train= []
        self.y_test= []
        self.y_test_predict= []
    def select_from_list (self,values_list):
        while True:
            try:
                self.printmd('### Please select one of the values below:')
                print(*values_list, sep = "\n")
                value = input('')
                values_list_str=[str(x) for x in values_list]
                if value not in values_list_str:
                    self.printmd('<div class="alert alert-block alert-danger"> Value not in the list.</div>')
                    raise NameError(value+ ' ' + 'Variable does not exists in dataset')
                else:
                    return value
            except :
                continue
            break
    def select_dependent_variable(self,df):
        '''
        Selection of dependent variable
        -----------------------------            
        Returns
        -------
        Y
        Notes
        -----
        dependent variable must be boolean
        '''
        while True:
            try:
                self.printmd('## Dependent variable need to be selected')
                y_label=self.select_from_list (df.columns)
                self.existing_variable (df,y_label)
                self.is_boolean_check(df,y_label)            
                return y_label
            except :
                continue
            break
    def select_sensitive_variable(self,df):
        '''
        Selection of sensitive variable
        -----------------------------
        Sensitive variable must be binary

        Notes
        -----
        If the variable contains more than 2 values the class gives the option to create a new boolean field based on one of the values

        Example
        -------
        If variable is country a new field ‘Spain’ can be created with Spain and Not Spain
        '''
        while True:
            try:
        
                self.printmd('## Sensitive variable need to be selected')
                columns=list(df.columns)
                columns.remove(self.y_label)
                sensitive=self.select_from_list (columns)
                self.existing_variable (df,sensitive)
                self.is_numeric_check(df,sensitive)
                if self.is_binary(df,sensitive)==False:
                    
                    self.printmd('<div class="alert alert-block alert-danger"> Sensitive variable must be binary. One value will be encoded.</div>')
                   # self.printmd('### Sensitive variable must be binary. One value will be encoded.')
                    value=self.select_from_list(list(df[sensitive].unique()))
                    self.data[value]= self.dummy_category(df,sensitive,value)
                    self.sensitive=value
                  #   print(self.data[value])
                else:
                    self.sensitive=sensitive
            except :
                continue
            break

    def is_numeric_check(self,df,variable):
        single_values= df[variable].unique()
        single_values.sort()
        evaluation=len(single_values)
        if df[variable].dtype != 'object' :
            print('This variable is numeric and contains '+ str(evaluation) + ' single results')
            print('Only categorical binary variables will be allowed to analize bias')
            print('If you continue, one value will be encoded. ')
            answer=input('Do you want to continue(Y/N)?')
            if answer=='Y':
                pass
            else: 
                raise NameError('discarted variable')


    def dummy_category(self,df,variable,value):
        '''
        Implementation of internal checks
        --------------------------------
        Checks creation of dummy variables
        Checks if variable is binary
        Checks if it is boolean
        '''
        df1=pd.DataFrame()
        variable_list=[variable]
        df1=pd.get_dummies(data=df,columns=variable_list)
        return df1[variable + '_' + value]
    def is_binary (self,df,variable):
        single_values= df[variable].nunique()
        if single_values==2:
            return True 
        else:
            return False 
    def is_boolean_check (self,df,variable): 
            single_values= df[variable].unique()
            single_values.sort()
            evaluation=len(single_values)

 
            if single_values[0]==0  and single_values[1]==1 and evaluation==2:

                pass
            else:
                self.printmd('<div class="alert alert-block alert-danger"> Variable must be boolean:'+ variable +'</div>')
                raise NameError(variable+ ' ' + 'Variable must be boolean')
    def printmd(self,string):
        display(Markdown(string))       

    def existing_variable (self,df,variable):
        '''
        It will check if the variable exists in the dataframe
        If variable does not exist returns an error
        '''
        while True:
            if (variable == df.columns).any():
                break
            else:
                raise NameError(variable+ ' ' + 'Variable does not exists in dataset')
                break

    def run_all(self):
        self.printmd('# Variables selection:')
        self.y_label=self.select_dependent_variable(self.data)
        self.select_sensitive_variable(self.data)
        self.printmd('# Data Cleansing')
        self.data_cleansing(self.sensitive)
        self.printmd('# Modelling')
        self.modelling(self.y_label)
        self.printmd('# Reporting')
        self.summary()
    def set_df(self, df):
        '''
        Data can be loaded from a dataframe
        '''
        self.data = df        
    def set_csv(self, csv):
        '''
        Data can be loaded from a csv
        '''
        self.data = pd.read_csv(csv)
    def data_cleansing(self,sensitive):
        '''
        2 improvements implemented in the data cleansing stage
        see improvement 1 and improvement 2
        '''
        self.columns_to_be_encoded()
        self.encoding_columns(sensitive)
        
    def columns_to_be_encoded(self):
        '''
        
        IMPROVEMENT 1
        ------------
        Identify and encode the categorical variables automatically
        '''
        for col in self.data.columns: 
             if self.data[col].dtypes == 'object' or col==self.sensitive:
                  self.categorical_variables.append(col)                 
    
    def encoding_columns(self,sensitive):
        '''
        
        IMPROVEMENT 2
        -------------
        Automatic creation of labels for the sensitive variable
        '''
        self.printmd('#### Categorical variables are being encoded')
        le = preprocessing.LabelEncoder()
        for col in self.categorical_variables:
            self.data[col] = le.fit_transform(self.data[col])
         #   self.printmd(col)
            if col==sensitive:
                self.labels = dict(zip(le.transform(le.classes_),le.classes_))
                
    def modelling(self,y_label):
        self.splitting_train_test(y_label)
        self.training_model()
    
    def splitting_train_test(self,y_label,train_size=0.8, test_size=0.2, random_state=0):
        '''
        Split our data into train and test
        '''
        self.printmd('#### Splitting Train and test data set as '+ str(train_size) + '/' + str(test_size))
        self.X = self.data.drop([y_label],axis=1) # axis: {0 or ‘index’, 1 or ‘columns’}, default 0
        self.y = self.data[y_label]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X,self.y,train_size=train_size, test_size=test_size, random_state=random_state)
   
    def training_model(self):
        '''
        Training our model with xgboost
        '''
        self.printmd('#### Training the model with xgboost.XGBClassifier')
        self.model = xgboost.XGBClassifier().fit(self.X_train, self.y_train)
        self.y_test_predict = self.model.predict(self.X_test)

    def summary(self):
        '''
        Summary of thecomplete bias analysis
        -----------------------------------
        Single method

        Returns
        -------
        Representation
        Ability
        Predictive
        Identifying bias
        Shap
        '''
        self.representation(self.X_test,self.y_test,self.sensitive,self.labels,self.y_test_predict)
        self.ability(self.sens_df,self.labels)
        self.ability_plots(self.labels,self.TPR,self.FPR,self.TNR,self.FNR)
        self.ability_metrics(self.TPR,self.FPR,self.TNR,self.FNR)
        self.predictive(self.labels,self.sens_df)
        self.identify_bias(self.sensitive,self.labels)
        self.understand_shap(self.labels,self.sensitive,self.affected_group,self.affected_target)

    def representation(self,X_test,y_test,sensitive,labels,predictions):
        '''
        Analysis of separate variables
        -----------------------------
        Compares two different variables

        Returns
        -------
        Contingency table
        Figures
        Dataframe
        P-value

        Notes
        -----
        With crosstab we will get the contingency table from which we will get the percentage table
        from these values we will get the chi value of the association of both variables
        '''
        full_table = X_test.copy()
        sens_df = {}

        for i in labels:
            full_table['p'] = predictions
            full_table['t'] = y_test
            sens_df[labels[i]] = full_table[full_table[sensitive]==i]

        contigency_p = pd.crosstab(full_table[sensitive], full_table['t']) 
        cp, pp, dofp, expectedp = chi2_contingency(contigency_p) 
        contigency_pct_p = pd.crosstab(full_table[sensitive], full_table['t'], normalize='index')

        sens_rep = {}
        for i in labels:
            sens_rep[labels[i]] = (X_test[sensitive].value_counts()/X_test[sensitive].value_counts().sum())[i]

        labl_rep = {}
        for i in labels:
            labl_rep[str(i)] = (y_test.value_counts()/y_test.value_counts().sum())[i]


        fig = make_subplots(rows=1, cols=2)

        for i in labels:
            fig.add_trace(go.Bar(
            showlegend=False,
            x = [labels[i]],
            y= [sens_rep[labels[i]]]),row=1,col=1)

            fig.add_trace(go.Bar(
            showlegend=False,
            x = [str(i)],
            y= [labl_rep[str(i)]],
            marker_color=['orange','blue'][i]),row=1,col=2)

        c, p, dof, expected = chi2_contingency(contigency_p)
        cont_table = (tabulate(contigency_pct_p.T, headers=labels.values(), tablefmt='fancy_grid'))
        
        self.sens_df = sens_df
        
        return cont_table, sens_df, fig, p



    def ability(self,sens_df,labels):
        '''
        It compares the ability of the sensitive groups    

        Returns
        -------
        true positive rate (TPR)
        false positive rate (FPR)
        true negative rate (TNR)
        false negative rate (FNR)
        '''
        sens_conf = {}
        for i in labels:
            sens_conf[labels[i]] = confusion_matrix(list(sens_df[labels[i]]['t']), list(sens_df[labels[i]]['p']), labels=[0,1]).ravel()

        true_positive_rate = {}
        false_positive_rate = {}
        true_negative_rate = {}
        false_negative_rate = {}

        for i in labels:
            true_positive_rate[labels[i]] = (sens_conf[labels[i]][3]/(sens_conf[labels[i]][3]+sens_conf[labels[i]][2]))
            false_positive_rate[labels[i]] = (sens_conf[labels[i]][1]/(sens_conf[labels[i]][1]+sens_conf[labels[i]][0]))
            true_negative_rate[labels[i]] = 1 - false_positive_rate[labels[i]]
            false_negative_rate[labels[i]] = 1 - true_positive_rate[labels[i]]
 
        self.TPR=true_positive_rate
        self.FPR=false_positive_rate
        self.TNR=true_negative_rate
        self.FNR=false_negative_rate
        
        return(true_positive_rate,false_positive_rate,true_negative_rate,false_negative_rate)



    def ability_plots(self,labels,TPR,FPR,TNR,FNR):
        '''
        The ability_plots method will plot the different metrics we have previously extracted
        '''
        fig = make_subplots(rows=2, cols=2, 
                            subplot_titles=("True Positive Rate", "False Positive Rate", "True Negative Rate", "False Negative Rate"))

        x_axis = list(labels.values())
        fig.add_trace(
            go.Bar(x = x_axis, y=list(TPR.values())),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(x = x_axis, y=list(FPR.values())),
            row=1, col=2
        )

        fig.add_trace(
            go.Bar(x = x_axis, y=list(TNR.values())),
            row=2, col=1
        )

        fig.add_trace(
            go.Bar(x = x_axis, y=list(FNR.values())),
            row=2, col=2
        )

        fig.update_layout(showlegend=False,height=600, width=800, title_text="Ability Disparities")
        fig.show()

    def ability_metrics(self,TPR,FPR,TNR,FNR):
        '''
        It calculates the chisquare rates for each different rate 

        Returns
        -------
        equalized odds
        '''
        TPR_p = chisquare(list(np.array(list(TPR.values()))*100))[1]
        FPR_p = chisquare(list(np.array(list(FPR.values()))*100))[1]
        TNR_p = chisquare(list(np.array(list(TNR.values()))*100))[1]
        FNR_p = chisquare(list(np.array(list(FNR.values()))*100))[1]

        if TPR_p <= 0.01:
            print("*** Reject H0: Significant True Positive Disparity with p=",TPR_p)
        elif TPR_p <= 0.05:
            print("** Reject H0: Significant True Positive Disparity with p=",TPR_p)
        elif TPR_p <= 0.1:
            print("*  Reject H0: Significant True Positive Disparity with p=",TPR_p)
        else:
            print("Accept H0: True Positive Disparity Not Detected. p=",TPR_p)

        if FPR_p <= 0.01:
            print("*** Reject H0: Significant False Positive Disparity with p=",FPR_p)
        elif FPR_p <= 0.05:
            print("** Reject H0: Significant False Positive Disparity with p=",FPR_p)
        elif FPR_p <= 0.1:
            print("*  Reject H0: Significant False Positive Disparity with p=",FPR_p)
        else:
            print("Accept H0: False Positive Disparity Not Detected. p=",FPR_p)

        if TNR_p <= 0.01:
            print("*** Reject H0: Significant True Negative Disparity with p=",TNR_p)
        elif TNR_p <= 0.05:
            print("** Reject H0: Significant True Negative Disparity with p=",TNR_p)
        elif TNR_p <= 0.1:
            print("*  Reject H0: Significant True Negative Disparity with p=",TNR_p)
        else:
            print("Accept H0: True Negative Disparity Not Detected. p=",TNR_p)

        if FNR_p <= 0.01:
            print("*** Reject H0: Significant False Negative Disparity with p=",FNR_p)
        elif FNR_p <= 0.05:
            print("** Reject H0: Significant False Negative Disparity with p=",FNR_p)
        elif FNR_p <= 0.1:
            print("*  Reject H0: Significant False Negative Disparity with p=",FNR_p)
        else:
            print("Accept H0: False Negative Disparity Not Detected. p=",FNR_p)




    def predictive(self,labels,sens_df):
        '''
        It compares the different distributions

        Returns
        -------
        Graph
        P-value
        '''
        precision_dic = {}

        for i in labels:
            precision_dic[labels[i]] = precision_score(sens_df[labels[i]]['t'],sens_df[labels[i]]['p'])

        fig = go.Figure([go.Bar(x=list(labels.values()), y=list(precision_dic.values()))])

        pred_p = chisquare(list(np.array(list(precision_dic.values()))*100))[1]

        return(precision_dic,fig,pred_p)




    def identify_bias(self, sensitive,labels):
        '''
        It runs the previous functions and will store and use previous values

        Returns
        -------
        This method will return the necessary metrics to conclude if there is bias or not
        '''
        predictions = self.model.predict(self.X_test)
        cont_table,sens_df,rep_fig,rep_p = self.representation(self.X_test,self.y_test,sensitive,labels,predictions)

        print("REPRESENTATION")
        rep_fig.show()

        print(cont_table,'\n')

        if rep_p <= 0.01:
            print("*** Reject H0: Significant Relation Between",sensitive,"and Target with p=",rep_p)
        elif rep_p <= 0.05:
            print("** Reject H0: Significant Relation Between",sensitive,"and Target with p=",rep_p)
        elif rep_p <= 0.1:
            print("* Reject H0: Significant Relation Between",sensitive,"and Target with p=",rep_p)
        else:
            print("Accept H0: No Significant Relation Between",sensitive,"and Target Detected. p=",rep_p)

        TPR, FPR, TNR, FNR = self.ability(sens_df,labels)
        print("\n\nABILITY")
        self.ability_plots(labels,TPR,FPR,TNR,FNR)
        self.ability_metrics(TPR,FPR,TNR,FNR)


        precision_dic, pred_fig, pred_p = self.predictive(labels,sens_df)
        print("\n\nPREDICTIVE")
        pred_fig.show()

        if pred_p <= 0.01:
            print("*** Reject H0: Significant Predictive Disparity with p=",pred_p)
        elif pred_p <= 0.05:
            print("** Reject H0: Significant Predictive Disparity with p=",pred_p)
        elif pred_p <= 0.1:
            print("* Reject H0: Significant Predictive Disparity with p=",pred_p)
        else:
            print("Accept H0: No Significant Predictive Disparity. p=",pred_p)


    def understand_shap(self,labels,sensitive,affected_group,affected_target):
        '''
        It identifies the specific area where the bias is ocurring and which features are more impacted by it

        Returns
        -------
        affected group
        affectcted target
        '''
        import shap
        explainer = shap.Explainer(self.model)

        full_table = self.X_test.copy()
        full_table['t'] = self.y_test
        full_table['p'] = self.model.predict(self.X_test)
        full_table

        shap_values = explainer(self.X_test)
        sens_glob_coh1 = np.where(self.X_test[sensitive]==list(labels.keys())[0],labels[0],labels[1])
        sens_glob_coh=[str(x) for x in sens_glob_coh1]
        
        misclass = full_table[full_table.t != full_table.p]
        affected_class = misclass[(misclass[sensitive] == affected_group) & (misclass.p == affected_target)]
        shap_values2 = explainer(affected_class.drop(['t','p'],axis=1))
        #sens_mis_coh = np.where(affected_class[sensitive]==list(labels.keys())[0],labels[0],labels[1])


        figure,axes = plt.subplots(nrows=2, ncols=2,figsize=(20,10))
        plt.subplots_adjust(right=1.4,wspace=1)

        print("Model Importance Comparison")
        shap.plots.bar(shap_values.cohorts(sens_glob_coh).abs.mean(0),show=False)
        plt.subplot(1, 2, 2) # row 1, col 2 index 1
        shap_values2 = explainer(affected_class.drop(['t','p'],axis=1))
        shap.plots.bar(shap_values2)
        #shap.plots.bar(shap_values2)

        full_table['t'] = self.y_test
        full_table['p'] = self.model.predict(self.X_test)
        #full_table=full_table[['checking_account','credit_amount','duration','sex','t','p']]

        misclass = full_table[full_table.t != full_table.p]
        affected_class = misclass[(misclass[sensitive] == affected_group) & (misclass.p == affected_target)]

        truclass = full_table[full_table.t == full_table.p]
        tru_class = truclass[(truclass[sensitive] == affected_group) & (truclass.t == affected_target)]

        x_axis = list(affected_class.drop(['t','p',sensitive],axis=1).columns)
        affect_character = list((affected_class.drop(['t','p',sensitive],axis=1).mean()-tru_class.drop(['t','p',sensitive],axis=1).mean())/affected_class.drop(['t','p',sensitive],axis=1).mean())

        #plt.figsize([10,10])
        #plt.bar(x_axis,affect_character)

        fig = go.Figure([go.Bar(x=x_axis, y=affect_character)])

        print("Affected Attribute Comparison")
        print("Average Comparison to True Class Members")
        fig.show()

        misclass = full_table[full_table.t != full_table.p]
        affected_class = misclass[(misclass[sensitive] == affected_group) & (misclass.p == affected_target)]

        #truclass = full_table[full_table.t == full_table.p]
        tru_class = full_table[(full_table[sensitive] == affected_group) & (full_table.p == affected_target)]

        x_axis = list(affected_class.drop(['t','p',sensitive],axis=1).columns)
        affect_character = list((affected_class.drop(['t','p',sensitive],axis=1).mean()-full_table.drop(['t','p',sensitive],axis=1).mean())/affected_class.drop(['t','p',sensitive],axis=1).mean())

        #plt.figsize([10,10])
        #plt.bar(x_axis,affect_character)

        fig = go.Figure([go.Bar(x=x_axis, y=affect_character)])
        print("Average Comparison to All Members")
        fig.show()

        print("Random Affected Decision Process")
        explainer = shap.Explainer(self.model)
        shap.plots.waterfall(explainer(affected_class.drop(['t','p'],axis=1))[randrange(0, len(affected_class))],show=False)
