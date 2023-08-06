import pandas as pd

urls = {
    "iris": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
    "dots": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/dots.csv",
    "anagrams": "https://raw.githubusercontent.com/mwaskom"
    "/seaborn-data/master/anagrams.csv",
    "fmri": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/fmri.csv",
}


def list_data():
    """List the test datasets."""
    print("These are the test datasets:")
    for key in urls:
        print("\t - " + key)


def load_data(name: str) -> pd.DataFrame:
    """Load a test dataset.

    Data are here: https://github.com/mwaskom/seaborn-data

    Inputs:
        name: The name of the test data
    Returns:
        df: The test data
    """
    url = urls[name]
    df = pd.read_csv(url)
    return df
