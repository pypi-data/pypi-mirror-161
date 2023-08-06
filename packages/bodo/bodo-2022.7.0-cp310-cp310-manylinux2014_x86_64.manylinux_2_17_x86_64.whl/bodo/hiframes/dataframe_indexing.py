"""
Indexing support for pd.DataFrame type.
"""
import operator
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.transform import gen_const_tup
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_list, get_overload_const_str, is_immutable_array, is_list_like_index_type, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, raise_bodo_error


@infer_global(operator.getitem)
class DataFrameGetItemTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        check_runtime_cols_unsupported(args[0], 'DataFrame getitem (df[])')
        if isinstance(args[0], DataFrameType):
            return self.typecheck_df_getitem(args)
        elif isinstance(args[0], DataFrameLocType):
            return self.typecheck_loc_getitem(args)
        else:
            return

    def typecheck_loc_getitem(self, args):
        I = args[0]
        idx = args[1]
        df = I.df_type
        if isinstance(df.columns[0], tuple):
            raise_bodo_error(
                'DataFrame.loc[] getitem (location-based indexing) with multi-indexed columns not supported yet'
                )
        if is_list_like_index_type(idx) and idx.dtype == types.bool_:
            vqfin__fjmfi = idx
            nihnc__uwbe = df.data
            wxqa__ulig = df.columns
            xaj__bpl = self.replace_range_with_numeric_idx_if_needed(df,
                vqfin__fjmfi)
            lfs__wez = DataFrameType(nihnc__uwbe, xaj__bpl, wxqa__ulig,
                is_table_format=df.is_table_format)
            return lfs__wez(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            hehn__itge = idx.types[0]
            zty__tlcys = idx.types[1]
            if isinstance(hehn__itge, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(zty__tlcys):
                    izvtp__ayt = get_overload_const_str(zty__tlcys)
                    if izvtp__ayt not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, izvtp__ayt))
                    olpn__lgjt = df.columns.index(izvtp__ayt)
                    return df.data[olpn__lgjt].dtype(*args)
                if isinstance(zty__tlcys, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(hehn__itge
                ) and hehn__itge.dtype == types.bool_ or isinstance(hehn__itge,
                types.SliceType):
                xaj__bpl = self.replace_range_with_numeric_idx_if_needed(df,
                    hehn__itge)
                if is_overload_constant_str(zty__tlcys):
                    pkhzb__edy = get_overload_const_str(zty__tlcys)
                    if pkhzb__edy not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {pkhzb__edy}'
                            )
                    olpn__lgjt = df.columns.index(pkhzb__edy)
                    lmrkk__jbgyf = df.data[olpn__lgjt]
                    sfgl__ruluz = lmrkk__jbgyf.dtype
                    shusy__kby = types.literal(df.columns[olpn__lgjt])
                    lfs__wez = bodo.SeriesType(sfgl__ruluz, lmrkk__jbgyf,
                        xaj__bpl, shusy__kby)
                    return lfs__wez(*args)
                if isinstance(zty__tlcys, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(zty__tlcys):
                    ocjb__qmug = get_overload_const_list(zty__tlcys)
                    jrvwr__ympzs = types.unliteral(zty__tlcys)
                    if jrvwr__ympzs.dtype == types.bool_:
                        if len(df.columns) != len(ocjb__qmug):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {ocjb__qmug} has {len(ocjb__qmug)} values'
                                )
                        uppb__xqph = []
                        sfvh__ftat = []
                        for vokm__rcsz in range(len(ocjb__qmug)):
                            if ocjb__qmug[vokm__rcsz]:
                                uppb__xqph.append(df.columns[vokm__rcsz])
                                sfvh__ftat.append(df.data[vokm__rcsz])
                        ilct__oxf = tuple()
                        dlxq__qgykk = df.is_table_format and len(uppb__xqph
                            ) > 0 and len(uppb__xqph
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        lfs__wez = DataFrameType(tuple(sfvh__ftat),
                            xaj__bpl, tuple(uppb__xqph), is_table_format=
                            dlxq__qgykk)
                        return lfs__wez(*args)
                    elif jrvwr__ympzs.dtype == bodo.string_type:
                        ilct__oxf, sfvh__ftat = (
                            get_df_getitem_kept_cols_and_data(df, ocjb__qmug))
                        dlxq__qgykk = df.is_table_format and len(ocjb__qmug
                            ) > 0 and len(ocjb__qmug
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        lfs__wez = DataFrameType(sfvh__ftat, xaj__bpl,
                            ilct__oxf, is_table_format=dlxq__qgykk)
                        return lfs__wez(*args)
        raise_bodo_error(
            f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet. If you are trying to select a subset of the columns by passing a list of column names, that list must be a compile time constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def typecheck_df_getitem(self, args):
        df = args[0]
        ind = args[1]
        if is_overload_constant_str(ind) or is_overload_constant_int(ind):
            ind_val = get_overload_const_str(ind) if is_overload_constant_str(
                ind) else get_overload_const_int(ind)
            if isinstance(df.columns[0], tuple):
                uppb__xqph = []
                sfvh__ftat = []
                for vokm__rcsz, ekplz__uky in enumerate(df.columns):
                    if ekplz__uky[0] != ind_val:
                        continue
                    uppb__xqph.append(ekplz__uky[1] if len(ekplz__uky) == 2
                         else ekplz__uky[1:])
                    sfvh__ftat.append(df.data[vokm__rcsz])
                lmrkk__jbgyf = tuple(sfvh__ftat)
                twql__oxb = df.index
                qof__aogy = tuple(uppb__xqph)
                lfs__wez = DataFrameType(lmrkk__jbgyf, twql__oxb, qof__aogy)
                return lfs__wez(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                olpn__lgjt = df.columns.index(ind_val)
                lmrkk__jbgyf = df.data[olpn__lgjt]
                sfgl__ruluz = lmrkk__jbgyf.dtype
                twql__oxb = df.index
                shusy__kby = types.literal(df.columns[olpn__lgjt])
                lfs__wez = bodo.SeriesType(sfgl__ruluz, lmrkk__jbgyf,
                    twql__oxb, shusy__kby)
                return lfs__wez(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            lmrkk__jbgyf = df.data
            twql__oxb = self.replace_range_with_numeric_idx_if_needed(df, ind)
            qof__aogy = df.columns
            lfs__wez = DataFrameType(lmrkk__jbgyf, twql__oxb, qof__aogy,
                is_table_format=df.is_table_format)
            return lfs__wez(*args)
        elif is_overload_constant_list(ind):
            zzngk__ant = get_overload_const_list(ind)
            qof__aogy, lmrkk__jbgyf = get_df_getitem_kept_cols_and_data(df,
                zzngk__ant)
            twql__oxb = df.index
            dlxq__qgykk = df.is_table_format and len(zzngk__ant) > 0 and len(
                zzngk__ant) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            lfs__wez = DataFrameType(lmrkk__jbgyf, twql__oxb, qof__aogy,
                is_table_format=dlxq__qgykk)
            return lfs__wez(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        xaj__bpl = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64,
            df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return xaj__bpl


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for dths__mougj in cols_to_keep_list:
        if dths__mougj not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(dths__mougj, df.columns))
    qof__aogy = tuple(cols_to_keep_list)
    lmrkk__jbgyf = tuple(df.data[df.column_index[xckp__xorme]] for
        xckp__xorme in qof__aogy)
    return qof__aogy, lmrkk__jbgyf


@lower_builtin(operator.getitem, DataFrameType, types.Any)
def getitem_df_lower(context, builder, sig, args):
    impl = df_getitem_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_getitem_overload(df, ind):
    if not isinstance(df, DataFrameType):
        return
    if is_overload_constant_str(ind) or is_overload_constant_int(ind):
        ind_val = get_overload_const_str(ind) if is_overload_constant_str(ind
            ) else get_overload_const_int(ind)
        if isinstance(df.columns[0], tuple):
            uppb__xqph = []
            sfvh__ftat = []
            for vokm__rcsz, ekplz__uky in enumerate(df.columns):
                if ekplz__uky[0] != ind_val:
                    continue
                uppb__xqph.append(ekplz__uky[1] if len(ekplz__uky) == 2 else
                    ekplz__uky[1:])
                sfvh__ftat.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(vokm__rcsz))
            dqj__rpqk = 'def impl(df, ind):\n'
            hprwp__vlg = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(dqj__rpqk,
                uppb__xqph, ', '.join(sfvh__ftat), hprwp__vlg)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        zzngk__ant = get_overload_const_list(ind)
        for dths__mougj in zzngk__ant:
            if dths__mougj not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(dths__mougj, df.columns))
        aavwq__cgzvv = None
        if df.is_table_format and len(zzngk__ant) > 0 and len(zzngk__ant
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            vjgb__sxk = [df.column_index[dths__mougj] for dths__mougj in
                zzngk__ant]
            aavwq__cgzvv = {'col_nums_meta': bodo.utils.typing.MetaType(
                tuple(vjgb__sxk))}
            sfvh__ftat = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            sfvh__ftat = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[dths__mougj]}).copy()'
                 for dths__mougj in zzngk__ant)
        dqj__rpqk = 'def impl(df, ind):\n'
        hprwp__vlg = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(dqj__rpqk,
            zzngk__ant, sfvh__ftat, hprwp__vlg, extra_globals=aavwq__cgzvv)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        dqj__rpqk = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            dqj__rpqk += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        hprwp__vlg = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            sfvh__ftat = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            sfvh__ftat = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[dths__mougj]})[ind]'
                 for dths__mougj in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(dqj__rpqk, df.
            columns, sfvh__ftat, hprwp__vlg)
    raise_bodo_error('df[] getitem using {} not supported'.format(ind))


@overload(operator.setitem, no_unliteral=True)
def df_setitem_overload(df, idx, val):
    check_runtime_cols_unsupported(df, 'DataFrame setitem (df[])')
    if not isinstance(df, DataFrameType):
        return
    raise_bodo_error('DataFrame setitem: transform necessary')


class DataFrameILocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        xckp__xorme = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(xckp__xorme)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mcdf__vpun = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, mcdf__vpun)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        xpxna__thl, = args
        fhoj__yosx = signature.return_type
        uiuf__pfyq = cgutils.create_struct_proxy(fhoj__yosx)(context, builder)
        uiuf__pfyq.obj = xpxna__thl
        context.nrt.incref(builder, signature.args[0], xpxna__thl)
        return uiuf__pfyq._getvalue()
    return DataFrameILocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iloc')
def overload_dataframe_iloc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iloc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iloc(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iloc_getitem(I, idx):
    if not isinstance(I, DataFrameILocType):
        return
    df = I.df_type
    if isinstance(idx, types.Integer):
        return _gen_iloc_getitem_row_impl(df, df.columns, 'idx')
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and not isinstance(
        idx[1], types.SliceType):
        if not (is_overload_constant_list(idx.types[1]) or
            is_overload_constant_int(idx.types[1])):
            raise_bodo_error(
                'idx2 in df.iloc[idx1, idx2] should be a constant integer or constant list of integers. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        jed__sioti = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            rljap__jwh = get_overload_const_int(idx.types[1])
            if rljap__jwh < 0 or rljap__jwh >= jed__sioti:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            tjmj__ihblb = [rljap__jwh]
        else:
            is_out_series = False
            tjmj__ihblb = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= jed__sioti for
                ind in tjmj__ihblb):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[tjmj__ihblb])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                rljap__jwh = tjmj__ihblb[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, rljap__jwh)
                        [idx[0]])
                return impl
            return _gen_iloc_getitem_row_impl(df, col_names, 'idx[0]')
        if is_list_like_index_type(idx.types[0]) and isinstance(idx.types[0
            ].dtype, (types.Integer, types.Boolean)) or isinstance(idx.
            types[0], types.SliceType):
            return _gen_iloc_getitem_bool_slice_impl(df, col_names, idx.
                types[0], 'idx[0]', is_out_series)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
        Integer, types.Boolean)) or isinstance(idx, types.SliceType):
        return _gen_iloc_getitem_bool_slice_impl(df, df.columns, idx, 'idx',
            False)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):
        raise_bodo_error(
            'slice2 in df.iloc[slice1,slice2] should be constant. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )
    raise_bodo_error(f'df.iloc[] getitem using {idx} not supported')


def _gen_iloc_getitem_bool_slice_impl(df, col_names, idx_typ, idx,
    is_out_series):
    dqj__rpqk = 'def impl(I, idx):\n'
    dqj__rpqk += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        dqj__rpqk += f'  idx_t = {idx}\n'
    else:
        dqj__rpqk += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    hprwp__vlg = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    aavwq__cgzvv = None
    if df.is_table_format and not is_out_series:
        vjgb__sxk = [df.column_index[dths__mougj] for dths__mougj in col_names]
        aavwq__cgzvv = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            vjgb__sxk))}
        sfvh__ftat = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        sfvh__ftat = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[dths__mougj]})[idx_t]'
             for dths__mougj in col_names)
    if is_out_series:
        vfo__kre = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        dqj__rpqk += f"""  return bodo.hiframes.pd_series_ext.init_series({sfvh__ftat}, {hprwp__vlg}, {vfo__kre})
"""
        ycpu__dwy = {}
        exec(dqj__rpqk, {'bodo': bodo}, ycpu__dwy)
        return ycpu__dwy['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(dqj__rpqk, col_names,
        sfvh__ftat, hprwp__vlg, extra_globals=aavwq__cgzvv)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    dqj__rpqk = 'def impl(I, idx):\n'
    dqj__rpqk += '  df = I._obj\n'
    nrvpw__cjeml = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[dths__mougj]})[{idx}]'
         for dths__mougj in col_names)
    dqj__rpqk += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    dqj__rpqk += f"""  return bodo.hiframes.pd_series_ext.init_series(({nrvpw__cjeml},), row_idx, None)
"""
    ycpu__dwy = {}
    exec(dqj__rpqk, {'bodo': bodo}, ycpu__dwy)
    impl = ycpu__dwy['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def df_iloc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameILocType):
        return
    raise_bodo_error(
        f'DataFrame.iloc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameLocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        xckp__xorme = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(xckp__xorme)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mcdf__vpun = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, mcdf__vpun)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        xpxna__thl, = args
        yuf__jhnc = signature.return_type
        qrwyz__sxo = cgutils.create_struct_proxy(yuf__jhnc)(context, builder)
        qrwyz__sxo.obj = xpxna__thl
        context.nrt.incref(builder, signature.args[0], xpxna__thl)
        return qrwyz__sxo._getvalue()
    return DataFrameLocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'loc')
def overload_dataframe_loc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.loc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_loc(df)


@lower_builtin(operator.getitem, DataFrameLocType, types.Any)
def loc_getitem_lower(context, builder, sig, args):
    impl = overload_loc_getitem(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def overload_loc_getitem(I, idx):
    if not isinstance(I, DataFrameLocType):
        return
    df = I.df_type
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        dqj__rpqk = 'def impl(I, idx):\n'
        dqj__rpqk += '  df = I._obj\n'
        dqj__rpqk += '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n'
        hprwp__vlg = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            sfvh__ftat = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            sfvh__ftat = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[dths__mougj]})[idx_t]'
                 for dths__mougj in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(dqj__rpqk, df.
            columns, sfvh__ftat, hprwp__vlg)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        inn__jeu = idx.types[1]
        if is_overload_constant_str(inn__jeu):
            khcj__bqjg = get_overload_const_str(inn__jeu)
            rljap__jwh = df.columns.index(khcj__bqjg)

            def impl_col_name(I, idx):
                df = I._obj
                hprwp__vlg = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                tfly__xut = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, rljap__jwh)
                return bodo.hiframes.pd_series_ext.init_series(tfly__xut,
                    hprwp__vlg, khcj__bqjg).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(inn__jeu):
            col_idx_list = get_overload_const_list(inn__jeu)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(dths__mougj in df.column_index for
                dths__mougj in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    tjmj__ihblb = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for vokm__rcsz, vmxcu__kxf in enumerate(col_idx_list):
            if vmxcu__kxf:
                tjmj__ihblb.append(vokm__rcsz)
                col_names.append(df.columns[vokm__rcsz])
    else:
        col_names = col_idx_list
        tjmj__ihblb = [df.column_index[dths__mougj] for dths__mougj in
            col_idx_list]
    aavwq__cgzvv = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        aavwq__cgzvv = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            tjmj__ihblb))}
        sfvh__ftat = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        sfvh__ftat = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in tjmj__ihblb)
    hprwp__vlg = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    dqj__rpqk = 'def impl(I, idx):\n'
    dqj__rpqk += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(dqj__rpqk, col_names,
        sfvh__ftat, hprwp__vlg, extra_globals=aavwq__cgzvv)


@overload(operator.setitem, no_unliteral=True)
def df_loc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameLocType):
        return
    raise_bodo_error(
        f'DataFrame.loc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameIatType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        xckp__xorme = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(xckp__xorme)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mcdf__vpun = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, mcdf__vpun)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        xpxna__thl, = args
        yyl__pvwiv = signature.return_type
        qvql__ump = cgutils.create_struct_proxy(yyl__pvwiv)(context, builder)
        qvql__ump.obj = xpxna__thl
        context.nrt.incref(builder, signature.args[0], xpxna__thl)
        return qvql__ump._getvalue()
    return DataFrameIatType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iat')
def overload_dataframe_iat(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iat')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iat(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iat_getitem(I, idx):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat getitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        rljap__jwh = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            tfly__xut = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                rljap__jwh)
            return bodo.utils.conversion.box_if_dt64(tfly__xut[idx[0]])
        return impl_col_ind
    raise BodoError('df.iat[] getitem using {} not supported'.format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_iat_setitem(I, idx, val):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat setitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        rljap__jwh = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[rljap__jwh]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            tfly__xut = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                rljap__jwh)
            tfly__xut[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    qvql__ump = cgutils.create_struct_proxy(fromty)(context, builder, val)
    fzp__gcw = context.cast(builder, qvql__ump.obj, fromty.df_type, toty.
        df_type)
    qao__tjlvx = cgutils.create_struct_proxy(toty)(context, builder)
    qao__tjlvx.obj = fzp__gcw
    return qao__tjlvx._getvalue()
