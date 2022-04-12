from matplotlib import pyplot as plt
import numpy as np
from scipy.spatial import distance
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets import make_blobs

incidents = Incident.query.filter(text(filterst)).all()

def dbscan(X, eps, min_samples):
    db = DBSCAN(eps=eps, min_samples=min_samples)
    db.fit(X)
    y_pred = db.fit_predict(X)
    plt.scatter(X[:,0], X[:,1],c=y_pred, cmap='Paired')
    plt.title("DBSCAN")
    plt.show()

if __name__ == "__main__":
    dbscan(np.array([[5.8, 2.8], [6.0, 2.2]]),0.5,1)