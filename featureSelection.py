'''
This module takes a dataset containing a multitude
of features and finds the most significant ones by:

1. Take the first derivative of the time series data
2. Normalizing the data
3. With each iteration of the regression, remove some
   n features with the lowest weights according to the
   variable elimination schedule
4. Return the indeces of features expected to have the 
   most impact on the data

For use:
Constructor takes no arguments to create FeatureSelection
object.

FSA function initializes the observations, the labels,
shrinking parameter, the number of iterations, and 
stepsize.

Testing for eta to minimize the loss function is important.
For this reason, I shrink the value of eta over time.
'''

import numpy as np

class FeatureSelection:

  def __init__(self):
    self.X = np.array() #observations x features
    self.y = np.array() #labels
    self.w = np.array() #weights
    self._eta = 0 # the learning rate
    self._Niter = 0 #number of iterations
    self.mu = 0 #for the variable elimination schedule
    self.k = 5 #number of features to select
    self.s = 0 #shrinking rate

  # Subtracts by mean and divides by the standard deviation
  # to give a dataset with mean 0 and variance 1 (assuming
  # normal distribution) for each variable. This also deletes
  # any variables with variance 0 as they have no significance
  # in the regression. Because we standardize the labels, we
  # do not need to worry about predicting a constant value in 
  # the regression. 
  # 
  # We also add a row at the top containing the indices of the 
  # original matrix so they can be returned at the end of the 
  # feature selection process.
  def normalize(self):
    self.X[1:,:] = self.X[1:,:] - np.mean(self.X[1:,:], axis=0)
    self.y = self.y - np.mean(self.y)

    std = np.std(self.X[1:,:], axis=0)
    usecol = std!=0

    # remove unused columns
    self.X = self.X[:,usecol]

    # divide by std for used columns
    self.X[1:,:] = self.X[1:,:]/std[usecol]

    return


  # Variable Elimination. The arguments are X, k (the number of
  # variables we wish to keep), i(the iteration we are on), mu (the shrinking
  # parameter), M (the number of columns), ncol
  # (the number of columns).
  def varElim(self,i):
    ncol = self.X.shape()[1]
    #update number of variables to keep
    M = k + (ncol - k)*np.maximum(0,(self.Niter - 2*i)/(2*i*self.mu + self.Niter))
    ranked = np.absolute(self.w)
    temp = np.argsort(ranked)
    bad_col=[]
    for index in range(0,(ncol-int(M))):
      bad_col.append(temp[index])

    self.w = np.delete(self.w,bad_col,axis=None)
    self.X = np.delete(self.X,bad_col,axis=1)
    return 

  # Mean Square Error of the regression
  def MSE(self):
    return np.sum(np.square(np.dot(self.w,self.X[1:,:].T))) / np.shape(self.y)[0]

  # Gradient of the loss function (Mean Square Error minus 
  # shrinking parameter) taken with respect of the weights.
  def gradient(self):
    grad = -2*np.matmul(self.X[1:,:],y)+2*np.dot(np.dot(self.X[1:,:],self.X[1:,:].T),self.w)
    grad = grad + 2*self.s*self.w
    return grad
 

  # Our Loss function is not simply the MSE, we also include
  # a shrinking parameter because we prefer a smaller number
  # of features, and it prevents sticking to local minima.
  def Loss(self,i):
    l = MSE(self.X[1:,:],self.y,self.w) + self.s*np.sum(np.square(self.w))
    lossArr.append([i,l])
    return l

  # eta is the step-size we take towards the bottom
  # of the gradient. mu is the factor for the shrinking
  # parameter.
  def FSA(self,X,y,s=0,mu=50,Niter=400,eta=0.35,k=25):
    self.X = np.array(X)
    self.y = np.array(y)
    self.mu = mu
    self._eta = eta
    self._Niter = Niter
    self._k = k
    # contains the loss values for 
    self.lossArr = [[],[]]

    

    it_num = range(1,Niter+1)
    self.normalize()
    for i in range(1,Niter+1):
      # update the weights
      w = w - self.s * self.gradient()
      # variable elimination
      self.varElim(i)
      # calculate the loss
      self.Loss(i)
    return self.X[0,:]