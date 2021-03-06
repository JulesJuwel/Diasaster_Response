import sys
import pandas as pd
import numpy as np

from sqlalchemy import create_engine

import nltk
nltk.download(['punkt', 'wordnet'])
import re
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.datasets import make_multilabel_classification
from sklearn.multioutput import MultiOutputClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
import pickle


def load_data(database_filepath):
    '''
    loading data from Disaster_Julia and 
    creating X,Y and category names for
    the model
    '''
    engine = create_engine(f'sqlite:///{database_filepath}')
    df = pd.read_sql_table('Disaster_Julia', engine)
    X = df.message.values 
    Y = df.drop(['message', 'genre', 'id', 'original'], axis = 1)
    category_names = Y.columns
    #print(category_names)
    return X, Y, category_names 


def tokenize(text):
    
    #tokenize text
    tokens = word_tokenize(text)
    
    #initiate lemmatizer
    lemmatizer = WordNetLemmatizer()
    
    clean_tokens = []
    
    for tok in tokens:
        
        clean_tok=lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
    
    return clean_tokens
    


def build_model():
    '''
    building model with pipeline and parameters and using
    GridSearch object
    '''
        
    # text processing and model pipeline
    pipeline = Pipeline([('vect', CountVectorizer(tokenizer=tokenize)), 
                     ('tfidf', TfidfTransformer()), 
                     ('clf', MultiOutputClassifier(ExtraTreesClassifier()))])
    
    # define parameters for GridSearchCV
    pipeline.get_params()
    parameters = {
    'clf__estimator__n_estimators' : [20, 50],
    'clf__estimator__min_samples_split' : [4,6],
    #'clf__estimator__max_leaf_nodes' : [2, None]
    }
    
    # create gridsearch object and return as final model pipeline
    model_pipeline = GridSearchCV(pipeline, param_grid=parameters)
    
    return model_pipeline

def evaluate_model(model, X_test, Y_test, category_names):
    #pred Y_pred with model
    Y_pred = model.predict(X_test)
    #print classification report and accuracy score
    for i, col in enumerate(Y_test):
        print(col)
        print(classification_report(Y_test[col], Y_pred[:, i], target_names=category_names))
        print('Accuracy Score: {}'.format(accuracy_score(Y_test[col], Y_pred[:, i])))
    
    #return model


def save_model(model, model_filepath):
    #create pkl file
    with open(model_filepath, 'wb') as f:
        pickle.dump(model, f)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()