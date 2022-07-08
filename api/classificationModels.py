from regex import P
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt

class classificationModels:
    X_train, X_test, y_train, y_test = [], [], [], []

    accuracy_scores = {}

    weather_data_name = 'weather_wuppertal.csv'
    osm_data_name = 'OSM_data_wuppertal.csv'

    def __init__(self) -> None:
        self.preprocessData()

    """Loads data from all sources and combines the data, scales and splits
    
    Keyword arguments:
    Return: Bulding train and test set for model building and testing
    """
    
    def preprocessData(self) -> None:
        # Load data and split
        df_osm = self.preprocessOSMData()
        df_weather = self.preprocessWeatherData()
        try:
            del df_weather['Unnamed: 0']
        except KeyError:
            print("Key not existing")
    
        df_merged = pd.merge(df_osm, df_weather, on=['incident_ID'])
        df_incident = self.prepeocessIncidentData()
        df_merged = df_incident
        # Combine Datapoints and remove ID uses for combination
        # df_merged = pd.merge(df_merged, df_incident, on=['incident_ID'])
        df_merged.drop('incident_ID', axis=1, inplace=True)
        df_merged.corr()['UKATEGORIE'].to_csv('test.csv')
        # Extract Y and X Values for Models
        y = df_merged['UKATEGORIE'].to_numpy()
        df_merged.drop('UKATEGORIE', axis=1, inplace=True)
        X = df_merged.to_numpy()

        # print(df_osm.columns[df_osm.isna().any()].tolist()) # Find cols with nan
        # print(df_osm['surface'].isnull().sum()) # Number of nan in a column
        # print(df_osm['maxspeed'].unique()) # Find all values from column
        # print(df_merged['UKATEGORIE'].value_counts()) # How many of one value are in the data

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, random_state=42)
        scaler = MinMaxScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)

    """Preprocess OSM Data
    
    - Loads OSM Dataframe from osm_data_name
    - Deletes empty values from lit and maxspeed
    - Removes not feasable data from maxspeed column
    - Explodes categoric surafce attribute
    Return: Dataframe with all problematic values removed or filled
    """
        
    def preprocessOSMData(self) -> pd.DataFrame:
        df_osm = pd.read_csv('api/data/' + self.osm_data_name)
        df_osm = df_osm[df_osm['lit'].notna()]
        df_osm = df_osm[df_osm['maxspeed'].notna()]
        df_osm['surface'] = df_osm['surface'].fillna('asphalt')
        # Remove not interpretable data and fill rest
        df_osm = df_osm.loc[(df_osm['maxspeed'] != 'signals')
                            & (df_osm['maxspeed'] != 'DE:urban')
                            & (df_osm['maxspeed'] != 'DE:walk')
                            & (df_osm['maxspeed'] != 'walk')]
        df_osm['maxspeed'].replace({'none': '200'}, inplace=True)
        df_osm.drop('name', axis=1, inplace=True)
        # Reorganize Dataframe
        column_names = ['incident_ID', 'lit', 'maxspeed', 'surface']
        df_osm = df_osm.reindex(columns=column_names)
        # Map Light Values
        df_osm['lit'] = df_osm['lit'].map({'yes': 1, 'no': 0})
        df_osm = df_osm[df_osm['lit'].notna()]
        df_osm['maxspeed'] = pd.to_numeric(df_osm['maxspeed'])
        # Change category attributes to bool values
        df_osm = self.explode(df_osm, ['surface'])
        df_osm.drop('surface', axis=1, inplace=True)
        return df_osm

    """Preprocess Weather Data
    
    - Loads Weather Dataframe from osm_data_name
    - Fills missing values with 0
    Return: Dataframe with all problematic values removed or filled
    """
    
    def preprocessWeatherData(self) -> pd.DataFrame:
        df_weather = pd.read_csv('api/data/' + self.weather_data_name)
        df_weather = df_weather.fillna(0.0)
        return df_weather

    """Preprocess Incident Data
    
    - Gets data from SQL Database
    - Renaming cloumns in dataframe
    - Explode Categoric attributes like UTYP1 and ULICHTVERH
    Return: Dataframe with all incident data
    """
    
    def prepeocessIncidentData(self) -> pd.DataFrame:
        # creating file path
        dbfile = 'api/data/test.db'
        # Create a SQL connection to our SQLite database
        con = sqlite3.connect(dbfile)
        # creating cursor
        cur = con.cursor()

        # Wuppertal 5, 1, 24, 0
        # Karlsruhe 8, 2, 12, 0
        table_list = [a for a in cur.execute(
            "SELECT ID, UKATEGORIE, UART, UTYP1, ULICHTVERH, IstRad, IstPKW, IstFuss, IstKrad, IstSonstige FROM incident WHERE ULAND = '5' AND UREGBEZ = '1' AND UKREIS = '24' AND UGEMEINDE = '0'")]
        df_incident = pd.DataFrame(table_list)
        df_incident = df_incident.rename({0: 'incident_ID', 1: 'UKATEGORIE', 2: 'UART', 3: 'UTYP1',
                                          4: 'ULICHTVERH', 5: 'IstRad', 6: 'IstPKW', 7: 'IstFuss', 8: 'IstKrad', 9: 'IstSonstige'}, axis=1)
        df_incident = self.explode(df_incident, ['UTYP1', 'ULICHTVERH', 'UART'])
        df_incident.drop(['UTYP1', 'ULICHTVERH', 'UART'], axis=1, inplace=True)
        return df_incident

    """All models
    
    - Training and testing different types of classification models
    - Accuracy will be stored in accuracy_scores dict for later visualization
    Return: return_description
    """
    
    def logisticRegression(self):
        from sklearn.linear_model import LogisticRegression
        logreg = LogisticRegression(multi_class='multinomial')
        logreg.fit(self.X_train, self.y_train)

        train = logreg.score(self.X_train, self.y_train)
        test = logreg.score(self.X_test, self.y_test)
        self.accuracy_scores['Logistic Regression'] = [train, test]

        print('Accuracy of Logistic regression classifier on training set: {:.2f}'
              .format(train))
        print('Accuracy of Logistic regression classifier on test set: {:.2f}'
              .format(test))

    def decisionTree(self):
        from sklearn.tree import DecisionTreeClassifier
        clf = DecisionTreeClassifier()
        clf.fit(self.X_train, self.y_train)
        train = clf.score(self.X_train, self.y_train)
        test = clf.score(self.X_test, self.y_test)

        self.accuracy_scores['Decision Tree'] = [train, test]
        print('Accuracy of Decision Tree classifier on training set: {:.2f}'
              .format(train))
        print('Accuracy of Decision Tree classifier on test set: {:.2f}'
              .format(test))

    def k_Neraest(self):
        from sklearn.neighbors import KNeighborsClassifier
        knn = KNeighborsClassifier()
        knn.fit(self.X_train, self.y_train)

        train = knn.score(self.X_train, self.y_train)
        test = knn.score(self.X_test, self.y_test)
        self.accuracy_scores['Nearest Neighbor'] = [train, test]

        print('Accuracy of K-NN classifier on training set: {:.2f}'
              .format(train))
        print('Accuracy of K-NN classifier on test set: {:.2f}'
              .format(test))

    def linearDiscriminatAnalysis(self):
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        lda = LinearDiscriminantAnalysis()
        lda.fit(self.X_train, self.y_train)

        train = lda.score(self.X_train, self.y_train)
        test = lda.score(self.X_test, self.y_test)
        self.accuracy_scores['LDA'] = [train, test]

        print('Accuracy of LDA classifier on training set: {:.2f}'
              .format(train))
        print('Accuracy of LDA classifier on test set: {:.2f}'
              .format(test))

    def complementNaiveBayes(self):
        from sklearn.naive_bayes import ComplementNB
        cnb = ComplementNB()
        cnb.fit(self.X_train, self.y_train)

        train = cnb.score(self.X_train, self.y_train)
        test = cnb.score(self.X_test, self.y_test)
        self.accuracy_scores['Complement NB'] = [train, test]

        print('Accuracy of GNB classifier on training set: {:.2f}'
              .format(train))
        print('Accuracy of GNB classifier on test set: {:.2f}'
              .format(test))

    def supportVectorMachine(self):
        from sklearn.svm import SVC
        svm = SVC()
        svm.fit(self.X_train, self.y_train)

        train = svm.score(self.X_train, self.y_train)
        test = svm.score(self.X_test, self.y_test)
        self.accuracy_scores['SVM'] = [train, test]

        print('Accuracy of SVM classifier on training set: {:.2f}'
              .format(train))
        print('Accuracy of SVM classifier on test set: {:.2f}'
              .format(test))

    """Takes original dataframe and explodes given cloumns horizontal
    
    Keyword arguments:
    df -- Original dataframe
    cols -- Columns to be exploded
    Return: The OG Dataframe with additional columns for every class in categoric attributes from cols
    """
    
    def explode(self, df, cols):
        new_cols = []
        for col in cols:
            unVals = df[col].value_counts()
            for key in unVals.index:
                name = str(col)+"_" + str(key)
                new_cols.append([col, name, key])
                df[name] = np.nan
        for col, name, key in new_cols:
            df[name] = np.where(df[col] == key, 1, 0)
        return df

    """Takes Correlation data and visualizes it with Seaborn Package
    
    Keyword arguments:
    data -- data to be visualiszed
    Return: Plot with Heatmap 
    """
    
    def plotHeatMap(self, data):
        sns.heatmap(data)
        plt.show()

    """Uses accuracy_scores dict to visualize accuracys between models via bar diagram
    
    Return: Bar plot from accuracy_scores dict 
    """
    
    def plotAccuracy(self):
        df = pd.DataFrame(self.accuracy_scores)
        df['Genauigkeit der Modelle'] = ['Training', 'Testing']
        df.set_index('Genauigkeit der Modelle', inplace=True)
        df.plot(kind='bar')
        plt.show()

    """Function to fix column mistakes in OSM data for Karlsruhe
    
    Return: correct dataframe for training and testing
    """
    
    def fixOSMDataKarlsruhe(self):
        df_osm = pd.read_csv('api/data/OSM_data_karlsruhe.csv')
        df_2 = df_osm.loc[500:3748]
        df_3 = df_osm.loc[4249:]
        
        df_2['temp'] = df_2['surface']
        df_2['surface'] = df_2['maxspeed']
        df_2['maxspeed'] = df_2['temp']
        del df_2['temp'], df_2['Unnamed: 0']
        df_2.to_csv('test_2.csv')


        df_3['temp'] = df_3['surface']
        df_3['surface'] = df_3['maxspeed']
        df_3['maxspeed'] = df_3['temp']
        del df_3['temp'], df_3['Unnamed: 0']
        df_3.to_csv('test_3.csv')

if __name__ == '__main__':
    cm = classificationModels()
    cm.logisticRegression()
    cm.decisionTree()
    cm.k_Neraest()
    cm.linearDiscriminatAnalysis()
    cm.complementNaiveBayes()
    cm.supportVectorMachine()
    cm.plotAccuracy()