import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    '''
    Loading data from the given filepaths and merging 
    it together to one data set df on the id-columns.
    '''
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    #merge data
    df = messages.merge(categories, on = 'id')
    return df


def clean_data(df):
    '''
    Cleaning the data, especially category columns.
    and dropping the duplicates.
    '''
    categories = df.categories.str.split(';', expand = True)
    # create name for categories by using first row (there is a name and a value for each column here)
    row = list(categories.iloc[0])

    category_colnames = [x[:-2] for x in row]
    categories.columns = category_colnames
    
    #convert category values to just number 0/1
    for column in categories:
    # set each value to be the last character of the string
        categories[column] = categories[column].str[-1:]
    
    # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
    
    #column related has  a 2 in it --> not binary --> make a 1 out of it
    categories = categories.replace(2, 1)
    
    # replace categories column in df with new category colums
    df = df.drop(columns = ['categories'])
    df = pd.concat([df, categories], axis = 1)
    
    # Remove duplicates
    df= df.drop_duplicates()
    
    
    
    return df


def save_data(df, database_filename):
    '''
    Saving the data to a Database, and if
    this databse exists then replace it.
    '''
    text = 'sqlite:///'+database_filename
    engine = create_engine(text)
    df.to_sql('Disaster_Julia', engine, if_exists='replace', index=False)
     


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()