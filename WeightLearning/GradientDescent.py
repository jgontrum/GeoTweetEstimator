#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import numpy as np
from sklearn.datasets.samples_generator import make_regression
import pylab
from scipy import stats

def gradient_descent(alpha, x, y, numIterations):
    m = x.shape[0] # number of samples
    theta = np.ones(4)
    x_transpose = x.transpose()
    for iter in range(0, numIterations):
        hypothesis = np.dot(x, theta) # evaluate all tweets in the corpus x with weights theta
        # hypothesis = vector of all calculated mid points
        loss = hypothesis - y # vector of distance between calculated and real coordinates
        J = np.sum(loss ** 2) / (2 * m)  # cost
        print "iter %s | J: %.3f" % (iter, J)
        gradient = np.dot(x_transpose, loss) / m
        print gradient
        theta = theta - alpha * gradient  # update
        print theta
    return theta

if __name__ == '__main__':

    x, y = make_regression(n_samples=100, n_features=1, n_informative=1,
                        random_state=0, noise=35)
    m, n = np.shape(x)

    # m = size of dev corpus
    # x = "tweets"
    # y = actual location of tweets in dev corpus

    x = np.c_[ np.ones(m), x] # insert column
    alpha = 0.01 # learning rate
    theta = gradient_descent(alpha, x, y, 10)

    # plot
    for i in range(x.shape[1]):
        y_predict = theta[0] + theta[1]*x
    pylab.plot(x[:,1],y,'o')
    pylab.plot(x,y_predict,'k-')
    pylab.show()
    print "Done!"