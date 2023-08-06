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
        ojbz__irgae = typemap[call_expr.args[1].name].literal_value
        return {ojbz__irgae}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        kbv__vot = dict(call_expr.kws)
        if 'used_cols' in kbv__vot:
            lskh__vkjqb = kbv__vot['used_cols']
            feqx__gzvsm = typemap[lskh__vkjqb.name]
            feqx__gzvsm = feqx__gzvsm.instance_type
            return set(feqx__gzvsm.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        lskh__vkjqb = call_expr.args[1]
        feqx__gzvsm = typemap[lskh__vkjqb.name]
        feqx__gzvsm = feqx__gzvsm.instance_type
        return set(feqx__gzvsm.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        pns__bjsdl = call_expr.args[1]
        vldkn__fbh = typemap[pns__bjsdl.name]
        vldkn__fbh = vldkn__fbh.instance_type
        ppw__dyqys = vldkn__fbh.meta
        kbv__vot = dict(call_expr.kws)
        if 'used_cols' in kbv__vot:
            lskh__vkjqb = kbv__vot['used_cols']
            feqx__gzvsm = typemap[lskh__vkjqb.name]
            feqx__gzvsm = feqx__gzvsm.instance_type
            ahn__nva = set(feqx__gzvsm.meta)
            jheqs__apo = set()
            for vrnh__hea, yrpfc__hge in enumerate(ppw__dyqys):
                if vrnh__hea in ahn__nva:
                    jheqs__apo.add(yrpfc__hge)
            return jheqs__apo
        else:
            return set(ppw__dyqys)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        hxsj__cvw = typemap[call_expr.args[2].name].instance_type.meta
        myiuz__zjamg = len(typemap[call_expr.args[0].name].arr_types)
        return set(vrnh__hea for vrnh__hea in hxsj__cvw if vrnh__hea <
            myiuz__zjamg)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        qva__nxk = typemap[call_expr.args[2].name].instance_type.meta
        gcrrw__tyta = len(typemap[call_expr.args[0].name].arr_types)
        kbv__vot = dict(call_expr.kws)
        if 'used_cols' in kbv__vot:
            ahn__nva = set(typemap[kbv__vot['used_cols'].name].
                instance_type.meta)
            mcp__fypv = set()
            for vsoz__mge, svv__vnz in enumerate(qva__nxk):
                if vsoz__mge in ahn__nva and svv__vnz < gcrrw__tyta:
                    mcp__fypv.add(svv__vnz)
            return mcp__fypv
        else:
            return set(vrnh__hea for vrnh__hea in qva__nxk if vrnh__hea <
                gcrrw__tyta)
    return None
