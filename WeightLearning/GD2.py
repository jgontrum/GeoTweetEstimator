#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# turn of data table rendering
pd.set_option('display.notebook_repr_html', False)

sns.set_palette(['#00A99D', '#F5CA0C', '#B6129F', '#76620C', '#095C57'])

# Load the training set from csv
training_set = pd.read_csv('data/brainweight.csv')

# 1. Normalize our feature set x
features = training_set[['gender', 'agerange', 'headsize']]
observations = training_set['brainweight']
mu = features.mean()
sigma = features.std()

features_norm = (features - mu) / sigma
print features_norm.head()


# 2. Add a constant feature x0 with value 1
m = len(features_norm)  # number of data points
features_norm['x0'] = pd.Series(np.ones(m))
n = features_norm.columns.size  # number of features
print features_norm.head()

# 3. Set the initial alpha and number of iterations
alpha = 0.25
iterations = 150
m = len(observations) * 1.0

# 4. Initialize the theta values to zero
thetas = np.zeros(len(features_norm.columns))
print thetas


# 5. Calculate the theta's by performing Gradient Descent
features_norm = np.array(features_norm)
observations = np.array(observations)

cost_history = []

for i in range(iterations):
    # Calculate the predicted values
    predicted = np.dot(features_norm, thetas)

    # Calculate the theta's for this iteration:
    thetas -= (alpha / m) * np.dot((predicted - observations), features_norm)

    # Calculate cost
    sum_of_square_errors = np.square(predicted - observations).sum()
    cost = sum_of_square_errors / (2 * m)

    # Append cost to history
    cost_history.append(cost)

print thetas


