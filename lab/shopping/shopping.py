import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    
    evidence= []
    labels = []
    months = {'Jan':1,'Feb':2,'Mar':3,
              'Apr':4,'May':5,'June':6,
              'Jul':7,'Aug':8,'Sep':9,
              'Oct':10,'Nov':11,'Dec':12}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = []
            data.append(int(row['Administrative']))
            data.append(float(row['Administrative_Duration']))
            data.append(int(row['Informational']))
            data.append(float(row['Informational_Duration']))
            data.append(int(row['ProductRelated']))
            data.append(float(row['ProductRelated_Duration']))
            data.append(float(row['BounceRates']))
            data.append(float(row['ExitRates']))
            data.append(float(row['PageValues']))
            data.append(float(row['SpecialDay']))
            data.append(months[row['Month']])
            data.append(int(row['OperatingSystems']))
            data.append(int(row['Browser']))
            data.append(int(row['Region']))
            data.append(int(row['TrafficType']))
            data.append(0 if row['VisitorType'] == 'Returning_Visitor' else 1)
            data.append(0 if row['Weekend'] == 'FALSE' else 1)

            evidence.append(data)
            labels.append(0 if row['Revenue'] == 'FALSE' else 1)

    return (evidence,labels)

    


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    
    model = KNeighborsClassifier(n_neighbors=1)
    # Fit model
    model.fit(evidence,labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    num_lab_p = sum(labels)
    num_lab_n = len(labels) - num_lab_p
    num_acu_pre_p = 0
    num_acu_pre_n = 0

    for lab,pre in zip(labels,predictions):
        if lab == 1 and pre == 1:
            num_acu_pre_p += 1
        elif lab == 0 and pre == 0:
            num_acu_pre_n += 1

    sensitivity = num_acu_pre_p / num_lab_p
    specificty = num_acu_pre_n / num_lab_n

    return (sensitivity,specificty)
    

if __name__ == "__main__":
    main()
