from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')

from sklearn.ensemble import GradientBoostingClassifier

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

import spacy

nlp = spacy.load("en_core_web_lg")
import numpy as np
import re
import string
from functools import partial
import datetime
import pickle

filter_keywords = ["payment", "coupon", "zone", "permit", "at", "park", "at hop", "card", "hop", "bus",
                   "train", "ferry", "driver", "staff", "buy", "broken", "report", "lost", "left", "tag",
                   "lane", "notice", "request", "property", "project", "information", "info"]

classifiers_name = [
    "Nearest_Neighbors",  # 0
    "Linear_SVM",  # 1
    "RBF_SVM",  # 2
    "Gaussian_Process",  # 3
    "Decision_Tree",  # 4
    "Random_Forest",  # 5
    "Neural_Net",  # 6
    "AdaBoost",  # 7
    "Naive_Bayes",  # 8
    "QDA",  # 9
    "Gradient_Booster"  # 10
]

classifiers = [
    KNeighborsClassifier(3),  # 0
    SVC(kernel="linear", C=0.025),  # 1
    SVC(gamma=2, C=1),  # 2
    GaussianProcessClassifier(1.0 * RBF(1.0)),  # 3
    DecisionTreeClassifier(max_depth=5),  # 4
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),  # 5
    MLPClassifier(alpha=1, max_iter=1000),  # 6
    AdaBoostClassifier(),  # 7
    GaussianNB(),  # 8
    QuadraticDiscriminantAnalysis(),  # 9
    GradientBoostingClassifier(n_estimators=400, random_state=0)  # 10
]


def clean_text(text):
    """
    Make text lowercase, remove text in square brackets, remove links, remove punctuation, remove unwanted space
    and remove words containing numbers.

    Args:
        text: string containing text

    """
    text = str(text).lower()
    text = text.strip()
    text = re.sub("[\"\']", "", text)
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = " ".join(text.split())
    text = text.strip()
    return text


def isNegative(token, sentence):
    """
    Takes a token representing a word and a doc representing a sentence
    Returns whether the word is negated in the sentence

    Args:
        token: word in spacy language model object
        sentence: sentence in spacy language model object
    """
    for word in sentence:
        if word.dep_ == 'neg':  # if word is a negation
            if word.head == token:  # check if it negates the desired word
                return True
    return False


def inClause(token, sentence):
    """
    Takes a token representing a word and a doc representing a sentence
    Returns whether the word is part of a subordinate clause rather than the main clause
    However, clauses subordinated by certain verbs of knowing or asking are included with main clauses

    Args:
        token: word in spacy language model object
        sentence: sentence in spacy language model object
    """

    clausetypes = ['advcl', 'relcl', 'csubj', 'csubjpass', 'pcomp', 'xcomp', 'acl', 'aux']
    knowing = ['know', 'understand', 'see', 'get']
    asking = ['wonder', 'ask', 'inquire', 'demand']

    check_infinite_loop_counter = 0

    while token.dep_ != 'ROOT' and check_infinite_loop_counter < len(sentence):
        if token.dep_ in clausetypes:
            return True
        if token.dep_ == 'ccomp' or token.dep_ == 'conj':
            if token.head.lemma_ in knowing:  # if it is a verb of knowing, only use negatives
                return not isNegative(token.head, sentence)
            if token.head.lemma_ in asking:
                return False
            return True

        token = token.head

        check_infinite_loop_counter = check_infinite_loop_counter + 1

    return token.pos_ != 'VERB' and token.pos_ != 'AUX'  # phrase head should be a verb


def isWHQuestion(sentence):
    """
    tokens.doc -> bool
    Takes a string representing a sentence
    Returns whether the sentence is a wh-question, i.e. who-what-where-when-why

    Args:
        token: word in spacy language model object
        sentence: sentence in spacy language model object
    """

    whwords = ['who', 'what', 'where', 'when', 'why', 'how', 'which', 'whose', 'whence', 'whither', 'whom']
    for word in sentence:
        if word.lemma_ in whwords:  # for each wh-word, see if it is in the main clause
            if inClause(word, sentence):
                continue  # if not, continue looking for wh-words
            return True
    return False


def extract_question(x, model, only_direct=True):
    """
    main function in extracting questions
    takes are paragraph, split them into sentences and checks if a sentence is question or not

    Args:
        model: ML model object
        only_direct: boolean, True extracts only the direct questions. False outcomes raw model prediction result
    """

    raw_sentences = re.split('[ ]*[.?!;\n]+[ \n]*', x)
    questions = []  # output list of questions
    for element in raw_sentences:
        if model.predict([clean_text(element)]) == "Question":  # check if the sentence is a question through ml model
            if only_direct:
                if isWHQuestion(nlp(element)):  # check for noun clause
                    if any(x in element.split(' ') for x in filter_keywords):
                        questions.append(element)
            else:
                questions.append(element)
    if questions:
        return questions
    else:
        np.nan


class classification_model:

    def __init__(self, mode):
        """
        Init function

        Args:
            mode: string value containing either "Train" or "Predict"
        """
        self.mode = mode

    def train_init(self, dataset, dataset_name, data_split):
        """
        Init function training

        Args:
            dataset: dataset in pandas DataFrame
            dataset_name: dataset name in string
            data_split: float value for splitting training data (e.g 0.8)
        """
        self.dataset = dataset
        self.dataset_name = dataset_name
        self.split = data_split

    def predict_init(self, model_filepath):
        """
        Init function prediction

        Args:
            model_filepath: string referring to path of the saved model file
        """
        self.load(model_filepath)

    def convert_data_into_num(self, data):
        """
        data encoding

        Args:
           data: list of raw text
        """
        return embedder.encode(data)

    def prep_data_for_training(self):
        """
        Prepares the data for model training
        Data splitting
        Text data encoding
        """

        dataset = self.dataset

        train = dataset.sample(frac=self.split, random_state=220)  # random state is a seed value
        test = dataset.drop(train.index)

        train_text = list(train.processed_doc)
        test_text = list(test.processed_doc)

        X_train = convert_data_into_num(train_text)  # vectorizer.fit_transform(train_text)
        X_test = convert_data_into_num(test_text)  # vectorizer.transform(test_text)

        y_train = list(train.label)
        y_test = list(test.label)

        return X_train, y_train, X_test, y_test

    def training(self, classifier_num=2):
        """
        model training and scoring

        Args:
           classifier_num: integer referes index of classifiers variable
        """

        model = classifiers[classifier_num]

        X_train, y_train, X_test, y_test = self.prep_data_for_training()

        print("---- model training ----")
        model.fit(X_train, y_train)

        score = model.score(X_test, y_test)

        self.classifier_name = classifiers_name[classifier_num]

        self.model = model

        print(f"{self.classifier_name} accuracy - {score}")

    def save(self):
        """
        saves the model in models folder in the format dataset_name_classifier_name_time
        Called from training function
        """
        now = datetime.datetime.now()
        filename = f"models/{self.dataset_name}_model_{self.classifier_name}_{now.day}-{now.hour}-{now.minute}.sav"
        pickle.dump(self.model, open(filename, 'wb'))
        print(f"---- model saved ---- {filename}")

    def load(self, filename):
        """
        loads the model from given filename path

        Args:
           filename: path of the file in string
        """

        self.model = pickle.load(open(filename, 'rb'))
        print(f"---- model loaded ---- {filename}")

    def predict(self, predict_data):
        """
        predicts data from loaded model

        Args:
           predict_data: list of sentences

        Returns:
           array of predictions
        """

        prediction = self.model.predict(self.convert_data_into_num(predict_data))
        return prediction[0]



