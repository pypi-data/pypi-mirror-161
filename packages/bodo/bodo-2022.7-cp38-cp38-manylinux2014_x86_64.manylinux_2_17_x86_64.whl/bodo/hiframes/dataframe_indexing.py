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
            tvu__sfj = idx
            xrle__kni = df.data
            dve__mijch = df.columns
            nwuv__tpag = self.replace_range_with_numeric_idx_if_needed(df,
                tvu__sfj)
            klmu__vvmaj = DataFrameType(xrle__kni, nwuv__tpag, dve__mijch,
                is_table_format=df.is_table_format)
            return klmu__vvmaj(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            crwjj__ivxdb = idx.types[0]
            qww__psx = idx.types[1]
            if isinstance(crwjj__ivxdb, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(qww__psx):
                    wyzru__prh = get_overload_const_str(qww__psx)
                    if wyzru__prh not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, wyzru__prh))
                    rqlc__oyj = df.columns.index(wyzru__prh)
                    return df.data[rqlc__oyj].dtype(*args)
                if isinstance(qww__psx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(crwjj__ivxdb
                ) and crwjj__ivxdb.dtype == types.bool_ or isinstance(
                crwjj__ivxdb, types.SliceType):
                nwuv__tpag = self.replace_range_with_numeric_idx_if_needed(df,
                    crwjj__ivxdb)
                if is_overload_constant_str(qww__psx):
                    gka__fyiu = get_overload_const_str(qww__psx)
                    if gka__fyiu not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {gka__fyiu}'
                            )
                    rqlc__oyj = df.columns.index(gka__fyiu)
                    dxgfl__xftv = df.data[rqlc__oyj]
                    abtbw__imhml = dxgfl__xftv.dtype
                    emj__vfdym = types.literal(df.columns[rqlc__oyj])
                    klmu__vvmaj = bodo.SeriesType(abtbw__imhml, dxgfl__xftv,
                        nwuv__tpag, emj__vfdym)
                    return klmu__vvmaj(*args)
                if isinstance(qww__psx, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(qww__psx):
                    kzl__nah = get_overload_const_list(qww__psx)
                    efapw__uwup = types.unliteral(qww__psx)
                    if efapw__uwup.dtype == types.bool_:
                        if len(df.columns) != len(kzl__nah):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {kzl__nah} has {len(kzl__nah)} values'
                                )
                        gxiyx__syuq = []
                        usfk__frwp = []
                        for alt__ocor in range(len(kzl__nah)):
                            if kzl__nah[alt__ocor]:
                                gxiyx__syuq.append(df.columns[alt__ocor])
                                usfk__frwp.append(df.data[alt__ocor])
                        tcwxw__fodgp = tuple()
                        ycvi__gsfx = df.is_table_format and len(gxiyx__syuq
                            ) > 0 and len(gxiyx__syuq
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        klmu__vvmaj = DataFrameType(tuple(usfk__frwp),
                            nwuv__tpag, tuple(gxiyx__syuq), is_table_format
                            =ycvi__gsfx)
                        return klmu__vvmaj(*args)
                    elif efapw__uwup.dtype == bodo.string_type:
                        tcwxw__fodgp, usfk__frwp = (
                            get_df_getitem_kept_cols_and_data(df, kzl__nah))
                        ycvi__gsfx = df.is_table_format and len(kzl__nah
                            ) > 0 and len(kzl__nah
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        klmu__vvmaj = DataFrameType(usfk__frwp, nwuv__tpag,
                            tcwxw__fodgp, is_table_format=ycvi__gsfx)
                        return klmu__vvmaj(*args)
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
                gxiyx__syuq = []
                usfk__frwp = []
                for alt__ocor, riyh__wslps in enumerate(df.columns):
                    if riyh__wslps[0] != ind_val:
                        continue
                    gxiyx__syuq.append(riyh__wslps[1] if len(riyh__wslps) ==
                        2 else riyh__wslps[1:])
                    usfk__frwp.append(df.data[alt__ocor])
                dxgfl__xftv = tuple(usfk__frwp)
                nqsbd__vawup = df.index
                rosc__ljqa = tuple(gxiyx__syuq)
                klmu__vvmaj = DataFrameType(dxgfl__xftv, nqsbd__vawup,
                    rosc__ljqa)
                return klmu__vvmaj(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                rqlc__oyj = df.columns.index(ind_val)
                dxgfl__xftv = df.data[rqlc__oyj]
                abtbw__imhml = dxgfl__xftv.dtype
                nqsbd__vawup = df.index
                emj__vfdym = types.literal(df.columns[rqlc__oyj])
                klmu__vvmaj = bodo.SeriesType(abtbw__imhml, dxgfl__xftv,
                    nqsbd__vawup, emj__vfdym)
                return klmu__vvmaj(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            dxgfl__xftv = df.data
            nqsbd__vawup = self.replace_range_with_numeric_idx_if_needed(df,
                ind)
            rosc__ljqa = df.columns
            klmu__vvmaj = DataFrameType(dxgfl__xftv, nqsbd__vawup,
                rosc__ljqa, is_table_format=df.is_table_format)
            return klmu__vvmaj(*args)
        elif is_overload_constant_list(ind):
            glu__nthn = get_overload_const_list(ind)
            rosc__ljqa, dxgfl__xftv = get_df_getitem_kept_cols_and_data(df,
                glu__nthn)
            nqsbd__vawup = df.index
            ycvi__gsfx = df.is_table_format and len(glu__nthn) > 0 and len(
                glu__nthn) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            klmu__vvmaj = DataFrameType(dxgfl__xftv, nqsbd__vawup,
                rosc__ljqa, is_table_format=ycvi__gsfx)
            return klmu__vvmaj(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        nwuv__tpag = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return nwuv__tpag


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for bylg__gth in cols_to_keep_list:
        if bylg__gth not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(bylg__gth, df.columns))
    rosc__ljqa = tuple(cols_to_keep_list)
    dxgfl__xftv = tuple(df.data[df.column_index[ddqlz__eawz]] for
        ddqlz__eawz in rosc__ljqa)
    return rosc__ljqa, dxgfl__xftv


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
            gxiyx__syuq = []
            usfk__frwp = []
            for alt__ocor, riyh__wslps in enumerate(df.columns):
                if riyh__wslps[0] != ind_val:
                    continue
                gxiyx__syuq.append(riyh__wslps[1] if len(riyh__wslps) == 2 else
                    riyh__wslps[1:])
                usfk__frwp.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(alt__ocor))
            gkoop__xbn = 'def impl(df, ind):\n'
            glvq__bvq = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(gkoop__xbn,
                gxiyx__syuq, ', '.join(usfk__frwp), glvq__bvq)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        glu__nthn = get_overload_const_list(ind)
        for bylg__gth in glu__nthn:
            if bylg__gth not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(bylg__gth, df.columns))
        caepq__mses = None
        if df.is_table_format and len(glu__nthn) > 0 and len(glu__nthn
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            kkj__ovxh = [df.column_index[bylg__gth] for bylg__gth in glu__nthn]
            caepq__mses = {'col_nums_meta': bodo.utils.typing.MetaType(
                tuple(kkj__ovxh))}
            usfk__frwp = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            usfk__frwp = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[bylg__gth]}).copy()'
                 for bylg__gth in glu__nthn)
        gkoop__xbn = 'def impl(df, ind):\n'
        glvq__bvq = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(gkoop__xbn,
            glu__nthn, usfk__frwp, glvq__bvq, extra_globals=caepq__mses)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        gkoop__xbn = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            gkoop__xbn += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        glvq__bvq = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            usfk__frwp = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            usfk__frwp = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[bylg__gth]})[ind]'
                 for bylg__gth in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(gkoop__xbn, df.
            columns, usfk__frwp, glvq__bvq)
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
        ddqlz__eawz = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(ddqlz__eawz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vaok__oeg = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, vaok__oeg)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        izavs__yxbck, = args
        nrv__dhl = signature.return_type
        kwxz__chvh = cgutils.create_struct_proxy(nrv__dhl)(context, builder)
        kwxz__chvh.obj = izavs__yxbck
        context.nrt.incref(builder, signature.args[0], izavs__yxbck)
        return kwxz__chvh._getvalue()
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
        mpswm__jxpav = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            jcrwh__bop = get_overload_const_int(idx.types[1])
            if jcrwh__bop < 0 or jcrwh__bop >= mpswm__jxpav:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            qlztq__tacl = [jcrwh__bop]
        else:
            is_out_series = False
            qlztq__tacl = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >=
                mpswm__jxpav for ind in qlztq__tacl):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[qlztq__tacl])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                jcrwh__bop = qlztq__tacl[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, jcrwh__bop)
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
    gkoop__xbn = 'def impl(I, idx):\n'
    gkoop__xbn += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        gkoop__xbn += f'  idx_t = {idx}\n'
    else:
        gkoop__xbn += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    glvq__bvq = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]'
    caepq__mses = None
    if df.is_table_format and not is_out_series:
        kkj__ovxh = [df.column_index[bylg__gth] for bylg__gth in col_names]
        caepq__mses = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            kkj__ovxh))}
        usfk__frwp = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        usfk__frwp = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[bylg__gth]})[idx_t]'
             for bylg__gth in col_names)
    if is_out_series:
        tqs__ring = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        gkoop__xbn += f"""  return bodo.hiframes.pd_series_ext.init_series({usfk__frwp}, {glvq__bvq}, {tqs__ring})
"""
        tcq__oikj = {}
        exec(gkoop__xbn, {'bodo': bodo}, tcq__oikj)
        return tcq__oikj['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(gkoop__xbn, col_names,
        usfk__frwp, glvq__bvq, extra_globals=caepq__mses)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    gkoop__xbn = 'def impl(I, idx):\n'
    gkoop__xbn += '  df = I._obj\n'
    rmkd__qud = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[bylg__gth]})[{idx}]'
         for bylg__gth in col_names)
    gkoop__xbn += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    gkoop__xbn += f"""  return bodo.hiframes.pd_series_ext.init_series(({rmkd__qud},), row_idx, None)
"""
    tcq__oikj = {}
    exec(gkoop__xbn, {'bodo': bodo}, tcq__oikj)
    impl = tcq__oikj['impl']
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
        ddqlz__eawz = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(ddqlz__eawz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vaok__oeg = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, vaok__oeg)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        izavs__yxbck, = args
        fdk__ixw = signature.return_type
        ygjya__vwugb = cgutils.create_struct_proxy(fdk__ixw)(context, builder)
        ygjya__vwugb.obj = izavs__yxbck
        context.nrt.incref(builder, signature.args[0], izavs__yxbck)
        return ygjya__vwugb._getvalue()
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
        gkoop__xbn = 'def impl(I, idx):\n'
        gkoop__xbn += '  df = I._obj\n'
        gkoop__xbn += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        glvq__bvq = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            usfk__frwp = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            usfk__frwp = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[bylg__gth]})[idx_t]'
                 for bylg__gth in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(gkoop__xbn, df.
            columns, usfk__frwp, glvq__bvq)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        zibtc__bnnnk = idx.types[1]
        if is_overload_constant_str(zibtc__bnnnk):
            wmd__rierc = get_overload_const_str(zibtc__bnnnk)
            jcrwh__bop = df.columns.index(wmd__rierc)

            def impl_col_name(I, idx):
                df = I._obj
                glvq__bvq = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
                    df)
                vwct__vcpwm = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_data(df, jcrwh__bop))
                return bodo.hiframes.pd_series_ext.init_series(vwct__vcpwm,
                    glvq__bvq, wmd__rierc).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(zibtc__bnnnk):
            col_idx_list = get_overload_const_list(zibtc__bnnnk)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(bylg__gth in df.column_index for
                bylg__gth in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    qlztq__tacl = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for alt__ocor, lynl__qsca in enumerate(col_idx_list):
            if lynl__qsca:
                qlztq__tacl.append(alt__ocor)
                col_names.append(df.columns[alt__ocor])
    else:
        col_names = col_idx_list
        qlztq__tacl = [df.column_index[bylg__gth] for bylg__gth in col_idx_list
            ]
    caepq__mses = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        caepq__mses = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            qlztq__tacl))}
        usfk__frwp = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        usfk__frwp = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in qlztq__tacl)
    glvq__bvq = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    gkoop__xbn = 'def impl(I, idx):\n'
    gkoop__xbn += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(gkoop__xbn, col_names,
        usfk__frwp, glvq__bvq, extra_globals=caepq__mses)


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
        ddqlz__eawz = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(ddqlz__eawz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vaok__oeg = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, vaok__oeg)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        izavs__yxbck, = args
        gpca__xmb = signature.return_type
        rmiu__ibe = cgutils.create_struct_proxy(gpca__xmb)(context, builder)
        rmiu__ibe.obj = izavs__yxbck
        context.nrt.incref(builder, signature.args[0], izavs__yxbck)
        return rmiu__ibe._getvalue()
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
        jcrwh__bop = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            vwct__vcpwm = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                jcrwh__bop)
            return bodo.utils.conversion.box_if_dt64(vwct__vcpwm[idx[0]])
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
        jcrwh__bop = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[jcrwh__bop]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            vwct__vcpwm = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                jcrwh__bop)
            vwct__vcpwm[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    rmiu__ibe = cgutils.create_struct_proxy(fromty)(context, builder, val)
    xjza__ivpmv = context.cast(builder, rmiu__ibe.obj, fromty.df_type, toty
        .df_type)
    itnlm__qeso = cgutils.create_struct_proxy(toty)(context, builder)
    itnlm__qeso.obj = xjza__ivpmv
    return itnlm__qeso._getvalue()
