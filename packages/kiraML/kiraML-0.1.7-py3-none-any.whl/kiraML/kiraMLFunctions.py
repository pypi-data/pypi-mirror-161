"""
KiraML Library v0.1.0
"""
from sklearn import datasets, linear_model, neural_network
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import numpy as np
import os
import csv
from ._version import __version__
_seed = 1
np.random.seed(_seed)

DATASETS = {'diabetes' : ['age', 'sex', 'bmi', 'tc', 'ldl', 'hdl', 'tch', 'ltg', 'glu']}

MODELS = {'regression' : {'model': linear_model.LinearRegression, 'params': {}},
        'neural-network':  {'model': neural_network.MLPClassifier, 'params': {
            'hidden_layer_sizes':(15,), 
            'activation': 'logistic',
            'alpha': 1e-4,
            'solver': 'adam', 
            'max_iter': 500,
            'tol': -1, # Always go for the specified number of iterations
            # 'random_state': 1,
            'learning_rate_init': .1, 
            'verbose': True}
            },
        }

def load(dataset, features=None):
    """
    Loads one of the built-in kiraML datasets or a custom dataset
    """
    # try a built-in dataset
    load_fn = f"load_{dataset}"
    if hasattr(datasets, load_fn):
        x, y = getattr(datasets, load_fn)(return_X_y=True)
        if features:
            return x[:, np.newaxis, DATASETS[dataset].index(features[0])], y
        else:
            return x, y
    else:
        # try to load a local dataset
        # if features is None, assume all features but last for data, 
        # last feature for label
        try:
            with open(dataset) as f:
                x = []
                y = []
                data_reader = csv.reader(f, delimiter=',', quotechar='"')
                header = list(next(data_reader))
                if features:
                    x_index = header.index(features[0])
                    y_index = header.index(features[1])
                    for row in data_reader:
                        x.append([float(row[x_index])])
                        y.append(float(row[y_index]))
                    # shape of x needs to be (1, len(x))
                    # shape of y needs to be (len(y), )
                else:
                    for idx, row in enumerate(data_reader):
                        row_list = list(row)
                        x.append([float(x) for x in row_list[:-1]])
                        y.append(float(row_list[-1]))
                return np.array(x), np.array(y) 

        except: 
            raise InvalidDataset(dataset)

def split_data(data, train_percent=95):
    """
    Splits the data into a training and testing set.
    The default training set is 95% of the total data set
    Returns [training_set, test_set]
    """
    training_count = round(train_percent / 100 * len(data))
    return data[:training_count], data[training_count:]

def train(training_x, training_y, algorithm="regression", user_params = None):
    """
    Train a data set based on the model
    """
    # Train the model
    np.random.seed(_seed) # force same results for all tests
    params = MODELS[algorithm]['params']
    if user_params:
        # Ensures that the student does not pass in an absurd number of iterations and
        # cause a long-running loop
        if 'max_iter' in user_params:
            user_params['max_iter'] = min(2000, user_params['max_iter'])
        for param, val in user_params.items():
            params[param] = val
        if 'verbose' in user_params and user_params['verbose']:
            print("All training parameters:")
            print(params)

    training_obj = MODELS[algorithm]['model'](**params) 
    training_obj.fit(training_x, training_y)

    return training_obj

def predict(model, testing_x_data):
    """
    Make a prediction based on the model and testing_x_data
    """
    # Make a prediction
    return model.predict(testing_x_data)

def print_stats(model, y_test, y_pred):
    # this is going to be different for each model, unfortunately
    if type(model) is linear_model.LinearRegression:
        # The coefficients
        print(f"Coefficients: {model.coef_}\n")

        # The mean squared error
        print(f"Mean squared error: {mean_squared_error(y_test, y_pred):.2f}")

        # The coefficient of determination: 1 is perfect prediction
        print(f"Coefficient of determination: {r2_score(y_test, y_pred):.2f}", end='')
        print(" (1 would be a perfect prediction)")
    elif type(model) is neural_network.MLPClassifier:
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy of neural network model: {round(accuracy * 100, 1)}%")

def test(model, testing_x, testing_y, stats_only=False):
    """
    Given a model and testing data and labels, makes a prediction on all
    testing data and prints out predictions and accuracy.

    A wrapper around predict() and print_stats().
    """
    if not stats_only:
        print()
    preds = predict(model, testing_x)
   
    if not stats_only:
        print()
        for pred, actual in zip(preds, testing_y):
            print(f"Predicted: {pred}, Actual: {actual}, {pred == actual}")
    
        print()
    # print the data (mean squared error and coeficient of determination)
    print_stats(model, testing_y, preds)

def scatterplot(x_data, y_data, color="black"):
    plt.scatter(x_data, y_data, color=color) 

def drawline(x_data, y_data, color="blue", linewidth=3):
    plt.plot(x_data, y_data, color=color, linewidth=linewidth) 

def show_plot():
    plt.xticks(())
    plt.yticks(())

    plt.show()

def label_plot(title="title", x_label="x-axis", y_label="y-axis"):
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

def set_random_seed(n):
    global _seed
    np.random.seed(n) # force same results for all tests
    _seed = n

def get_random_seed():
    global _seed
    return _seed

# custom exceptions

class InvalidDataset(Exception):
    def __init__(self, name="(empty)"):
        super().__init__(f"Dataset '{name}' not found in library, or unreadable.")

