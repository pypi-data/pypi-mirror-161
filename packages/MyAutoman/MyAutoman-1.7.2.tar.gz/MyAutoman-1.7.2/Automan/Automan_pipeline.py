from sklearn.pipeline import Pipeline
from sklearn.utils import _print_elapsed_time
from Automan.Automan_data_prep import get_orgin_ls
import pandas as pd


class AM_Pipeline(Pipeline):
    """特征工程流水线模块

    Parameters
    ----------
    steps : list
        按顺序连接的元组列表,格式为（用户定义的Transformer名称、Transformer对象）。
    col_x: list
        输入字段列表
    feature_map:None or pd.DataFrame()
        特征图配置表,默认None,当为None时桂根据col_x生成，或者用户也可以传入特征表格
    verbose: bool
        日志输出开关，默认False
    orgin_ls_sup: List or None
        补充特征列表，默认None，推理过程中需要的特征列表，col_new对应的orgin_ls中额外补充该列表中的字段，
        例如，当使用XimputeTransformer自填婚姻和推理婚姻进行特定的规则转换时，需要将自填婚姻配置在该列表中

    Attributes
    ----------
    col_new:list
        输出返回特征列表
    orgin_ls:list
        返回特征列表对应的原始特征列表

    """

    def __init__(self, steps, col_x, feature_map=None, verbose=False, orgin_ls_sup=None):
        self.steps = steps
        self.col_x = col_x
        self.verbose = verbose
        self._validate_steps()
        self.col_new = []
        self.orgin_ls_sup = orgin_ls_sup
        if feature_map is not None:
            self.feature_map = feature_map
        else:
            self.feature_map = pd.DataFrame(zip(self.col_x, self.col_x, [0] * len(self.col_x)),
                                            columns=['variable', 'relyon', 'type'])
        if self.orgin_ls_sup:
            if not isinstance(self.orgin_ls_sup,list):
                raise TypeError("orgin_ls_sup must be list")

    def _validate_steps(self):
        names, estimators = zip(*self.steps)

        # validate names
        self._validate_names(names)

        # validate estimators
        transformers = estimators

        for t in transformers:
            if (not (hasattr(t, "fit") or hasattr(t, "fit_transform")) or not
                    hasattr(t, "transform")):
                raise TypeError("All intermediate steps should be "
                                "transformers and implement fit and transform "
                                "or be the string 'passthrough' "
                                "'%s' (type %s) doesn't" % (t, type(t)))

    def _fit(self, X, y=None, **fit_params):
        # shallow copy of steps - this should really be steps_
        self.steps = list(self.steps)
        self._validate_steps()

        fit_params_steps = {name: {} for name, step in self.steps
                            if step is not None}
        for pname, pval in fit_params.items():
            if '__' not in pname:
                raise ValueError(
                    "Pipeline.fit does not accept the {} parameter. "
                    "You can pass parameters to specific steps of your "
                    "pipeline using the stepname__parameter format, e.g. "
                    "`Pipeline.fit(X, y, logisticregression__sample_weight"
                    "=sample_weight)`.".format(pname))
            step, param = pname.split('__', 1)
            fit_params_steps[step][param] = pval

        for (step_idx,
             name,
             transformer) in self._iter(with_final=True,
                                        filter_passthrough=False):
        # for (step_idx,st) in enumerate(self.steps):
        #     name, transformer = st
        #     print("^^^^",step_idx,
        #      name,
        #      transformer)
            message_clsname = 'Pipeline',
            message=self._log_message(step_idx),
            # print("message=",message)
            with _print_elapsed_time(message_clsname, message):
                print(step_idx)
                if step_idx == 0:
                    transformer.col_x = self.col_x[:]
                    transformer.feature_map = self.feature_map.copy(deep=True)
                    X = transformer.fit_transform(X, y)
                    # print("transformer.col_new",transformer.col_new)
                else:
                    # print(f"step {step_idx} col_new:",self.steps[step_idx - 1][1].col_new)
                    transformer.col_x = self.steps[step_idx - 1][1].col_new[:]
                    transformer.feature_map = self.steps[step_idx - 1][1].feature_map.copy(deep=True)
                    X = transformer.fit_transform(X, y)
                    # print("!!! transformer.col_new",transformer.col_new)
        self.col_new = self[-1].col_new[:]
        # print(f"step final col_new:",self.col_new)
        self.feature_map = self[-1].feature_map.copy(deep=True)
        self.orgin_ls = get_orgin_ls(self.col_new, self.feature_map)
        if self.orgin_ls_sup:
            for sup in self.orgin_ls_sup:
                if sup not in self.orgin_ls:
                    self.orgin_ls.append(sup)
        return X, {}

    def fit(self, X, y=None, **fit_params):
        self._fit(X, y, **fit_params)
        return self

    def fit_transform(self, X, y=None, **fit_params):
        Xt, fit_params = self._fit(X, y, **fit_params)
        return Xt

    def predict(self, X, **predict_params):
        pass

    def fit_predict(self, X, y=None, **fit_params):
        pass

    def transform(self, X):
        Xt = X
        for _, _, transform in self._iter():
            Xt = transform.transform(Xt)
        return Xt

    def __getitem__(self, ind):
        """Returns a sub-pipeline or a single esimtator in the pipeline

        Indexing with an integer will return an estimator; using a slice
        returns another Pipeline instance which copies a slice of this
        Pipeline. This copy is shallow: modifying (or fitting) estimators in
        the sub-pipeline will affect the larger pipeline and vice-versa.
        However, replacing a value in `step` will not affect a copy.
        """
        if isinstance(ind, slice):
            return self.__class__(
                steps=self.steps[ind],
                col_x=self.col_x,
                feature_map=self.feature_map,
                verbose=self.verbose
            )
        try:
            name, est = self.steps[ind]
        except TypeError:
            # Not an int, try get step by name
            return self.named_steps[ind]
        return est
