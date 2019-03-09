# Load libraries
import pandas
from pandas.plotting import scatter_matrix
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC


# Load dataset
url = "./mlb6.csv"
names = ['Win','Loss', 'Win Ratio','Team' ]
dataset = pandas.read_csv(url, names=names)

# shape
print(dataset.shape)

# descriptions
print(dataset.describe())



# # scatter plot matrix
# scatter_matrix(dataset)
# plt.show()
#
# # histograms
# dataset.hist()
# plt.show()

# Split-out validation dataset
array = dataset.values
X = array[:,0:3]
Y = array[:,3]
validation_size = 0.30
seed = 12
X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size, random_state=seed)
#Y_train=Y_train.astype('int')


# Test options and evaluation metric
seed = 5
scoring = 'accuracy'

# Spot Check Algorithms
models = []
models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))
models.append(('SVM', SVC(gamma='auto')))
# evaluate each model in turn
results = []
names = []
for name, model in models:
	kfold = model_selection.KFold(n_splits=20, random_state=seed)
	cv_results = model_selection.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
	results.append(cv_results)
	names.append(name)
	msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
	print(msg)

#Compare Algorithms
fig = plt.figure()
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(results)
ax.set_xticklabels(names)
plt.show()

# Make predictions on validation dataset
# knn = KNeighborsClassifier()
# knn.fit(X_train, Y_train)
# predictions = knn.predict(X_validation)
# print(accuracy_score(Y_validation, predictions))
# #print(confusion_matrix(Y_validation, predictions))
# print(classification_report(Y_validation, predictions))
# print(len(predictions))

dn= DecisionTreeClassifier()
dn.fit(X_train, Y_train)
predictions_d=dn.predict(X_validation)
print(accuracy_score(Y_validation, predictions_d))
print(confusion_matrix(Y_validation, predictions_d))
print(classification_report(Y_validation, predictions_d))
print(len(predictions_d))

