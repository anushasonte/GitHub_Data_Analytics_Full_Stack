'''
Goal of LSTM microservice:
1. LSTM microservice will accept the GitHub data from Flask microservice and will forecast the data for next 1 year based on past 30 days
2. It will also plot three different graph (i.e.  "Model Loss", "LSTM Generated Data", "All Issues Data") using matplot lib 
3. This graph will be stored as image in Google Cloud Storage.
4. The image URL are then returned back to Flask microservice.
'''
# Import all the required packages
from flask import Flask, jsonify, request, make_response
import os
from dateutil import *
from datetime import timedelta
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
from flask_cors import CORS

# Tensorflow (Keras & LSTM) related packages
import tensorflow as tf
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Input, Dense, LSTM, Dropout
from tensorflow.python.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

# Import required storage package from Google Cloud Storage
from google.cloud import storage

# Initilize flask app
app = Flask(__name__)
# Handles CORS (cross-origin resource sharing)
CORS(app)
# Initlize Google cloud storage client
client = storage.Client()

# Add response headers to accept all types of  requests

def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

#  Modify response headers when returning to the origin

def build_actual_response(response):
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

def preprocess_data(issues):
    # Convert input_data to a pandas DataFrame
    data_frame = pd.DataFrame(issues)

    # Group by 'created_at' and count the number of issues for each date
    df1 = data_frame.groupby(['created_at'], as_index=False).count()
    df = df1[['created_at', 'issue_number']]
    df.columns = ['ds', 'y']

    # Convert 'ds' to datetime format
    df['ds'] = pd.to_datetime(df['ds'])

    # Add additional features such as day of the week and month
    df['day_of_week'] = df['ds'].dt.day_name()
    df['month'] = df['ds'].dt.month

    return df

def predict_max_issues(model, input_data, is_month=False):
    df = preprocess_data(input_data)
    
    # Extract features from the preprocessed data
    array = df.to_numpy()
    x = np.array([time.mktime(i[0].timetuple()) for i in array])
    y = np.array([i[1] for i in array])

    lzip = lambda *x: list(zip(*x))

    days = df.groupby('ds')['ds'].value_counts()
    Y = df['y'].values
    X = lzip(*days.index.values)[0]
    firstDay = min(X)

    Ys = [0, ]*((max(X) - firstDay).days + 1)
    days = pd.Series([firstDay + timedelta(days=i) for i in range(len(Ys))])
    for x, y in zip(X, Y):
        Ys[(x - firstDay).days] = y

    Ys = np.array(Ys)
    Ys = Ys.astype('float32')
    Ys = np.reshape(Ys, (-1, 1))

    scaler = MinMaxScaler(feature_range=(0, 1))
    Ys = scaler.fit_transform(Ys)

    train_size = int(len(Ys) * 0.80)
    test_size = len(Ys) - train_size
    train, test = Ys[0:train_size, :], Ys[train_size:len(Ys), :]

    look_back = min(30, len(test))
    X_train, Y_train = create_dataset(train, look_back)
    X_test, Y_test = create_dataset(test, look_back)

    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    model.fit(X_train, Y_train, epochs=20, batch_size=70, validation_data=(X_test, Y_test),
              callbacks=[EarlyStopping(monitor='val_loss', patience=10)], verbose=1, shuffle=False)

    # Make predictions using the trained model
    model = initialize_lstm_model(look_back)
    predictions = model.predict(X_test)

    if is_month:
        # Find the month with the maximum predicted issues
        max_value = np.argmax(predictions) + 1  # Adding 1 to match month format (1-12)
    else:
        # Find the day of the week with the maximum predicted issues
        max_value = days[np.argmax(predictions)]

    return max_value

def create_dataset(dataset, look_back=1):
        X, Y = [], []
        for i in range(len(dataset)-look_back-1):
            a = dataset[i:(i+look_back), 0]
            X.append(a)
            Y.append(dataset[i + look_back, 0])
        return np.array(X), np.array(Y)

def initialize_lstm_model(look_back):
    model = Sequential()
    model.add(LSTM(100, input_shape=(1, look_back)))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

'''
API route path is  "/api/forecast"
This API will accept only POST request
'''

@app.route('/api/forecast/lstm', methods=['POST'])
def forecast():
    body = request.get_json()
    issues = body["issues"]
    type = body["type"]
    repo_name = body["repo"]
    data_frame = pd.DataFrame(issues)
    df1 = data_frame.groupby([type], as_index=False).count()
    df = df1[[type, 'issue_number']]
    df.columns = ['ds', 'y']

    df['ds'] = df['ds'].astype('datetime64[ns]')
    array = df.to_numpy()
    x = np.array([time.mktime(i[0].timetuple()) for i in array])
    y = np.array([i[1] for i in array])

    lzip = lambda *x: list(zip(*x))

    days = df.groupby('ds')['ds'].value_counts()
    Y = df['y'].values
    X = lzip(*days.index.values)[0]
    firstDay = min(X)

    '''
    To achieve data consistancy with both actual data and predicted values, 
    add zeros to dates that do not have orders
    [firstDay + timedelta(days=day) for day in range((max(X) - firstDay).days + 1)]
    '''
    Ys = [0, ]*((max(X) - firstDay).days + 1)
    days = pd.Series([firstDay + timedelta(days=i)
                      for i in range(len(Ys))])
    for x, y in zip(X, Y):
        Ys[(x - firstDay).days] = y

    # Modify the data that is suitable for LSTM
    Ys = np.array(Ys)
    Ys = Ys.astype('float32')
    Ys = np.reshape(Ys, (-1, 1))
    # Apply min max scaler to transform the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    Ys = scaler.fit_transform(Ys)
    # Divide training - test data with 80-20 split
    train_size = int(len(Ys) * 0.80)
    test_size = len(Ys) - train_size
    train, test = Ys[0:train_size, :], Ys[train_size:len(Ys), :]
    print('train size:', len(train), ", test size:", len(test))

    # Create the training and test datase
    '''
    Look back decides how many days of data the model looks at for prediction
    Here LSTM looks at approximately one month data
    '''
    look_back = min(30, len(test))
    X_train, Y_train = create_dataset(train, look_back)
    X_test, Y_test = create_dataset(test, look_back)

    # Reshape input to be [samples, time steps, features]
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # Verifying the shapes
    X_train.shape, X_test.shape, Y_train.shape, Y_test.shape

    # Model to forecast
    model = Sequential()
    model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Fit the model with training data and set appropriate hyper parameters
    history = model.fit(X_train, Y_train, epochs=20, batch_size=70, validation_data=(X_test, Y_test),
                        callbacks=[EarlyStopping(monitor='val_loss', patience=10)], verbose=1, shuffle=False)

    '''
    Creating image URL
    BASE_IMAGE_PATH refers to Google Cloud Storage Bucket URL.Add your Base Image Path in line 145
    if you want to run the application local
    LOCAL_IMAGE_PATH refers local directory where the figures generated by matplotlib are stored
    These locally stored images will then be uploaded to Google Cloud Storage
    '''
    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'Your_Base_Image_path')
    # DO NOT DELETE "static/images" FOLDER as it is used to store figures/images generated by matplotlib
    LOCAL_IMAGE_PATH = "static/images/"

    # Creating the image path for model loss, LSTM generated image and all issues data image
    MODEL_LOSS_IMAGE_NAME = "model_loss_" + type +"_"+ repo_name + ".png"
    MODEL_LOSS_URL = BASE_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME

    LSTM_GENERATED_IMAGE_NAME = "lstm_generated_data_" + type +"_" + repo_name + ".png"
    LSTM_GENERATED_URL = BASE_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME

    ALL_ISSUES_DATA_IMAGE_NAME = "all_issues_data_" + type + "_"+ repo_name + ".png"
    ALL_ISSUES_DATA_URL = BASE_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME

    # Add your unique Bucket Name if you want to run it local
    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'Your_BUCKET_NAME')

    # Model summary()

    # Plot the model loss image
    plt.figure(figsize=(8, 4))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Test Loss')
    plt.title('Model Loss For ' + type)
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.legend(loc='upper right')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)

    # Predict issues for test data
    y_pred = model.predict(X_test)

    # Plot the LSTM Generated image
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(np.arange(0, len(Y_train)), Y_train, 'g', label="history")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             Y_test, marker='.', label="true")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             y_pred, 'r', label="prediction")
    axs.legend()
    axs.set_title('LSTM Generated Data For ' + type)
    axs.set_xlabel('Time Steps')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)

    # Plot the All Issues data images
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(X, Ys, 'purple', marker='.')
    locator = mdates.AutoDateLocator()
    axs.xaxis.set_major_locator(locator)
    axs.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    axs.legend()
    axs.set_title('All Issues Data')
    axs.set_xlabel('Date')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME)

    # Uploads an images into the google cloud storage bucket
    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(MODEL_LOSS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)
    new_blob = bucket.blob(ALL_ISSUES_DATA_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME)
    new_blob = bucket.blob(LSTM_GENERATED_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)

    # Inside the /api/forecast/lstm route function, after making predictions
    max_day_of_week_created = predict_max_issues(model, issues, is_month = False)
    max_day_of_week_closed = predict_max_issues(model, issues, is_month = False)
    max_month_closed = predict_max_issues(model, issues, is_month = True)
    
    json_response = {
    "model_loss_image_url": MODEL_LOSS_URL,
    "lstm_generated_image_url": LSTM_GENERATED_URL,
    "all_issues_data_image": ALL_ISSUES_DATA_URL,
    "dayOfWeekMaxCreated": max_day_of_week_created,
    "dayOfWeekMaxClosed": max_day_of_week_closed,
    "monthOfYearMaxClosed": max_month_closed
    }

    # Returns image url back to flask microservice
    return jsonify(json_response)

# Run LSTM app server on port 8080
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


