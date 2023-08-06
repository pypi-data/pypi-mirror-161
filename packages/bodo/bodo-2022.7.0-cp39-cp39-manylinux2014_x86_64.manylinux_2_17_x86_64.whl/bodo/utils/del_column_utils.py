"""Helper information to keep table column deletion
pass organized. This contains information about all
table operations for optimizations.
"""
from typing import Dict, Tuple
from numba.core import ir, types
from bodo.hiframes.table import TableType
table_usecol_funcs = {('get_table_data', 'bodo.hiframes.table'), (
    'table_filter', 'bodo.hiframes.table'), ('table_subset',
    'bodo.hiframes.table'), ('set_table_data', 'bodo.hiframes.table'), (
    'set_table_data_null', 'bodo.hiframes.table'), (
    'generate_mappable_table_func', 'bodo.utils.table_utils'), (
    'table_astype', 'bodo.utils.table_utils'), ('generate_table_nbytes',
    'bodo.utils.table_utils'), ('table_concat', 'bodo.utils.table_utils'),
    ('py_data_to_cpp_table', 'bodo.libs.array'), ('logical_table_to_table',
    'bodo.hiframes.table')}


def is_table_use_column_ops(fdef: Tuple[str, str], args, typemap):
    return fdef in table_usecol_funcs and len(args) > 0 and isinstance(typemap
        [args[0].name], TableType)


def get_table_used_columns(fdef: Tuple[str, str], call_expr: ir.Expr,
    typemap: Dict[str, types.Type]):
    if fdef == ('get_table_data', 'bodo.hiframes.table'):
        lmsx__iqf = typemap[call_expr.args[1].name].literal_value
        return {lmsx__iqf}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        oqfru__xkzp = dict(call_expr.kws)
        if 'used_cols' in oqfru__xkzp:
            zlu__pjzc = oqfru__xkzp['used_cols']
            moz__dkn = typemap[zlu__pjzc.name]
            moz__dkn = moz__dkn.instance_type
            return set(moz__dkn.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        zlu__pjzc = call_expr.args[1]
        moz__dkn = typemap[zlu__pjzc.name]
        moz__dkn = moz__dkn.instance_type
        return set(moz__dkn.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        xfmi__npte = call_expr.args[1]
        rzof__xto = typemap[xfmi__npte.name]
        rzof__xto = rzof__xto.instance_type
        wkm__fja = rzof__xto.meta
        oqfru__xkzp = dict(call_expr.kws)
        if 'used_cols' in oqfru__xkzp:
            zlu__pjzc = oqfru__xkzp['used_cols']
            moz__dkn = typemap[zlu__pjzc.name]
            moz__dkn = moz__dkn.instance_type
            kzj__woj = set(moz__dkn.meta)
            fnb__kkv = set()
            for kncxh__mtp, ysb__sfq in enumerate(wkm__fja):
                if kncxh__mtp in kzj__woj:
                    fnb__kkv.add(ysb__sfq)
            return fnb__kkv
        else:
            return set(wkm__fja)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        vofsg__rkj = typemap[call_expr.args[2].name].instance_type.meta
        urxa__qptjr = len(typemap[call_expr.args[0].name].arr_types)
        return set(kncxh__mtp for kncxh__mtp in vofsg__rkj if kncxh__mtp <
            urxa__qptjr)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        ieb__quz = typemap[call_expr.args[2].name].instance_type.meta
        iwgws__bciou = len(typemap[call_expr.args[0].name].arr_types)
        oqfru__xkzp = dict(call_expr.kws)
        if 'used_cols' in oqfru__xkzp:
            kzj__woj = set(typemap[oqfru__xkzp['used_cols'].name].
                instance_type.meta)
            cdbh__dfnxa = set()
            for bji__vve, tgx__gvs in enumerate(ieb__quz):
                if bji__vve in kzj__woj and tgx__gvs < iwgws__bciou:
                    cdbh__dfnxa.add(tgx__gvs)
            return cdbh__dfnxa
        else:
            return set(kncxh__mtp for kncxh__mtp in ieb__quz if kncxh__mtp <
                iwgws__bciou)
    return None
