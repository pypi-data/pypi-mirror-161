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
            rnuwn__dwa = idx
            yfude__knx = df.data
            uzkq__jxj = df.columns
            xvf__xhqfn = self.replace_range_with_numeric_idx_if_needed(df,
                rnuwn__dwa)
            luwcb__yqde = DataFrameType(yfude__knx, xvf__xhqfn, uzkq__jxj,
                is_table_format=df.is_table_format)
            return luwcb__yqde(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            uypx__ndgi = idx.types[0]
            ljtuc__bnkhc = idx.types[1]
            if isinstance(uypx__ndgi, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(ljtuc__bnkhc):
                    okb__mgqup = get_overload_const_str(ljtuc__bnkhc)
                    if okb__mgqup not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, okb__mgqup))
                    xaww__rfda = df.columns.index(okb__mgqup)
                    return df.data[xaww__rfda].dtype(*args)
                if isinstance(ljtuc__bnkhc, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(uypx__ndgi
                ) and uypx__ndgi.dtype == types.bool_ or isinstance(uypx__ndgi,
                types.SliceType):
                xvf__xhqfn = self.replace_range_with_numeric_idx_if_needed(df,
                    uypx__ndgi)
                if is_overload_constant_str(ljtuc__bnkhc):
                    pqas__miv = get_overload_const_str(ljtuc__bnkhc)
                    if pqas__miv not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {pqas__miv}'
                            )
                    xaww__rfda = df.columns.index(pqas__miv)
                    zkbcg__ink = df.data[xaww__rfda]
                    jifzi__yfpr = zkbcg__ink.dtype
                    cpwlt__lcoqk = types.literal(df.columns[xaww__rfda])
                    luwcb__yqde = bodo.SeriesType(jifzi__yfpr, zkbcg__ink,
                        xvf__xhqfn, cpwlt__lcoqk)
                    return luwcb__yqde(*args)
                if isinstance(ljtuc__bnkhc, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(ljtuc__bnkhc):
                    xxlrc__ppnff = get_overload_const_list(ljtuc__bnkhc)
                    ifl__gjnxb = types.unliteral(ljtuc__bnkhc)
                    if ifl__gjnxb.dtype == types.bool_:
                        if len(df.columns) != len(xxlrc__ppnff):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {xxlrc__ppnff} has {len(xxlrc__ppnff)} values'
                                )
                        mtmb__nixtg = []
                        pbwbr__jbgcq = []
                        for htyfu__djvta in range(len(xxlrc__ppnff)):
                            if xxlrc__ppnff[htyfu__djvta]:
                                mtmb__nixtg.append(df.columns[htyfu__djvta])
                                pbwbr__jbgcq.append(df.data[htyfu__djvta])
                        gzep__asv = tuple()
                        gsjqx__yhyi = df.is_table_format and len(mtmb__nixtg
                            ) > 0 and len(mtmb__nixtg
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        luwcb__yqde = DataFrameType(tuple(pbwbr__jbgcq),
                            xvf__xhqfn, tuple(mtmb__nixtg), is_table_format
                            =gsjqx__yhyi)
                        return luwcb__yqde(*args)
                    elif ifl__gjnxb.dtype == bodo.string_type:
                        gzep__asv, pbwbr__jbgcq = (
                            get_df_getitem_kept_cols_and_data(df, xxlrc__ppnff)
                            )
                        gsjqx__yhyi = df.is_table_format and len(xxlrc__ppnff
                            ) > 0 and len(xxlrc__ppnff
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        luwcb__yqde = DataFrameType(pbwbr__jbgcq,
                            xvf__xhqfn, gzep__asv, is_table_format=gsjqx__yhyi)
                        return luwcb__yqde(*args)
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
                mtmb__nixtg = []
                pbwbr__jbgcq = []
                for htyfu__djvta, pxnn__kgqz in enumerate(df.columns):
                    if pxnn__kgqz[0] != ind_val:
                        continue
                    mtmb__nixtg.append(pxnn__kgqz[1] if len(pxnn__kgqz) == 
                        2 else pxnn__kgqz[1:])
                    pbwbr__jbgcq.append(df.data[htyfu__djvta])
                zkbcg__ink = tuple(pbwbr__jbgcq)
                wba__mexb = df.index
                mmsdw__nuw = tuple(mtmb__nixtg)
                luwcb__yqde = DataFrameType(zkbcg__ink, wba__mexb, mmsdw__nuw)
                return luwcb__yqde(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                xaww__rfda = df.columns.index(ind_val)
                zkbcg__ink = df.data[xaww__rfda]
                jifzi__yfpr = zkbcg__ink.dtype
                wba__mexb = df.index
                cpwlt__lcoqk = types.literal(df.columns[xaww__rfda])
                luwcb__yqde = bodo.SeriesType(jifzi__yfpr, zkbcg__ink,
                    wba__mexb, cpwlt__lcoqk)
                return luwcb__yqde(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            zkbcg__ink = df.data
            wba__mexb = self.replace_range_with_numeric_idx_if_needed(df, ind)
            mmsdw__nuw = df.columns
            luwcb__yqde = DataFrameType(zkbcg__ink, wba__mexb, mmsdw__nuw,
                is_table_format=df.is_table_format)
            return luwcb__yqde(*args)
        elif is_overload_constant_list(ind):
            xsjv__ngyxi = get_overload_const_list(ind)
            mmsdw__nuw, zkbcg__ink = get_df_getitem_kept_cols_and_data(df,
                xsjv__ngyxi)
            wba__mexb = df.index
            gsjqx__yhyi = df.is_table_format and len(xsjv__ngyxi) > 0 and len(
                xsjv__ngyxi) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            luwcb__yqde = DataFrameType(zkbcg__ink, wba__mexb, mmsdw__nuw,
                is_table_format=gsjqx__yhyi)
            return luwcb__yqde(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        xvf__xhqfn = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return xvf__xhqfn


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for aniga__dmlqa in cols_to_keep_list:
        if aniga__dmlqa not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(aniga__dmlqa, df.columns))
    mmsdw__nuw = tuple(cols_to_keep_list)
    zkbcg__ink = tuple(df.data[df.column_index[yjp__ysntn]] for yjp__ysntn in
        mmsdw__nuw)
    return mmsdw__nuw, zkbcg__ink


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
            mtmb__nixtg = []
            pbwbr__jbgcq = []
            for htyfu__djvta, pxnn__kgqz in enumerate(df.columns):
                if pxnn__kgqz[0] != ind_val:
                    continue
                mtmb__nixtg.append(pxnn__kgqz[1] if len(pxnn__kgqz) == 2 else
                    pxnn__kgqz[1:])
                pbwbr__jbgcq.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(htyfu__djvta))
            yrsod__uei = 'def impl(df, ind):\n'
            uurdq__yimxl = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(yrsod__uei,
                mtmb__nixtg, ', '.join(pbwbr__jbgcq), uurdq__yimxl)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        xsjv__ngyxi = get_overload_const_list(ind)
        for aniga__dmlqa in xsjv__ngyxi:
            if aniga__dmlqa not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(aniga__dmlqa, df.columns))
        fmd__ssfvm = None
        if df.is_table_format and len(xsjv__ngyxi) > 0 and len(xsjv__ngyxi
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            miwx__bux = [df.column_index[aniga__dmlqa] for aniga__dmlqa in
                xsjv__ngyxi]
            fmd__ssfvm = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (miwx__bux))}
            pbwbr__jbgcq = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            pbwbr__jbgcq = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[aniga__dmlqa]}).copy()'
                 for aniga__dmlqa in xsjv__ngyxi)
        yrsod__uei = 'def impl(df, ind):\n'
        uurdq__yimxl = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(yrsod__uei,
            xsjv__ngyxi, pbwbr__jbgcq, uurdq__yimxl, extra_globals=fmd__ssfvm)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        yrsod__uei = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            yrsod__uei += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        uurdq__yimxl = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            pbwbr__jbgcq = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            pbwbr__jbgcq = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[aniga__dmlqa]})[ind]'
                 for aniga__dmlqa in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(yrsod__uei, df.
            columns, pbwbr__jbgcq, uurdq__yimxl)
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
        yjp__ysntn = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(yjp__ysntn)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qdc__ysu = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, qdc__ysu)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        viwrf__ondh, = args
        dhdiw__ymh = signature.return_type
        bnh__iywdi = cgutils.create_struct_proxy(dhdiw__ymh)(context, builder)
        bnh__iywdi.obj = viwrf__ondh
        context.nrt.incref(builder, signature.args[0], viwrf__ondh)
        return bnh__iywdi._getvalue()
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
        qvwm__eajg = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            iogxl__dqz = get_overload_const_int(idx.types[1])
            if iogxl__dqz < 0 or iogxl__dqz >= qvwm__eajg:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            lyxtp__acy = [iogxl__dqz]
        else:
            is_out_series = False
            lyxtp__acy = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= qvwm__eajg for
                ind in lyxtp__acy):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[lyxtp__acy])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                iogxl__dqz = lyxtp__acy[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, iogxl__dqz)
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
    yrsod__uei = 'def impl(I, idx):\n'
    yrsod__uei += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        yrsod__uei += f'  idx_t = {idx}\n'
    else:
        yrsod__uei += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    uurdq__yimxl = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    fmd__ssfvm = None
    if df.is_table_format and not is_out_series:
        miwx__bux = [df.column_index[aniga__dmlqa] for aniga__dmlqa in
            col_names]
        fmd__ssfvm = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            miwx__bux))}
        pbwbr__jbgcq = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        pbwbr__jbgcq = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[aniga__dmlqa]})[idx_t]'
             for aniga__dmlqa in col_names)
    if is_out_series:
        qgjj__ctsd = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        yrsod__uei += f"""  return bodo.hiframes.pd_series_ext.init_series({pbwbr__jbgcq}, {uurdq__yimxl}, {qgjj__ctsd})
"""
        oem__mgkcr = {}
        exec(yrsod__uei, {'bodo': bodo}, oem__mgkcr)
        return oem__mgkcr['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(yrsod__uei, col_names,
        pbwbr__jbgcq, uurdq__yimxl, extra_globals=fmd__ssfvm)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    yrsod__uei = 'def impl(I, idx):\n'
    yrsod__uei += '  df = I._obj\n'
    qny__xzln = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[aniga__dmlqa]})[{idx}]'
         for aniga__dmlqa in col_names)
    yrsod__uei += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    yrsod__uei += f"""  return bodo.hiframes.pd_series_ext.init_series(({qny__xzln},), row_idx, None)
"""
    oem__mgkcr = {}
    exec(yrsod__uei, {'bodo': bodo}, oem__mgkcr)
    impl = oem__mgkcr['impl']
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
        yjp__ysntn = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(yjp__ysntn)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qdc__ysu = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, qdc__ysu)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        viwrf__ondh, = args
        heigx__gpc = signature.return_type
        fgdb__ous = cgutils.create_struct_proxy(heigx__gpc)(context, builder)
        fgdb__ous.obj = viwrf__ondh
        context.nrt.incref(builder, signature.args[0], viwrf__ondh)
        return fgdb__ous._getvalue()
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
        yrsod__uei = 'def impl(I, idx):\n'
        yrsod__uei += '  df = I._obj\n'
        yrsod__uei += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        uurdq__yimxl = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            pbwbr__jbgcq = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            pbwbr__jbgcq = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[aniga__dmlqa]})[idx_t]'
                 for aniga__dmlqa in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(yrsod__uei, df.
            columns, pbwbr__jbgcq, uurdq__yimxl)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        xmcf__ecf = idx.types[1]
        if is_overload_constant_str(xmcf__ecf):
            lgeao__iyvdc = get_overload_const_str(xmcf__ecf)
            iogxl__dqz = df.columns.index(lgeao__iyvdc)

            def impl_col_name(I, idx):
                df = I._obj
                uurdq__yimxl = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                iasdq__lqwd = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_data(df, iogxl__dqz))
                return bodo.hiframes.pd_series_ext.init_series(iasdq__lqwd,
                    uurdq__yimxl, lgeao__iyvdc).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(xmcf__ecf):
            col_idx_list = get_overload_const_list(xmcf__ecf)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(aniga__dmlqa in df.
                column_index for aniga__dmlqa in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    lyxtp__acy = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for htyfu__djvta, jfdlq__xvb in enumerate(col_idx_list):
            if jfdlq__xvb:
                lyxtp__acy.append(htyfu__djvta)
                col_names.append(df.columns[htyfu__djvta])
    else:
        col_names = col_idx_list
        lyxtp__acy = [df.column_index[aniga__dmlqa] for aniga__dmlqa in
            col_idx_list]
    fmd__ssfvm = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        fmd__ssfvm = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            lyxtp__acy))}
        pbwbr__jbgcq = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        pbwbr__jbgcq = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in lyxtp__acy)
    uurdq__yimxl = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    yrsod__uei = 'def impl(I, idx):\n'
    yrsod__uei += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(yrsod__uei, col_names,
        pbwbr__jbgcq, uurdq__yimxl, extra_globals=fmd__ssfvm)


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
        yjp__ysntn = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(yjp__ysntn)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qdc__ysu = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, qdc__ysu)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        viwrf__ondh, = args
        oexan__oqof = signature.return_type
        oih__bgqbs = cgutils.create_struct_proxy(oexan__oqof)(context, builder)
        oih__bgqbs.obj = viwrf__ondh
        context.nrt.incref(builder, signature.args[0], viwrf__ondh)
        return oih__bgqbs._getvalue()
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
        iogxl__dqz = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            iasdq__lqwd = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                iogxl__dqz)
            return bodo.utils.conversion.box_if_dt64(iasdq__lqwd[idx[0]])
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
        iogxl__dqz = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[iogxl__dqz]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            iasdq__lqwd = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                iogxl__dqz)
            iasdq__lqwd[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    oih__bgqbs = cgutils.create_struct_proxy(fromty)(context, builder, val)
    nanpw__pfolu = context.cast(builder, oih__bgqbs.obj, fromty.df_type,
        toty.df_type)
    hbv__toud = cgutils.create_struct_proxy(toty)(context, builder)
    hbv__toud.obj = nanpw__pfolu
    return hbv__toud._getvalue()
