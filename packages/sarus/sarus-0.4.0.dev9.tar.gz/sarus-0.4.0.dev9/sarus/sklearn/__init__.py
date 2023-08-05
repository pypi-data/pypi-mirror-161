try:
    from sklearn import *
except ModuleNotFoundError:
    pass


try:
    import sarus.sklearn.cluster as cluster
    import sarus.sklearn.decomposition as decomposition
    import sarus.sklearn.ensemble as ensemble
    import sarus.sklearn.inspection as inspection
    import sarus.sklearn.metrics as metrics
    import sarus.sklearn.model_selection as model_selection
    import sarus.sklearn.preprocessing as preprocessing
    import sarus.sklearn.svm as svm
except NameError:
    pass
