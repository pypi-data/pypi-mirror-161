import os
import shutil
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
import sys
sys.path.append('..')
from util_functions import loading_data

class Labeler:
    def __init__(self, target = 'CollectedImages/Unknown'):
        self.target = target
        
    def clustering(self):

        # Move all the images to the root Unknown and delete old folders
        move_data(self.target)
        
        
        # Loop through folder Unknown
        loaded_images_encodings, loaded_images_locations, loaded_images_names, loaded_images_fnames = loading_data(data_dir= self.target)
#         print(loaded_images_encodings.shape)
        
        
        # Get the clusters and their members with kmeans
        # Rule of the thumb for defining initial number of clusters : (n/2)^0.5, to lessen the number of clusters, after some tests
        # I chose to apply (n*3/2)^0.5
        kmeans= KMeans(init='random',random_state=0, n_clusters=(int((len(loaded_images_encodings)*1.5)**0.5)))
        clusters = kmeans.fit_predict(loaded_images_encodings)
        
        ordered_clusters = sorted(list(set(clusters)), reverse=False)
#         print('{} clusters determined'.format(clusters))
        # Create subfolders of Unknown to generate generic labels
        for i in range(len(ordered_clusters)):
            path = 'CollectedImages/Unknown/Unknown{}'.format(i)
            os.makedirs(path, exist_ok=False)
            
        
        # Affect/move all images to their corresponding Unknown cluster
        for c in range(len(ordered_clusters)):
            for i in range(len(loaded_images_fnames)):
                if clusters[i] == c:
                    dest = shutil.move(loaded_images_fnames[i], 'CollectedImages/Unknown/Unknown{}'.format(c))
#                     print(c,':',loaded_images_fnames[i])

        # Call drift detector to verify the new distribution
        
        
        # Call for retraining
#         loaded_images_encodings, loaded_images_locations, loaded_images_names, loaded_images_fnames = loading_data()
#         Xtrain, Xval, ytrain, yval = train_test_split(loaded_images_encodings, loaded_images_names, test_size=0.25, random_state=2)
#         model = ProbabilitiesChecker()
#         model.fit(Xtrain, ytrain)
#         model.score(Xval, yval)