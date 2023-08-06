import os, pickle


def save_model(model, file_name, folder_name="model"):
    """
    Saving object using pickle


    == Example usage ==
    save_model(model, "my_file.pkl")
    save_model(model.best_estimator_, "my_file.pkl")


    == Arguments ==
    model: Python Objects
        Python object to pickle. You may want to save your scikit-learn GridSearchCV or RandomizedSearchCV object.
        You can also save the best model too.

    file_name: string
        a string for the file name

    folder_name: string
        a string where the model is going to be saved
    """
    os.makedirs(folder_name, exist_ok=True)
    pickle.dump(model, open(f"{folder_name}/{file_name}", "wb"))
    print(f"Model is pickled as {folder_name}/{file_name}")
