import pickle


def load_model(model_path):
    """
    Saving object using pickle


    == Example usage ==
    load_model("model/my_file.pkl")


    == Arguments ==
    model_path: string
        a .pkl model file path
    """
    model = pickle.load(open(model_path, "rb"))
    return model
