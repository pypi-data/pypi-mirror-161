import os
import pickle


def unpickle(filepath: str):
    with open(filepath, "rb") as f:
        return pickle.load(f)  # nosec
