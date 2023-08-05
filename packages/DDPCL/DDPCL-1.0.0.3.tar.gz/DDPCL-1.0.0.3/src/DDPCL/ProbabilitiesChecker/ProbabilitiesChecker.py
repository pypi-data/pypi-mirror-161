import numpy as np
import face_recognition
from scipy import stats
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score

class ProbabilitiesChecker:
    # Initialization
    def __init__(self, probs_threshold=25.0, distance_threshold=0.5, encoding_face_size=128):
        self.probs_threshold = probs_threshold
        self.distance_threshold = distance_threshold
        self.encoding_face_size = encoding_face_size
    # Method for fitting Dataset and Labels
    def fit(self, data, labels):
        self.classes_gaussian = self.generate_gauss_per_class(data, labels)
        self.X = data
        self.y = labels
    
    # Generating gaussian (multivariate normal distribution) for all images of each class
    def generate_gauss_per_class(self,data,names):
        gaussians_per_class = {}
        for n in set(names):
            idx = [i for i in range(len(names)) if names[i] == n ]
            img_encoded = data[idx]
            gaussians_per_class[n] = self.generate_Gauss_multivar(img_encoded)
        return gaussians_per_class
    
    # Method for generating a multivariate gaussian
    def generate_Gauss_multivar(self,data):
        mean = np.mean(data, axis=0)
        df = pd.DataFrame(data)
        cov = np.cov(data.T)
        return stats.multivariate_normal(mean=mean, cov=cov, allow_singular=True)
    
    # Computing the probabilities of an image to belong to the existing class of the model
    def probabilities_distributions(self,infer_encod):
        probs_classes = {}
        for key,cg in self.classes_gaussian.items():
            probs_classes[key]= {'pdf' : cg.pdf(infer_encod)}
            #*(1/len(self.classes_gaussian))
            #,'logpdf:' : cg.logpdf(infer_encod)
        return probs_classes
    
    # Method for computing the distances of one image with the referenced classes
    def distances(self, infer_encod):
        preds_dist_classes = {}
        for n in set(self.y):
            idx = [i for i in range(len(self.y)) if self.y[i] == n ]
            img_encoded = self.X[idx]
            preds_dist_classes[n]= {'pred_dist' : face_recognition.face_distance(img_encoded, infer_encod).mean()}      
            #, 'nb_occ' : len(face_recognition.face_distance(img_encoded, infer_encod))
        return preds_dist_classes
    
    # Method for predicting
    # TODO include multiple predictions
    def predict(self, infer_encod):
        probs_gaussian_classes = self.probabilities_distributions(infer_encod)
        preds_distances_classes = self.distances(infer_encod)
        id_probs_over_threshold = [k for k,p in probs_gaussian_classes.items() if p['pdf'] >= self.probs_threshold]
        id_preds_lower_threshold = [k for k,d in preds_distances_classes.items() if d['pred_dist'] <= self.distance_threshold]
        id_most_prob_pred = np.intersect1d(id_probs_over_threshold,id_preds_lower_threshold)
        if len(id_most_prob_pred) == 0 or len(id_most_prob_pred) >1:
            return '???'
        else: 
            return id_most_prob_pred[0]    
    
    
    # Multiple predictions
    def multi_predict(self, data, encoded=True):
        preds=[]
        if encoded:
            inference = data
        else:
            inference = face_recognition.face_encodings(data)
        if len(inference.shape) >1:
            N,M = inference.shape 
            if N != self.encoding_face_size and M != self.encoding_face_size:
                return False
            else:
                if N == 1 or M == 1:
                     preds.append(self.predict(inference))
                else:
                    if N == self.encoding_face_size:
                        inference = inference.T
                    for i in range(len(inference)):
                        preds.append(self.predict(inference[i,:]))
        else: 
            preds.append(self.predict(inference)) 
        return preds
    
    
    def score(self, X_val, y_val):
        score = {}
        score['acc'] = accuracy_score(y_val,self.multi_predict(X_val))
        score['rec'] = recall_score(y_val,self.multi_predict(X_val), average='weighted', zero_division=0)
        return score