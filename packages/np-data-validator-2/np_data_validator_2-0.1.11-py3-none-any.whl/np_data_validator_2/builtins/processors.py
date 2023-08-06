import os
import pickle


def unpickle(filepath: str, encoding="latin1"):
    with open(filepath, "rb") as f:
        return pickle.load(f, encoding=encoding)  # nosec
