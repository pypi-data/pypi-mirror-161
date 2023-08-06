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
        zpno__rlr = typemap[call_expr.args[1].name].literal_value
        return {zpno__rlr}
    elif fdef in {('table_filter', 'bodo.hiframes.table'), ('table_astype',
        'bodo.utils.table_utils'), ('generate_mappable_table_func',
        'bodo.utils.table_utils'), ('set_table_data', 'bodo.hiframes.table'
        ), ('set_table_data_null', 'bodo.hiframes.table')}:
        xqjs__rlb = dict(call_expr.kws)
        if 'used_cols' in xqjs__rlb:
            mpc__dpxq = xqjs__rlb['used_cols']
            mvsh__sjwsq = typemap[mpc__dpxq.name]
            mvsh__sjwsq = mvsh__sjwsq.instance_type
            return set(mvsh__sjwsq.meta)
    elif fdef == ('table_concat', 'bodo.utils.table_utils'):
        mpc__dpxq = call_expr.args[1]
        mvsh__sjwsq = typemap[mpc__dpxq.name]
        mvsh__sjwsq = mvsh__sjwsq.instance_type
        return set(mvsh__sjwsq.meta)
    elif fdef == ('table_subset', 'bodo.hiframes.table'):
        slkpn__drrr = call_expr.args[1]
        fun__cofpd = typemap[slkpn__drrr.name]
        fun__cofpd = fun__cofpd.instance_type
        cwvj__dmgni = fun__cofpd.meta
        xqjs__rlb = dict(call_expr.kws)
        if 'used_cols' in xqjs__rlb:
            mpc__dpxq = xqjs__rlb['used_cols']
            mvsh__sjwsq = typemap[mpc__dpxq.name]
            mvsh__sjwsq = mvsh__sjwsq.instance_type
            doq__nom = set(mvsh__sjwsq.meta)
            mja__okxgq = set()
            for nvkaj__xrvx, vneui__coi in enumerate(cwvj__dmgni):
                if nvkaj__xrvx in doq__nom:
                    mja__okxgq.add(vneui__coi)
            return mja__okxgq
        else:
            return set(cwvj__dmgni)
    elif fdef == ('py_data_to_cpp_table', 'bodo.libs.array'):
        diomk__cjo = typemap[call_expr.args[2].name].instance_type.meta
        nnr__qzm = len(typemap[call_expr.args[0].name].arr_types)
        return set(nvkaj__xrvx for nvkaj__xrvx in diomk__cjo if nvkaj__xrvx <
            nnr__qzm)
    elif fdef == ('logical_table_to_table', 'bodo.hiframes.table'):
        bgrk__leenk = typemap[call_expr.args[2].name].instance_type.meta
        pfy__uffy = len(typemap[call_expr.args[0].name].arr_types)
        xqjs__rlb = dict(call_expr.kws)
        if 'used_cols' in xqjs__rlb:
            doq__nom = set(typemap[xqjs__rlb['used_cols'].name].
                instance_type.meta)
            xkt__wzb = set()
            for gjw__zgof, qnmc__odpbb in enumerate(bgrk__leenk):
                if gjw__zgof in doq__nom and qnmc__odpbb < pfy__uffy:
                    xkt__wzb.add(qnmc__odpbb)
            return xkt__wzb
        else:
            return set(nvkaj__xrvx for nvkaj__xrvx in bgrk__leenk if 
                nvkaj__xrvx < pfy__uffy)
    return None
