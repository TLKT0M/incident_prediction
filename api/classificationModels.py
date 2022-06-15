from regex import P
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import sqlite3

class classificationModels:
    X_train, X_test, y_train, y_test = [], [], [], []

    def __init__(self) -> None:
        self.preprocessData()

    def preprocessData(self) -> None:
        # Load data and split
        df_osm = self.preprocessOSMData()
        df_weather = self.preprocessWeatherData()
        df_merged = pd.merge(df_osm, df_weather, on=['incident_ID'])
        df_incident = self.prepeocessIncidentData()
        # Combine Datapoints and remove ID uses for combination
        df_merged = pd.merge(df_merged, df_incident, on=['incident_ID'])
        df_merged.drop('incident_ID', axis=1, inplace=True)

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

    def preprocessOSMData(self) -> pd.DataFrame:
        df_osm = pd.read_csv('api/data/OSM_data.csv')
        df_osm = df_osm[df_osm['lit'].notna()]
        df_osm = df_osm[df_osm['maxspeed'].notna()]
        df_osm['surface'] = df_osm['surface'].fillna('asphalt')
        # Remove not interpretable data and fill rest
        df_osm = df_osm.loc[(df_osm['maxspeed'] != 'signals')
                            & (df_osm['maxspeed'] != 'DE:urban')]
        df_osm['maxspeed'].replace({'none': '200'}, inplace=True)
        df_osm.drop('name', axis=1, inplace=True)
        # Reorganize Dataframe
        column_names = ['incident_ID', 'lit', 'maxspeed', 'surface']
        df_osm = df_osm.reindex(columns=column_names)
        # Map Light Values
        df_osm['lit'] = df_osm['lit'].map({'yes': 1, 'no': 0})
        # Change category attributes to bool values
        df_osm = self.explode(df_osm, ['surface'])
        df_osm.drop('surface', axis=1, inplace=True)
        return df_osm

    def preprocessWeatherData(self) -> pd.DataFrame:
        df_weather = pd.read_csv('api/data/weather_wuppertal.csv')
        df_weather = df_weather.fillna(0.0)
        return df_weather

    def prepeocessIncidentData(self) -> pd.DataFrame:
        # creating file path
        dbfile = 'api/data/test.db'
        # Create a SQL connection to our SQLite database
        con = sqlite3.connect(dbfile)
        # creating cursor
        cur = con.cursor()

        table_list = [a for a in cur.execute(
            "SELECT ID, UKATEGORIE, UART, UTYP1, ULICHTVERH, IstRad, IstPKW, IstFuss, IstKrad, IstSonstige FROM incident WHERE ULAND = '5' AND UREGBEZ = '1' AND UKREIS = '24' AND UGEMEINDE = '0'")]
        df_incident = pd.DataFrame(table_list)
        df_incident = df_incident.rename({0: 'incident_ID', 1: 'UKATEGORIE', 2: 'UART', 3: 'UTYP1',
                                          4: 'ULICHTVERH', 5: 'IstRad', 6: 'IstPKW', 7: 'IstFuss', 8: 'IstKrad', 9: 'IstSonstige'}, axis=1)
        df_incident = self.explode(df_incident, ['UTYP1', 'ULICHTVERH'])
        df_incident.drop(['UTYP1', 'ULICHTVERH'], axis=1, inplace=True)
        return df_incident

    def logisticRegression(self):
        from sklearn.linear_model import LogisticRegression
        logreg = LogisticRegression()
        logreg.fit(self.X_train, self.y_train)

        print('Accuracy of Logistic regression classifier on training set: {:.2f}'
              .format(logreg.score(self.X_train, self.y_train)))
        print('Accuracy of Logistic regression classifier on test set: {:.2f}'
              .format(logreg.score(self.X_test, self.y_test)))

    def decisionTree(self):
        from sklearn.tree import DecisionTreeClassifier
        clf = DecisionTreeClassifier()
        clf.fit(self.X_train, self.y_train)

        print('Accuracy of Decision Tree classifier on training set: {:.2f}'
              .format(clf.score(self.X_train, self.y_train)))
        print('Accuracy of Decision Tree classifier on test set: {:.2f}'
              .format(clf.score(self.X_test, self.y_test)))

    def k_Neraest(self):
        from sklearn.neighbors import KNeighborsClassifier
        knn = KNeighborsClassifier()
        knn.fit(self.X_train, self.y_train)

        print('Accuracy of K-NN classifier on training set: {:.2f}'
              .format(knn.score(self.X_train, self.y_train)))
        print('Accuracy of K-NN classifier on test set: {:.2f}'
              .format(knn.score(self.X_test, self.y_test)))

    def linearDiscriminatAnalysis(self):
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        lda = LinearDiscriminantAnalysis()
        lda.fit(self.X_train, self.y_train)

        print('Accuracy of LDA classifier on training set: {:.2f}'
              .format(lda.score(self.X_train, self.y_train)))
        print('Accuracy of LDA classifier on test set: {:.2f}'
              .format(lda.score(self.X_test, self.y_test)))

    def gaussianNaiveBayes(self):
        from sklearn.naive_bayes import GaussianNB
        gnb = GaussianNB()
        gnb.fit(self.X_train, self.y_train)

        print('Accuracy of GNB classifier on training set: {:.2f}'
              .format(gnb.score(self.X_train, self.y_train)))
        print('Accuracy of GNB classifier on test set: {:.2f}'
              .format(gnb.score(self.X_test, self.y_test)))

    def supportVectorMachine(self):
        from sklearn.svm import SVC
        svm = SVC()
        svm.fit(self.X_train, self.y_train)

        print('Accuracy of SVM classifier on training set: {:.2f}'
              .format(svm.score(self.X_train, self.y_train)))
        print('Accuracy of SVM classifier on test set: {:.2f}'
              .format(svm.score(self.X_test, self.y_test)))

    def explode(self, df, cols):
        row_count = len(df)
        new_cols = []
        for col in cols:
            unVals = df[col].value_counts()
            # unVals = unVals[unVals.values > round(row_count*0.05)]
            for key in unVals.index:
                name = str(col)+"_" + str(key)
                new_cols.append([col, name, key])
                df[name] = np.nan
        for col, name, key in new_cols:
            df[name] = np.where(df[col] == key, 1, 0)
        return df


if __name__ == '__main__':
    cm = classificationModels()
    cm.logisticRegression()
    cm.decisionTree()
    cm.k_Neraest()
    cm.linearDiscriminatAnalysis()
    cm.gaussianNaiveBayes()
    cm.supportVectorMachine()