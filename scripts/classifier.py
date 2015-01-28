from __future__ import division, print_function
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree 

from sklearn import preprocessing
from sklearn import metrics
from sklearn import svm
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
import numpy as np
import pandas as pd




def main():

    infile = '/Users/nasrallah/Desktop/Insight/scotus_predict/db/feature_table.txt'

    ## Kennedy's words carry low weight among the justices, indicating that perhaps his speech is the least predictive of the outcome. Doesn't reveal much. That is IF the order is preserved...
    feature_names = ['amicus', 'cutoffs_ALL', 'cutoffs_BREYER', 'cutoffs_GINSBURG', 'cutoffs_KENNEDY', 'cutoffs_ROBERTS', 'cutoffs_SCALIA', 'words_BREYER', 'words_GINSBURG', 'words_KENNEDY', 'words_ROBERTS', 'words_SCALIA']
    #print(feature_names)

    ## get the feature table and partition into a 'gold' testing set and a training set (rest)
    d = pd.read_csv(infile, sep='\t', index_col=0)    
    #print(d.head())
    #print(d.shape)
    d_gold_start = int(d.shape[0] * 0.8)
    d_gold = d.iloc[d_gold_start:]
    d_rest = d.iloc[:d_gold_start]

    ## Get a numpy ndarray X (2d) of the case features and the labels y (1d) for the non-gold set
    X = d_rest[feature_names].values.astype(np.float)    
    y = preprocessing.LabelEncoder().fit_transform(d_rest.winner)
    
    ## Split this into training and testing sets
#    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)    

    ## Ensure the same split occurs every time we run the program, for now, to compare methods and hyperparameters
    this_test_start = X.shape[0] * 0.75 
    X_train = X[:this_test_start,]
    X_test = X[this_test_start:,]
    y_train = y[:this_test_start]
    y_test = y[this_test_start:]



    ## Define a scoring function with the Matthew correlation coefficient for cross-validation with unbalanced data
    mc_scorer = metrics.make_scorer(metrics.matthews_corrcoef)

    ##################### Random Forest #####################
    print('\nRandom Forest analyses:')   
    RF = RandomForestClassifier(n_estimators=50)
    RF_fit = RF.fit(X_train,y_train)
    RF_pred = RF_fit.predict(X_test)
    RF_prob = RF_fit.predict_proba(X_test)      ## Average outcome of all trees

    ## Classification probabilities
    #print('RF Prediction probabilities:')
    #for i,j in zip(RF_pred,RF_prob): print(i,j)

    ## Feature importances are helpful
    print('RF feature_importances:')
    for i, j in zip(feature_names, RF_fit.feature_importances_): print(i,j)
    
    print(metrics.classification_report(y_test, RF_pred))
    print(metrics.confusion_matrix(y_test, RF_pred))
    print('Test Accuracy:', RF_fit.score(X_test,y_test))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_test, RF_pred))
    
    RF_scores = cross_val_score(RF, X, y, cv=5, scoring=mc_scorer)
    #print('\nCross-validation scores:', RF_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (RF_scores.mean(), RF_scores.std() * 2))    
    print('-'*20)
    ## Transform removes the lower-importance features from the dataset and returns a trimmed input dataset. 
    ## In this case it removed the interruptions, but we already saw that removing them lowered performance.
    ## Was I overfitting?
    #print(RF.transform(X))

    ##################### Decision Tree #####################
#     print('\nDecision Tree analyses:')
#     DT = tree.DecisionTreeClassifier(max_depth=None, min_samples_split=1, random_state=0)
#     DT_fit = DT.fit(X_train, y_train)
#     DT_pred = DT_fit.predict(X_test)
# 
#     print(metrics.classification_report(y_test, DT_pred))
#     print(metrics.confusion_matrix(y_test, DT_pred))
#     print('Test Accuracy:', DT_fit.score(X_test,y_test))
#     print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_test, DT_pred))
#    
#     DT_scores = cross_val_score(DT, X, y, cv=5, scoring=mc_scorer)
#     print('\nCross-validation scores:', DT_scores)
#     print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (DT_scores.mean(), DT_scores.std() * 2))    
#     print('-'*20)
# 
#     #tree.export_graphviz(DT, out_file='tree.dot', feature_names=feature_names, max_depth=5) 


    ##################### SVM #####################

#### class_weight='auto'

    print('\nSVM analyses:')
    my_svm = svm.SVC(C=0.2, kernel='linear', probability=True)
    svm_fit = my_svm.fit(X_train, y_train)
    svm_pred = svm_fit.predict(X_test)
    svm_prob = svm_fit.predict_proba(X_test)            ## Class probabilities, based on log regression on distance to hyperplane.
    svm_dist = svm_fit.decision_function(X_test)        ## Distance from hyperplane for each point
    #SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3, gamma=0.0, kernel='rbf', max_iter=-1, probability=False, random_state=None, shrinking=True, tol=0.001, verbose=False)

    ## Classification probabilities
    #print('SVM Prediction probabilities:')
    #for i,j,k in zip(svm_pred, svm_prob, svm_dist): print(i,j,k)    

    print(metrics.classification_report(y_test, svm_pred))
    print(metrics.confusion_matrix(y_test, svm_pred))
    print('Test Accuracy:', svm_fit.score(X_test,y_test))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_test, svm_pred))
    
    SVM_scores = cross_val_score(my_svm, X, y, cv=5, scoring=mc_scorer)
    #print('\nCross-validation scores:', SVM_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (SVM_scores.mean(), SVM_scores.std() * 2))    
    
    #print(my_svm.predict([[-1, 1]]))

    ## Predict outcomes of the training data to see if do much better than cv data (overfitting)
    svm_pred_self = svm_fit.predict(X_train)
    print(metrics.classification_report(y_train, svm_pred_self))
    print(metrics.confusion_matrix(y_train, svm_pred_self))
    print('Test Accuracy:', svm_fit.score(X_train, y_train))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_train, svm_pred_self))



    ##################### Logistic Regression #####################


    print('\nLR analyses:')
    from sklearn.linear_model import LogisticRegression
    # Train
    LR = LogisticRegression(penalty='l2',C=1.0, fit_intercept=True)
    LR_fit = LR.fit(X_train, y_train) 


    LR_pred = LR_fit.predict(X_test)
    LR_prob = LR_fit.predict_proba(X_test)            ## Class probabilities, based on log regression on distance to hyperplane.



    print(metrics.classification_report(y_test, LR_pred))
    print(metrics.confusion_matrix(y_test, LR_pred))
    print('Test Accuracy:', LR_fit.score(X_test,y_test))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_test, LR_pred))
    
    LR_scores = cross_val_score(LR_fit, X, y, cv=5, scoring=mc_scorer)
    #print('\nCross-validation scores:', LR_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (LR_scores.mean(), LR_scores.std() * 2))    
    
    #print(LR_fit.predict([[-1, 1]]))

    ## Predict outcomes of the training data to see if do much better than cv data (overfitting)
    LR_pred_self = LR_fit.predict(X_train)
    print(metrics.classification_report(y_train, LR_pred_self))
    print(metrics.confusion_matrix(y_train, LR_pred_self))
    print('Test Accuracy:', LR_fit.score(X_train, y_train))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_train, LR_pred_self))






    #### ******* To DO: Do this for ALL cases, including gold set. - predict X_gold, save all d not just d_rest *******

    ## Once I've picked a model, test all cases and save the predictions and probabilities
    ## along with the case features as a database_table to put into mysql
    RF_final_predictions = RF_fit.predict(X)
    RF_final_probabilities = RF_fit.predict_proba(X)
    ## Get max of each probability tuple
    RF_final_probabilities = np.apply_along_axis(max, arr=RF_final_probabilities,axis=1)
    ## Drop old columns (fix this) and add new ones
    #d_rest.drop('prediction', axis=1, inplace=True)  ## probably just remove these from the transcripts.py output instead of manually here. Same w/probs.
    #d_rest.drop('confidence', axis=1, inplace=True)  ## probably just remove these from the transcripts.py output instead of manually here. Same w/probs.
    #d_rest['prediction'] = RF_final_predictions
    #d_rest['confidence'] = RF_final_probabilities

#     d_rest['prediction'] = pd.Series(RF_final_predictions, index=d_rest.index)
#     d_rest['confidence'] = pd.Series(RF_final_probabilities, index=d_rest.index)
#     ## Produces a warning b/c d_rest is a copy of d, so the warning is that d isn't being modified.
#     ## Doesn't really need to be a pd.Series...can just be: d_rest['prediction'] = RF_final_predictions
# 
#     outfile = '/Users/nasrallah/Desktop/Insight/scotus_predict/db/database_table.txt'
#     d_rest.to_csv(outfile, sep='\t')
    
    
if __name__ == '__main__':
    main()
