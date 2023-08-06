import hashlib
import inspect
import warnings
import pandas as pd
pandas_version = tuple(map(int, pd.__version__.split('.')[:2]))
_check_pandas_change = False
if pandas_version < (1, 4):

    def _set_noconvert_columns(self):
        assert self.orig_names is not None
        dhdc__rar = {fbv__wfj: ckmn__nksz for ckmn__nksz, fbv__wfj in
            enumerate(self.orig_names)}
        bnz__nmw = [dhdc__rar[fbv__wfj] for fbv__wfj in self.names]
        qeok__vjg = self._set_noconvert_dtype_columns(bnz__nmw, self.names)
        for vvdmr__jgyvj in qeok__vjg:
            self._reader.set_noconvert(vvdmr__jgyvj)
    if _check_pandas_change:
        lines = inspect.getsource(pd.io.parsers.c_parser_wrapper.
            CParserWrapper._set_noconvert_columns)
        if (hashlib.sha256(lines.encode()).hexdigest() !=
            'afc2d738f194e3976cf05d61cb16dc4224b0139451f08a1cf49c578af6f975d3'
            ):
            warnings.warn(
                'pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns has changed'
                )
    (pd.io.parsers.c_parser_wrapper.CParserWrapper._set_noconvert_columns
        ) = _set_noconvert_columns
