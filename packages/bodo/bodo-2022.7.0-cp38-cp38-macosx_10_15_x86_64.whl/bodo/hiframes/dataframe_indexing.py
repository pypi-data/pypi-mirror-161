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
            gonv__drthw = idx
            aeq__wabob = df.data
            lil__tyjqu = df.columns
            kdem__cuacz = self.replace_range_with_numeric_idx_if_needed(df,
                gonv__drthw)
            szjn__piobw = DataFrameType(aeq__wabob, kdem__cuacz, lil__tyjqu,
                is_table_format=df.is_table_format)
            return szjn__piobw(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            azl__ecfse = idx.types[0]
            stbkr__fooz = idx.types[1]
            if isinstance(azl__ecfse, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(stbkr__fooz):
                    dwaut__zgw = get_overload_const_str(stbkr__fooz)
                    if dwaut__zgw not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, dwaut__zgw))
                    utv__ipgj = df.columns.index(dwaut__zgw)
                    return df.data[utv__ipgj].dtype(*args)
                if isinstance(stbkr__fooz, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(azl__ecfse
                ) and azl__ecfse.dtype == types.bool_ or isinstance(azl__ecfse,
                types.SliceType):
                kdem__cuacz = self.replace_range_with_numeric_idx_if_needed(df,
                    azl__ecfse)
                if is_overload_constant_str(stbkr__fooz):
                    efvev__mfpfw = get_overload_const_str(stbkr__fooz)
                    if efvev__mfpfw not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {efvev__mfpfw}'
                            )
                    utv__ipgj = df.columns.index(efvev__mfpfw)
                    xwib__beywa = df.data[utv__ipgj]
                    fbamf__fbdmk = xwib__beywa.dtype
                    ihic__cwqtt = types.literal(df.columns[utv__ipgj])
                    szjn__piobw = bodo.SeriesType(fbamf__fbdmk, xwib__beywa,
                        kdem__cuacz, ihic__cwqtt)
                    return szjn__piobw(*args)
                if isinstance(stbkr__fooz, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(stbkr__fooz):
                    kfc__gsc = get_overload_const_list(stbkr__fooz)
                    fufv__fjr = types.unliteral(stbkr__fooz)
                    if fufv__fjr.dtype == types.bool_:
                        if len(df.columns) != len(kfc__gsc):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {kfc__gsc} has {len(kfc__gsc)} values'
                                )
                        olcx__ddp = []
                        jes__bzc = []
                        for mnbi__yjlcv in range(len(kfc__gsc)):
                            if kfc__gsc[mnbi__yjlcv]:
                                olcx__ddp.append(df.columns[mnbi__yjlcv])
                                jes__bzc.append(df.data[mnbi__yjlcv])
                        jmul__nob = tuple()
                        zlj__ihyqx = df.is_table_format and len(olcx__ddp
                            ) > 0 and len(olcx__ddp
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        szjn__piobw = DataFrameType(tuple(jes__bzc),
                            kdem__cuacz, tuple(olcx__ddp), is_table_format=
                            zlj__ihyqx)
                        return szjn__piobw(*args)
                    elif fufv__fjr.dtype == bodo.string_type:
                        jmul__nob, jes__bzc = (
                            get_df_getitem_kept_cols_and_data(df, kfc__gsc))
                        zlj__ihyqx = df.is_table_format and len(kfc__gsc
                            ) > 0 and len(kfc__gsc
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        szjn__piobw = DataFrameType(jes__bzc, kdem__cuacz,
                            jmul__nob, is_table_format=zlj__ihyqx)
                        return szjn__piobw(*args)
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
                olcx__ddp = []
                jes__bzc = []
                for mnbi__yjlcv, ohi__gwve in enumerate(df.columns):
                    if ohi__gwve[0] != ind_val:
                        continue
                    olcx__ddp.append(ohi__gwve[1] if len(ohi__gwve) == 2 else
                        ohi__gwve[1:])
                    jes__bzc.append(df.data[mnbi__yjlcv])
                xwib__beywa = tuple(jes__bzc)
                pixad__wtnfb = df.index
                skj__oukga = tuple(olcx__ddp)
                szjn__piobw = DataFrameType(xwib__beywa, pixad__wtnfb,
                    skj__oukga)
                return szjn__piobw(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                utv__ipgj = df.columns.index(ind_val)
                xwib__beywa = df.data[utv__ipgj]
                fbamf__fbdmk = xwib__beywa.dtype
                pixad__wtnfb = df.index
                ihic__cwqtt = types.literal(df.columns[utv__ipgj])
                szjn__piobw = bodo.SeriesType(fbamf__fbdmk, xwib__beywa,
                    pixad__wtnfb, ihic__cwqtt)
                return szjn__piobw(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            xwib__beywa = df.data
            pixad__wtnfb = self.replace_range_with_numeric_idx_if_needed(df,
                ind)
            skj__oukga = df.columns
            szjn__piobw = DataFrameType(xwib__beywa, pixad__wtnfb,
                skj__oukga, is_table_format=df.is_table_format)
            return szjn__piobw(*args)
        elif is_overload_constant_list(ind):
            otx__ugyq = get_overload_const_list(ind)
            skj__oukga, xwib__beywa = get_df_getitem_kept_cols_and_data(df,
                otx__ugyq)
            pixad__wtnfb = df.index
            zlj__ihyqx = df.is_table_format and len(otx__ugyq) > 0 and len(
                otx__ugyq) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            szjn__piobw = DataFrameType(xwib__beywa, pixad__wtnfb,
                skj__oukga, is_table_format=zlj__ihyqx)
            return szjn__piobw(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        kdem__cuacz = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return kdem__cuacz


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for ynra__labwt in cols_to_keep_list:
        if ynra__labwt not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(ynra__labwt, df.columns))
    skj__oukga = tuple(cols_to_keep_list)
    xwib__beywa = tuple(df.data[df.column_index[gnryb__hdzxb]] for
        gnryb__hdzxb in skj__oukga)
    return skj__oukga, xwib__beywa


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
            olcx__ddp = []
            jes__bzc = []
            for mnbi__yjlcv, ohi__gwve in enumerate(df.columns):
                if ohi__gwve[0] != ind_val:
                    continue
                olcx__ddp.append(ohi__gwve[1] if len(ohi__gwve) == 2 else
                    ohi__gwve[1:])
                jes__bzc.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(mnbi__yjlcv))
            qpiy__vuue = 'def impl(df, ind):\n'
            trcxf__tkce = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(qpiy__vuue,
                olcx__ddp, ', '.join(jes__bzc), trcxf__tkce)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        otx__ugyq = get_overload_const_list(ind)
        for ynra__labwt in otx__ugyq:
            if ynra__labwt not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(ynra__labwt, df.columns))
        hrppf__sfkch = None
        if df.is_table_format and len(otx__ugyq) > 0 and len(otx__ugyq
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            vpktm__eonaw = [df.column_index[ynra__labwt] for ynra__labwt in
                otx__ugyq]
            hrppf__sfkch = {'col_nums_meta': bodo.utils.typing.MetaType(
                tuple(vpktm__eonaw))}
            jes__bzc = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            jes__bzc = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ynra__labwt]}).copy()'
                 for ynra__labwt in otx__ugyq)
        qpiy__vuue = 'def impl(df, ind):\n'
        trcxf__tkce = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(qpiy__vuue,
            otx__ugyq, jes__bzc, trcxf__tkce, extra_globals=hrppf__sfkch)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        qpiy__vuue = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            qpiy__vuue += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        trcxf__tkce = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            jes__bzc = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            jes__bzc = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ynra__labwt]})[ind]'
                 for ynra__labwt in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(qpiy__vuue, df.
            columns, jes__bzc, trcxf__tkce)
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
        gnryb__hdzxb = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(gnryb__hdzxb)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rwaq__hcamh = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, rwaq__hcamh)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        pzf__jiyu, = args
        qvz__qgyky = signature.return_type
        lsour__gzd = cgutils.create_struct_proxy(qvz__qgyky)(context, builder)
        lsour__gzd.obj = pzf__jiyu
        context.nrt.incref(builder, signature.args[0], pzf__jiyu)
        return lsour__gzd._getvalue()
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
        fkdh__kvrv = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            cqzj__saxsy = get_overload_const_int(idx.types[1])
            if cqzj__saxsy < 0 or cqzj__saxsy >= fkdh__kvrv:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            nyma__yzchl = [cqzj__saxsy]
        else:
            is_out_series = False
            nyma__yzchl = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= fkdh__kvrv for
                ind in nyma__yzchl):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[nyma__yzchl])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                cqzj__saxsy = nyma__yzchl[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, cqzj__saxsy
                        )[idx[0]])
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
    qpiy__vuue = 'def impl(I, idx):\n'
    qpiy__vuue += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        qpiy__vuue += f'  idx_t = {idx}\n'
    else:
        qpiy__vuue += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    trcxf__tkce = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    hrppf__sfkch = None
    if df.is_table_format and not is_out_series:
        vpktm__eonaw = [df.column_index[ynra__labwt] for ynra__labwt in
            col_names]
        hrppf__sfkch = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            vpktm__eonaw))}
        jes__bzc = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        jes__bzc = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ynra__labwt]})[idx_t]'
             for ynra__labwt in col_names)
    if is_out_series:
        ejtwc__fqzfg = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        qpiy__vuue += f"""  return bodo.hiframes.pd_series_ext.init_series({jes__bzc}, {trcxf__tkce}, {ejtwc__fqzfg})
"""
        lcir__bryri = {}
        exec(qpiy__vuue, {'bodo': bodo}, lcir__bryri)
        return lcir__bryri['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(qpiy__vuue, col_names,
        jes__bzc, trcxf__tkce, extra_globals=hrppf__sfkch)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    qpiy__vuue = 'def impl(I, idx):\n'
    qpiy__vuue += '  df = I._obj\n'
    txb__izfe = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ynra__labwt]})[{idx}]'
         for ynra__labwt in col_names)
    qpiy__vuue += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    qpiy__vuue += f"""  return bodo.hiframes.pd_series_ext.init_series(({txb__izfe},), row_idx, None)
"""
    lcir__bryri = {}
    exec(qpiy__vuue, {'bodo': bodo}, lcir__bryri)
    impl = lcir__bryri['impl']
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
        gnryb__hdzxb = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(gnryb__hdzxb)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rwaq__hcamh = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, rwaq__hcamh)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        pzf__jiyu, = args
        souii__yscyz = signature.return_type
        kld__yax = cgutils.create_struct_proxy(souii__yscyz)(context, builder)
        kld__yax.obj = pzf__jiyu
        context.nrt.incref(builder, signature.args[0], pzf__jiyu)
        return kld__yax._getvalue()
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
        qpiy__vuue = 'def impl(I, idx):\n'
        qpiy__vuue += '  df = I._obj\n'
        qpiy__vuue += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        trcxf__tkce = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            jes__bzc = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            jes__bzc = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ynra__labwt]})[idx_t]'
                 for ynra__labwt in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(qpiy__vuue, df.
            columns, jes__bzc, trcxf__tkce)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        yboqn__get = idx.types[1]
        if is_overload_constant_str(yboqn__get):
            kkt__euc = get_overload_const_str(yboqn__get)
            cqzj__saxsy = df.columns.index(kkt__euc)

            def impl_col_name(I, idx):
                df = I._obj
                trcxf__tkce = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                ahjh__hnfo = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, cqzj__saxsy)
                return bodo.hiframes.pd_series_ext.init_series(ahjh__hnfo,
                    trcxf__tkce, kkt__euc).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(yboqn__get):
            col_idx_list = get_overload_const_list(yboqn__get)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(ynra__labwt in df.column_index for
                ynra__labwt in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    nyma__yzchl = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for mnbi__yjlcv, tjdsi__slx in enumerate(col_idx_list):
            if tjdsi__slx:
                nyma__yzchl.append(mnbi__yjlcv)
                col_names.append(df.columns[mnbi__yjlcv])
    else:
        col_names = col_idx_list
        nyma__yzchl = [df.column_index[ynra__labwt] for ynra__labwt in
            col_idx_list]
    hrppf__sfkch = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        hrppf__sfkch = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            nyma__yzchl))}
        jes__bzc = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        jes__bzc = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in nyma__yzchl)
    trcxf__tkce = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    qpiy__vuue = 'def impl(I, idx):\n'
    qpiy__vuue += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(qpiy__vuue, col_names,
        jes__bzc, trcxf__tkce, extra_globals=hrppf__sfkch)


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
        gnryb__hdzxb = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(gnryb__hdzxb)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rwaq__hcamh = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, rwaq__hcamh)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        pzf__jiyu, = args
        gxzrk__stvs = signature.return_type
        yuzuq__xwaf = cgutils.create_struct_proxy(gxzrk__stvs)(context, builder
            )
        yuzuq__xwaf.obj = pzf__jiyu
        context.nrt.incref(builder, signature.args[0], pzf__jiyu)
        return yuzuq__xwaf._getvalue()
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
        cqzj__saxsy = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            ahjh__hnfo = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                cqzj__saxsy)
            return bodo.utils.conversion.box_if_dt64(ahjh__hnfo[idx[0]])
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
        cqzj__saxsy = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[cqzj__saxsy]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            ahjh__hnfo = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                cqzj__saxsy)
            ahjh__hnfo[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    yuzuq__xwaf = cgutils.create_struct_proxy(fromty)(context, builder, val)
    acgi__ruj = context.cast(builder, yuzuq__xwaf.obj, fromty.df_type, toty
        .df_type)
    peepm__obgr = cgutils.create_struct_proxy(toty)(context, builder)
    peepm__obgr.obj = acgi__ruj
    return peepm__obgr._getvalue()
