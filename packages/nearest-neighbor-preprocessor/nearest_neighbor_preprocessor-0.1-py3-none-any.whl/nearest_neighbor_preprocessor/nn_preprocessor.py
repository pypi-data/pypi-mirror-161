from pynndescent import NNDescent
from sklearn.neighbors import NearestNeighbors
import numpy as np

class preprocessor:
    def __init__(self, n_principle_components, n_neighbors_query, nn_search_method='NNDescent'):
        self.pc_comp = n_principle_components
        self.n_query = n_neighbors_query
        self.nn_search_method = nn_search_method
        self.nn_model = None
        self.train_data = None
        self.labels = None
        self.query = None
        self.average_train_vector = None
        self.U_p = None

    def fit(self, X, y):

        self.train_data = X
        self.labels = y
        if isinstance(self.train_data, np.ndarray) is False:
            raise Exception("Data and labels must be numpy arrays")
        if self.train_data.shape[0] > self.train_data.shape[1]:
            # perform direct PCA
            self.x_data = self.train_data
            self.x_data = self.x_data.T

            self.average_train_vector = np.mean(self.x_data, axis=1)

            X_av = np.tile(self.average_train_vector, (self.x_data.shape[1], 1)).T
            S = np.dot((self.x_data - X_av), (self.x_data - X_av).T)
            eig_val, eig_vec = np.linalg.eig(S)
            eig_val_ind = np.argsort(eig_val)
            eig_val_ind = eig_val_ind[::-1]
            eig_val_ind = eig_val_ind[0:self.pc_comp]
            self.U_p = eig_vec[:, eig_val_ind]
            self.U_p = np.real(self.U_p)
            embedded_X = np.dot(self.U_p.T, self.x_data - X_av)

        if self.nn_search_method == 'NNDescent':
            self.nn_model = NNDescent(embedded_X.T, n_neighbors=500)
        elif self.nn_search_method == 'ball_tree':
            self.nn_model = NearestNeighbors(n_neighbors=3, algorithm='ball_tree').fit(embedded_X.T)
        else:
            print("Given method not yet implemented")

    def convert(self, query_data_set):
        self.query = query_data_set
        if isinstance(self.query, np.ndarray) is False:
            raise Exception("Query data and labels must be a numpy array")

        self.query = self.query.T

        X_av_query = np.tile(self.average_train_vector, (self.query.shape[1], 1)).T
        embedded_query = np.dot(self.U_p.T, self.query - X_av_query)

        predictions = []
        cleaned_images = []
        if self.nn_search_method == 'NNDescent':
            for i in embedded_query.T:

                indices, _ = self.nn_model.query(i.reshape(1, -1), k=self.n_query)

                vote = {}
                for n in (indices.squeeze()):

                    if self.labels[n] in vote:

                        vote[self.labels[n]] += 1
                    else:
                        vote[self.labels[n]] = 1

                key, val = max(vote.items(), key=lambda k: k[1])
                predictions.append(key)
                sum_pic = np.zeros(784)
                for pic in (indices.squeeze()):
                    if self.labels[pic] == key:
                        sum_pic += self.train_data[pic]

                mean_pic = sum_pic / val
                cleaned_images.append(mean_pic)

        elif self.nn_search_method == 'ball_tree':
            for i in embedded_query.T:

                _, indices = self.nn_model.kneighbors(i.reshape(1, -1))

                vote = {}
                for n in (indices.squeeze()):

                    if self.labels[n] in vote:

                        vote[self.labels[n]] += 1
                    else:
                        vote[self.labels[n]] = 1

                key, val = max(vote.items(), key=lambda k: k[1])
                predictions.append(key)
                sum_pic = np.zeros(784)
                for pic in (indices.squeeze()):
                    if self.labels[pic] == key:
                        sum_pic += self.train_data[pic]

                mean_pic = sum_pic / val
                cleaned_images.append(mean_pic)
        return (np.asarray(cleaned_images), np.asarray(predictions))