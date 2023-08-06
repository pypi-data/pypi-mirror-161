import re
import time
import pandas as pd
import jaro
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from ftfy import fix_text

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ScorerNotAvailable(Exception):
    pass


class VectorizerNotDefined(Exception):
    pass


def ngrams(string: str, n=10) -> list:
    """
    Takes an input string, cleans it and converts to ngrams.
    :param string: str
    :param n: int
    :return: list
    """
    string = str(string)
    string = string.lower()  # lower case
    string = fix_text(string)  # fix text
    string = string.encode("ascii", errors="ignore").decode()  # remove non ascii chars
    chars_to_remove = [")", "(", ".", "|", "[", "]", "{", "}", "'", "-"]
    rx = '[' + re.escape(''.join(chars_to_remove)) + ']'  # remove punc, brackets etc...
    string = re.sub(rx, '', string)
    string = string.replace('&', 'and')
    string = string.title()  # normalise case - capital at start of each word
    string = re.sub(' +', ' ', string).strip()  # get rid of multiple spaces and replace with a single
    string = ' ' + string + ' '  # pad names for ngrams...
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]


def generateRelatedOntologies(query: str, choices: list, method: str, **kwargs) -> list or pd.DataFrame:
    """
    Generates ontologies in choices that are related to the query based on the method selected.
    :param query: str
    :param choices: list
    :param method: str (partial_ratio, jaro_winkler, tf_idf)
    :return: list
    """
    if method == 'partial_ratio':
        try:
            kwargs['df_ontology']
        except KeyError:
            related = process.extractBests(query, choices, scorer=fuzz.partial_ratio, limit=100)
            return related[1:]
        else:
            df_ontology = kwargs['df_ontology']
            related = process.extractBests(query, choices, scorer=fuzz.partial_ratio, limit=100)
            df_related_score = pd.DataFrame(related[1:], columns=['LABEL', 'partial_ratio'])
            df_related = df_ontology[df_ontology['LABEL'].isin([i[0] for i in related[1:]])]
            df_data = df_related.merge(df_related_score, on='LABEL')
            df_data = df_data.sort_values(by=['partial_ratio'], ascending=False)
            return df_data
    elif method == 'jaro_winkler':
        try:
            kwargs['df_ontology']
        except KeyError:
            related = process.extractBests(query, choices, scorer=jaro.jaro_winkler_metric, limit=100)
            return related[1:]
        else:
            df_ontology = kwargs['df_ontology']
            related = process.extractBests(query, choices, scorer=jaro.jaro_winkler_metric, limit=100)
            df_related_score = pd.DataFrame(related[1:], columns=['LABEL', 'partial_ratio'])
            df_related = df_ontology[df_ontology['LABEL'].isin([i[0] for i in related[1:]])]
            df_data = df_related.merge(df_related_score, on='LABEL')
            df_data = df_data.sort_values(by=['partial_ratio'], ascending=False)
            return df_data

    elif method == 'tf_idf':
        try:
            kwargs['vectorizer'], kwargs['tf_idf_matrix']
        except KeyError:
            raise VectorizerNotDefined("Please define a vectorizer in the fucntion call.")
        else:
            vectorizer = kwargs['vectorizer']
            tf_idf_matrix = kwargs['tf_idf_matrix']
            try:
                kwargs['df_ontology']
            except KeyError:
                fitted_query = vectorizer.transform([query])
                scores = cosine_similarity(tf_idf_matrix, fitted_query)
                return scores
            else:
                df_ontology = kwargs['df_ontology']
                fitted_query = vectorizer.transform([query])
                scores = cosine_similarity(tf_idf_matrix, fitted_query)
                df_ontology_temp = df_ontology
                df_ontology_temp['cosine_score'] = scores
                df_ontology_temp = df_ontology_temp.sort_values(by=['cosine_score'], ascending=False)
                df_data = df_ontology_temp[1:101]
                return df_data
    else:
        raise ScorerNotAvailable("Please define scorer from available options in the configuration file.")


def partial_ratio(string_1: str, string_2: str) -> float:
    """
    Calculates the fuzzywuzzy partial ratio between 2 strings.
    :param string_1: str
    :param string_2: str
    :return: float
    """
    ratio = fuzz.partial_ratio(string_1.lower(), string_2.lower())
    return ratio


def jaro_winkler(string_1: str, string_2: str) -> float:
    """
    Calculates the Jaro-Winkler score between 2 strings.
    :param string_1: str
    :param string_2: str
    :return: float
    """
    score = jaro.jaro_winkler_metric(string_1.lower(), string_2.lower())
    return score


def tf_idf(list_of_ontologies: list) -> float:
    """
    Calculates the cosine similarity between 2 strings after Term Frequency - Inverse Document Frequency Vectorization.
    :param list_of_ontologies: list
    :return: float
    """
    t1 = time.time()

    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
    tf_idf_matrix = vectorizer.fit_transform(list_of_ontologies)

    t = time.time() - t1
    print("Time:", t)
    print(tf_idf_matrix.shape)

    score = 0.0
    return score
