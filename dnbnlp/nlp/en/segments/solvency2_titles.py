"""Title segmentation for English.

This module implements title segmentation/location in English using simple
machine learning classifiers.
"""

# Imports
import os
import string
from typing import Generator

# Packages
import pandas
import sklearn.ensemble
from sklearn.externals import joblib

# Project
from lexnlp.nlp.en.segments.utils import build_document_line_distribution
from lexnlp.utils.decorators import safe_failure
from lexnlp.utils.unicode.unicode_lookup import UNICODE_CHAR_TOP_CATEGORY_MAPPING


# Setup module path
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load segmenters
SECTION_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./solvency2_title_locator.pickle"))


def build_title_features(lines, line_id, line_window_pre, line_window_post, characters=string.printable,
                         include_doc=None):
    """
    Build a feature vector for a given line ID with given parameters.

    :param lines:
    :param line_id:
    :param line_window_pre:
    :param line_window_post:
    :param characters:
    :param include_doc:
    :return:
    """
    # Feature vector
    feature_vector = {}

    # Check start offset
    if line_id < line_window_pre:
        line_window_pre = line_id

    # Check final offset
    if (line_id + line_window_post) >= len(lines):
        line_window_post = len(lines) - line_window_post - 1

    # Iterate through window
    for i in range(0 - line_window_pre, line_window_post + 1):
        try:
            line = lines[line_id + i]
        except IndexError:
            continue

        index_str = str(i)
        # Count length
        feature_vector["line_len_" + index_str] = len(line)
        feature_vector["line_lenstrip_" + index_str] = len(line.strip())
        feature_vector["line_title_case_" + index_str] = line == line.title()
        feature_vector["line_upper_case_" + index_str] = line.isupper()

        alpha_count, number_count, punct_count, whitespace_count = 0, 0, 0, 0
        for c in line:
            if UNICODE_CHAR_TOP_CATEGORY_MAPPING[c] == 'L':
                alpha_count += 1
            elif UNICODE_CHAR_TOP_CATEGORY_MAPPING[c] == 'Z':
                whitespace_count += 1
            elif UNICODE_CHAR_TOP_CATEGORY_MAPPING[c] == 'N':
                number_count += 1
            elif UNICODE_CHAR_TOP_CATEGORY_MAPPING[c] == 'P':
                punct_count += 1

        # Count characters
        feature_vector["line_n_alpha_" + index_str] = alpha_count
        feature_vector["line_n_number_" + index_str] = number_count
        feature_vector["line_n_punct_" + index_str] = punct_count
        feature_vector["line_n_whitespace_" + index_str] = whitespace_count

    # Simple checks
    line = lines[line_id]
    line_strip_lower = line.strip().lower()
    feature_vector["orsa"] = 1 if "orsa" in line else 0
    feature_vector["Orsa"] = 1 if "Orsa" in line else 0
    feature_vector["ORSA"] = 1 if "ORSA" in line else 0
    feature_vector["Own Risk and Solvency Assessment"] = 1 if "Own Risk and Solvency Assessment" in line else 0
    feature_vector["OWN RISK AND SOLVENCY ASSESSMENT"] = 1 if "OWN RISK AND SOLVENCY ASSESSMENT" in line else 0
    feature_vector["rsr"] = 1 if "rsr" in line else 0
    feature_vector["Rsr"] = 1 if "Rsr" in line else 0
    feature_vector["RSR"] = 1 if "RSR" in line else 0
    feature_vector["Regular Supervisory Report"] = 1 if "Regular Supervisory Report" in line else 0
    feature_vector["REGULAR SUPERVISORY REPORT"] = 1 if "REGULAR SUPERVISORY REPORT" in line else 0
    feature_vector["sfcr"] = 1 if "sfcr" in line else 0
    feature_vector["Sfcr"] = 1 if "Sfcr" in line else 0
    feature_vector["SFCR"] = 1 if "SFCR" in line else 0
    feature_vector["Solvency and Financial Condition Report"] = 1 if "Solvency and Financial Condition Report" in line else 0
    feature_vector["Solvency Financial Condition Report"] = 1 if "Solvency Financial Condition Report" in line else 0
    feature_vector["Solvency"] = 1 if "Solvency" in line else 0
    feature_vector["Financial"] = 1 if "Financial" in line else 0
    feature_vector["Condition"] = 1 if "Condition" in line else 0
    feature_vector["Report"] = 1 if "Report" in line else 0
    feature_vector["SOLVENCY AND FINANCIAL CONDITION REPORT"] = 1 if "SOLVENCY AND FINANCIAL CONDITION REPORT" in line else 0
    feature_vector["SOLVENCY FINANCIAL CONDITION REPORT"] = 1 if "SOLVENCY FINANCIAL CONDITION REPORT" in line else 0
    feature_vector["SOLVENCY"] = 1 if "SOLVENCY" in line else 0
    feature_vector["FINANCIAL"] = 1 if "FINANCIAL" in line else 0
    feature_vector["CONDITION"] = 1 if "CONDITION" in line else 0
    feature_vector["REPORT"] = 1 if "REPORT" in line else 0

    # Build character vector
    characters_count = {}
    for character in characters:
        characters_count[character] = 0

    for character in lines[line_id]:
        if characters_count.get(character) is not None:
            characters_count[character] += 1

    for character, count in characters_count.items():
        feature_vector["char_" + character] = count

    # Add doc if requested
    if include_doc:
        feature_vector.update(include_doc)

    return feature_vector


def build_document_title_features(text, window_pre=3, window_post=3):
    """
    Get a document title given file text.
    """
    # Get document character distribution
    doc_distribution = build_document_line_distribution(text)

    # Parse all lines
    lines = text.splitlines()
    feature_data = []

    for line_id in range(len(lines)):
        feature_data.append(build_title_features(lines, line_id, window_pre, window_post, include_doc=doc_distribution))

    # Get feature DF
    feature_df = pandas.DataFrame(feature_data).fillna(-1).astype(int)
    return feature_df


def build_model(training_file_path, data_path):
    """
    Build a title extraction model given a training file path.

    :param training_file_path:
    :return:
    """
    import requests
    import numpy

    # Read title training data
    training_data = pandas.read_csv(training_file_path, encoding="utf-8", low_memory=False)
    training_data = training_data.loc[-training_data["Line Number"].isnull(), :]
    training_data.head()

    # All data
    all_feature_list = []
    all_target_list = []
    all_file_lines = []

    # Build training data
    for _, row in training_data.iterrows():
        # Download file
        file_name = row["File"]

        file = open(os.path.join(data_path, file_name), "rb")
        file_text = file.read().decode('utf-8')
        file.close()

        file_text = file_text.replace('\uf0b7', "")
        file_text = file_text.replace('\uf0a7', "")
        file_text = file_text.replace('\uf0fc', "")
        file_text = file_text.replace('\uf00c', "")
        file_text = file_text.replace('\uf00d', "")
        file_text = file_text.replace('\uf020', "")
        file_lines = file_text.splitlines()

        # Get features and target for model
        feature_data = build_document_title_features(file_text)
        target_data = pandas.Series(numpy.zeros((feature_data.shape[0],)))

        # Parse line numbers
        if "-" in str(row["Line Number"]):
            target_line_ranges = row["Line Number"].split("-")
            target_lines = list(range(int(target_line_ranges[0]),
                                      int(target_line_ranges[1]) + 1))
        else:
            target_lines = [int(row["Line Number"])]

#        if len(target_lines) > 2:
#            continue

        for target_line_num in target_lines:
            if len(file_lines[target_line_num - 1].strip()) > 0:
                target_data.iloc[target_line_num - 1] = 1

        # Append
        all_feature_list.append(feature_data)
        all_target_list.append(target_data)
        all_file_lines.extend((row["File"], l) for l in file_lines)

    # Collate
    all_feature_df = pandas.concat(all_feature_list, axis=0)
    all_target_df = pandas.concat(all_target_list, axis=0)

    # Build final model
    model = sklearn.ensemble.ExtraTreesClassifier(n_estimators=25)
    model.fit(all_feature_df, all_target_df)

    # Save production model
    joblib.dump(model, os.path.join(MODULE_PATH, "solvency2_title_locator.pickle"))


@safe_failure
def get_titles(text, window_pre=3, window_post=3, score_threshold=0.5) -> Generator:
    """
    Get titles from text.
    :param text:
    :param window_pre:
    :param window_post:
    :param score_threshold:
    :return:
    """

    # Get features and target for model
    feature_data = build_document_title_features(text, window_pre, window_post)

    # Predict title lines
    predicted_lines = SECTION_SEGMENTER_MODEL.predict_proba(feature_data)
    predicted_df = pandas.DataFrame(predicted_lines, columns=["prob_false", "prob_true"])
    title_lines = predicted_df.loc[predicted_df["prob_true"] >= score_threshold, :].index.tolist()

    # Check if results
    if len(title_lines) > 0:
        # Get lines
        lines = text.splitlines()

        # Iterate through lines
        title = ""
        for i in range(len(lines)):
            if i in title_lines:
                title += lines[i] + " "
            elif len(lines[i].strip()) == 0:
                continue
            else:
                if len(title) > 0:
                    yield title.strip()
                    title = ""

        if len(title) > 0:
            yield title.strip()
