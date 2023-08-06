import pytest


class ChemBee:
    """
    Just the rough interface
    """

    def __init__(self, data_path: str):
        pass

    def load_classifier(self, result: dict, clf: str = "rfc"):
        from chembee_config.calibration.knn import KNeighborsClassifierAlgorithm
        from chembee_config.calibration.random_forest import (
            RandomForestClassifierAlgorithm,
        )
        from chembee_config.calibration.mlp_classifier import MLPClassifierAlgorithm
        from chembee_config.calibration.svc import NaivelyCalibratedSVC

        from sklearn.neighbors import KNeighborsClassifier

        from file_utils import load_json_from_file

        clf = RandomForestClassifierAlgorithm(**fitted_clf[clf]["best_parameters"])
        return clf

    def filter_features(
        self, data=None, cut_off=0.01, target=None, X_data=None, y_data=None
    ):

        from chembee_actions.feature_extraction import (
            get_feature_importances,
            filter_importance_by_std,
        )
        from chembee_plotting.feature_extraction import plot_feature_importances

        if data == None:
            data = self.data
        if target == None:
            target = self.target
        if X_data == None:
            X_data = self.X_data
        if y_data == None:
            y_data = self.y_data
        result_json = get_feature_importances(
            X_data, y_data, feature_names=data.drop(columns=target).columns.to_list()
        )
        result_json = filter_importance_by_std(result_json, cut_off=cut_off)
        sorted_std = np.array(result_json["std"])
        indices = np.argpartition(sorted_std, -len(sorted_std))[-len(sorted_std) :]
        X_data = data[data.columns.to_numpy()[indices]]
        return X_data

    def get_mols(self, mol_path: str):
        mols = Chem.SDMolSupplier(mol_path)
        return mols


class BMBee(ChemBee):

    file_name = "feature_extraction"
    prefix = "mordred"
    target = "ReadyBiodegradability"
    name = "mordred_reduced"

    def __init__(self, data_set_path: str, mol_path: str, split_ratio: float = 0.7):
        self.data, self.X_data, self.y_data = self.prepare_data_set(data_set_path)
        self.mols = self.get_mols(mol_path=mol_path)

    def prepare_data_set(self, data_set_path, split_ratio=0.7):
        """
        The prepare_data function takes in a data set path and splits it into training and testing sets.
        It also saves the data as csv files for easy access. Could also be an ETL process.

        :param data_path: Used to specify the path to the data file.
        :param split_ratio=0.7: Used to split the dataset into training and test set.
        :return: A dataframe with the clean dataset, and a numpy array of the target variable.

        :doc-author: Julian M. Kleber
        """

        target = "ReadyBiodegradability"
        data = pd.read_csv(data_set_path)
        data = data.drop(columns=["Unnamed: 0"])
        for col in data.columns.tolist():
            data_col = pd.to_numeric(data[col], errors="coerce")
            data[col] = data_col
        data = data.fillna(0)
        X_data = data.drop(columns=[target]).to_numpy()  # is unnecessary
        y_data = data[target].to_numpy()
        return data, X_data, y_data


class FPBee(ChemBee):
    target = "ReadyBiodegradability"
    name = "fingerprints"

    def __init__(self, mol_path: str, split_ratio: float = 0.7):
        self.X_data, self.y_data = self.prepare_data_set(mol_path)
        self.mols = self.get_mols(mol_path=mol_path)

    def prepare_data_set(self, mol_path: str, radius=3, n_bits=2048, target=None):
        from rdkit.Chem import PandasTools
        from chembee_preparation.processing import convert_mols_to_morgan_fp

        if target is None:
            target = self.target

        mols = self.get_mols(mol_path=mol_path)
        data = PandasTools.LoadSDF(mol_path)
        y_data = data[target].to_numpy().astype(np.int32)
        data = convert_mols_to_morgan_fp(
            mols, radius=radius, n_bits=n_bits, return_bit=True
        )
        data = np.array(data)
        return data, y_data


class LPBee(ChemBee):
    target = "ReadyBiodegradability"
    name = "lipinski"

    def __init__(self, mol_path: str, split_ratio: float = 0.7):
        self.X_data, self.y_data = self.prepare_data_set(mol_path)
        self.mols = self.get_mols(mol_path=mol_path)

    def prepare_data_set(self, mol_path: str, target=None):
        from rdkit.Chem import PandasTools
        from chembee_preparation.processing import calculate_lipinski_desc
        from chembee_datasets.BioDegDataSet import BioDegDataSet

        if target is None:
            target = self.target

        mols = self.get_mols(mol_path=mol_path)
        data = PandasTools.LoadSDF(mol_path)
        data = calculate_lipinski_desc(data, mols)
        data = self.clean_data(data)
        X_data = data.drop(columns=target).to_numpy()
        y_data = data[target].to_numpy()
        return X_data, y_data

    def clean_data(self, data):
        """
        The clean_data function takes in a dataframe and cleans it by removing the SMILES, CASRN, ID and Dataset columns.
        It also converts all of the dtypes to float64 or int64. It returns a cleaned dataframe.

        :param self: Used to reference the class itself.
        :param data: Used to pass the data that is to be cleaned.
        :return: A dataframe with the columns "smiles", "dataset", "casrn" and "id" dropped, and all other columns converted to numeric type.

        :doc-author: Trelent
        """

        data = data.drop(columns=["Dataset", "CASNR", "ID"])
        data = data.convert_dtypes()
        bad_types = data.select_dtypes(
            exclude=["string", "int64", "float64"]
        ).columns.to_list()
        data = data.drop(columns=bad_types)
        return data


@pytest.fixture(scope=session)
def lpbee():
    """
    initiates bee with enhanced lipinski fingerprints
    """
    lpbee = LPBee(mol_path="AllPublicnew.sdf")
    fitted_clf = load_json_from_file("lipinski_cv.json")
    lpbee.clf = lpbee.load_classifier(fitted_clf)
    return lpbee


@pytest.fixture(scope=session)
def fpbee():
    """
    Initiates bee with Morgan fingerprints
    """
    fpbee = FPBee(mol_path="AllPublicnew.sdf")
    fitted_clf = load_json_from_file("fingerprints_cv.json")
    fpbee.clf = fpbee.load_classifier(fitted_clf)
    return fpbee


@pytest.fixture(scope=session)
def morbee():
    """
    Initiates bee with screened mordred descriptors
    """
    morbee = BMBee(
        data_set_path="clean_mordred_france.csv", mol_path="AllPublicnew.sdf"
    )
    morbee.X_data = morbee.filter_features()
    fitted_clf = load_json_from_file("reduced_mordred_cv.json")
    morbee.clf = morbee.load_classifier(fitted_clf)
    return morbee
