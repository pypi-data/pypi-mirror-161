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
        zbgzo__bage = typemap[call_expr.args[1].name].literal_value
        return {zbgzo__bage}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        fmdnc__uzng = dict(call_expr.kws)
        if 'used_cols' in fmdnc__uzng:
            ahd__ufof = fmdnc__uzng['used_cols']
            bgtl__bfcam = typemap[ahd__ufof.name]
            bgtl__bfcam = bgtl__bfcam.instance_type
            return set(bgtl__bfcam.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        ahd__ufof = call_expr.args[1]
        bgtl__bfcam = typemap[ahd__ufof.name]
        bgtl__bfcam = bgtl__bfcam.instance_type
        return set(bgtl__bfcam.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        uvji__jvar = call_expr.args[1]
        ivb__dlx = typemap[uvji__jvar.name]
        ivb__dlx = ivb__dlx.instance_type
        mbhkx__ocp = ivb__dlx.meta
        fmdnc__uzng = dict(call_expr.kws)
        if 'used_cols' in fmdnc__uzng:
            ahd__ufof = fmdnc__uzng['used_cols']
            bgtl__bfcam = typemap[ahd__ufof.name]
            bgtl__bfcam = bgtl__bfcam.instance_type
            riu__akhf = set(bgtl__bfcam.meta)
            yoa__ppsnv = set()
            for cazax__ffekc, iju__zah in enumerate(mbhkx__ocp):
                if cazax__ffekc in riu__akhf:
                    yoa__ppsnv.add(iju__zah)
            return yoa__ppsnv
        else:
            return set(mbhkx__ocp)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        pmov__xbxke = typemap[call_expr.args[2].name].instance_type.meta
        bgbv__rpiqp = len(typemap[call_expr.args[0].name].arr_types)
        return set(cazax__ffekc for cazax__ffekc in pmov__xbxke if 
            cazax__ffekc < bgbv__rpiqp)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        pqfs__mhw = typemap[call_expr.args[2].name].instance_type.meta
        bxu__dkol = len(typemap[call_expr.args[0].name].arr_types)
        fmdnc__uzng = dict(call_expr.kws)
        if 'used_cols' in fmdnc__uzng:
            riu__akhf = set(typemap[fmdnc__uzng['used_cols'].name].
                instance_type.meta)
            abv__twt = set()
            for zxuz__tuf, msui__serz in enumerate(pqfs__mhw):
                if zxuz__tuf in riu__akhf and msui__serz < bxu__dkol:
                    abv__twt.add(msui__serz)
            return abv__twt
        else:
            return set(cazax__ffekc for cazax__ffekc in pqfs__mhw if 
                cazax__ffekc < bxu__dkol)
    return None
