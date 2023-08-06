""" Implementation of binary operators for the different types.
    Currently implemented operators:
        arith: add, sub, mul, truediv, floordiv, mod, pow
        cmp: lt, le, eq, ne, ge, gt
"""
import operator
import numba
from numba.core import types
from numba.core.imputils import lower_builtin
from numba.core.typing.builtins import machine_ints
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type, datetime_timedelta_type
from bodo.hiframes.datetime_timedelta_ext import datetime_datetime_type, datetime_timedelta_array_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import DatetimeIndexType, HeterogeneousIndexType, is_index_type
from bodo.hiframes.pd_offsets_ext import date_offset_type, month_begin_type, month_end_type, week_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.series_impl import SeriesType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.typing import BodoError, is_overload_bool, is_str_arr_type, is_timedelta_type


class SeriesCmpOpTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lhs, rhs = args
        if cmp_timeseries(lhs, rhs) or (isinstance(lhs, DataFrameType) or
            isinstance(rhs, DataFrameType)) or not (isinstance(lhs,
            SeriesType) or isinstance(rhs, SeriesType)):
            return
        mmcv__kkxcj = lhs.data if isinstance(lhs, SeriesType) else lhs
        tqx__xmuqw = rhs.data if isinstance(rhs, SeriesType) else rhs
        if mmcv__kkxcj in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and tqx__xmuqw.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            mmcv__kkxcj = tqx__xmuqw.dtype
        elif tqx__xmuqw in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and mmcv__kkxcj.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            tqx__xmuqw = mmcv__kkxcj.dtype
        kkd__rmth = mmcv__kkxcj, tqx__xmuqw
        xqjom__chxkj = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            rpido__rwtsl = self.context.resolve_function_type(self.key,
                kkd__rmth, {}).return_type
        except Exception as fcbv__pzls:
            raise BodoError(xqjom__chxkj)
        if is_overload_bool(rpido__rwtsl):
            raise BodoError(xqjom__chxkj)
        uxjqd__byzb = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        kysn__hqowy = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        slns__dkot = types.bool_
        bozny__nfpib = SeriesType(slns__dkot, rpido__rwtsl, uxjqd__byzb,
            kysn__hqowy)
        return bozny__nfpib(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        izpxp__uvzxv = bodo.hiframes.series_impl.create_binary_op_overload(op)(
            *sig.args)
        if izpxp__uvzxv is None:
            izpxp__uvzxv = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, izpxp__uvzxv, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        mmcv__kkxcj = lhs.data if isinstance(lhs, SeriesType) else lhs
        tqx__xmuqw = rhs.data if isinstance(rhs, SeriesType) else rhs
        kkd__rmth = mmcv__kkxcj, tqx__xmuqw
        xqjom__chxkj = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            rpido__rwtsl = self.context.resolve_function_type(self.key,
                kkd__rmth, {}).return_type
        except Exception as bim__efvtw:
            raise BodoError(xqjom__chxkj)
        uxjqd__byzb = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        kysn__hqowy = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        slns__dkot = rpido__rwtsl.dtype
        bozny__nfpib = SeriesType(slns__dkot, rpido__rwtsl, uxjqd__byzb,
            kysn__hqowy)
        return bozny__nfpib(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        izpxp__uvzxv = bodo.hiframes.series_impl.create_binary_op_overload(op)(
            *sig.args)
        if izpxp__uvzxv is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                izpxp__uvzxv = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, izpxp__uvzxv, sig, args)
    return lower_and_or_impl


def overload_add_operator_scalars(lhs, rhs):
    if lhs == week_type or rhs == week_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_week_offset_type(lhs, rhs))
    if lhs == month_begin_type or rhs == month_begin_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_begin_offset_type(lhs, rhs))
    if lhs == month_end_type or rhs == month_end_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_end_offset_type(lhs, rhs))
    if lhs == date_offset_type or rhs == date_offset_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_date_offset_type(lhs, rhs))
    if add_timestamp(lhs, rhs):
        return bodo.hiframes.pd_timestamp_ext.overload_add_operator_timestamp(
            lhs, rhs)
    if add_dt_td_and_dt_date(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_add_operator_datetime_date(lhs, rhs))
    if add_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_add_operator_datetime_timedelta(lhs, rhs))
    raise_error_if_not_numba_supported(operator.add, lhs, rhs)


def overload_sub_operator_scalars(lhs, rhs):
    if sub_offset_to_datetime_or_timestamp(lhs, rhs):
        return bodo.hiframes.pd_offsets_ext.overload_sub_operator_offsets(lhs,
            rhs)
    if lhs == pd_timestamp_type and rhs in [pd_timestamp_type,
        datetime_timedelta_type, pd_timedelta_type]:
        return bodo.hiframes.pd_timestamp_ext.overload_sub_operator_timestamp(
            lhs, rhs)
    if sub_dt_or_td(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_sub_operator_datetime_date(lhs, rhs))
    if sub_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_sub_operator_datetime_timedelta(lhs, rhs))
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
        return (bodo.hiframes.datetime_datetime_ext.
            overload_sub_operator_datetime_datetime(lhs, rhs))
    raise_error_if_not_numba_supported(operator.sub, lhs, rhs)


def create_overload_arith_op(op):

    def overload_arith_operator(lhs, rhs):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if time_series_operation(lhs, rhs) and op in [operator.add,
            operator.sub]:
            return bodo.hiframes.series_dt_impl.create_bin_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return bodo.hiframes.series_impl.create_binary_op_overload(op)(lhs,
                rhs)
        if sub_dt_index_and_timestamp(lhs, rhs) and op == operator.sub:
            return (bodo.hiframes.pd_index_ext.
                overload_sub_operator_datetime_index(lhs, rhs))
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if args_td_and_int_array(lhs, rhs):
            return bodo.libs.int_arr_ext.get_int_array_op_pd_td(op)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if op == operator.add and (is_str_arr_type(lhs) or types.unliteral(
            lhs) == string_type):
            return bodo.libs.str_arr_ext.overload_add_operator_string_array(lhs
                , rhs)
        if op == operator.add:
            return overload_add_operator_scalars(lhs, rhs)
        if op == operator.sub:
            return overload_sub_operator_scalars(lhs, rhs)
        if op == operator.mul:
            if mul_timedelta_and_int(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mul_operator_timedelta(lhs, rhs))
            if mul_string_arr_and_int(lhs, rhs):
                return bodo.libs.str_arr_ext.overload_mul_operator_str_arr(lhs,
                    rhs)
            if mul_date_offset_and_int(lhs, rhs):
                return (bodo.hiframes.pd_offsets_ext.
                    overload_mul_date_offset_types(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op in [operator.truediv, operator.floordiv]:
            if div_timedelta_and_int(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_pd_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_pd_timedelta(lhs, rhs))
            if div_datetime_timedelta(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_dt_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_dt_timedelta(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.mod:
            if mod_timedeltas(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mod_operator_timedeltas(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.pow:
            raise_error_if_not_numba_supported(op, lhs, rhs)
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_arith_operator


def create_overload_cmp_operator(op):

    def overload_cmp_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
                f'{op} operator')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
                f'{op} operator')
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if cmp_timeseries(lhs, rhs):
            return bodo.hiframes.series_dt_impl.create_cmp_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if lhs == datetime_date_array_type or rhs == datetime_date_array_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload_arr(
                op)(lhs, rhs)
        if (lhs == datetime_timedelta_array_type or rhs ==
            datetime_timedelta_array_type):
            izpxp__uvzxv = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return izpxp__uvzxv(lhs, rhs)
        if is_str_arr_type(lhs) or is_str_arr_type(rhs):
            return bodo.libs.str_arr_ext.create_binary_op_overload(op)(lhs, rhs
                )
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            return bodo.libs.decimal_arr_ext.decimal_create_cmp_op_overload(op
                )(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if binary_array_cmp(lhs, rhs):
            return bodo.libs.binary_arr_ext.create_binary_cmp_op_overload(op)(
                lhs, rhs)
        if cmp_dt_index_to_string(lhs, rhs):
            return bodo.hiframes.pd_index_ext.overload_binop_dti_str(op)(lhs,
                rhs)
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if lhs == datetime_date_type and rhs == datetime_date_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload(op)(
                lhs, rhs)
        if can_cmp_date_datetime(lhs, rhs, op):
            return (bodo.hiframes.datetime_date_ext.
                create_datetime_date_cmp_op_overload(op)(lhs, rhs))
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
            return bodo.hiframes.datetime_datetime_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:
            return bodo.hiframes.datetime_timedelta_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if cmp_timedeltas(lhs, rhs):
            izpxp__uvzxv = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return izpxp__uvzxv(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    ime__dfy = lhs == datetime_timedelta_type and rhs == datetime_date_type
    iziyp__kftx = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return ime__dfy or iziyp__kftx


def add_timestamp(lhs, rhs):
    wkhy__trp = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    pqssy__qeoay = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return wkhy__trp or pqssy__qeoay


def add_datetime_and_timedeltas(lhs, rhs):
    cmor__nhk = [datetime_timedelta_type, pd_timedelta_type]
    eyb__dhp = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    wxq__uejhe = lhs in cmor__nhk and rhs in cmor__nhk
    jgib__nefoc = (lhs == datetime_datetime_type and rhs in cmor__nhk or 
        rhs == datetime_datetime_type and lhs in cmor__nhk)
    return wxq__uejhe or jgib__nefoc


def mul_string_arr_and_int(lhs, rhs):
    tqx__xmuqw = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    mmcv__kkxcj = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return tqx__xmuqw or mmcv__kkxcj


def mul_timedelta_and_int(lhs, rhs):
    ime__dfy = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    iziyp__kftx = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return ime__dfy or iziyp__kftx


def mul_date_offset_and_int(lhs, rhs):
    rge__plul = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    mdqe__rxq = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return rge__plul or mdqe__rxq


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    skvpj__jsntn = [datetime_datetime_type, pd_timestamp_type,
        datetime_date_type]
    omqr__frn = [date_offset_type, month_begin_type, month_end_type, week_type]
    return rhs in omqr__frn and lhs in skvpj__jsntn


def sub_dt_index_and_timestamp(lhs, rhs):
    hibrf__brkt = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    mpfl__dujdu = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return hibrf__brkt or mpfl__dujdu


def sub_dt_or_td(lhs, rhs):
    azap__hyhw = lhs == datetime_date_type and rhs == datetime_timedelta_type
    eapo__yyp = lhs == datetime_date_type and rhs == datetime_date_type
    fbom__uuomw = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return azap__hyhw or eapo__yyp or fbom__uuomw


def sub_datetime_and_timedeltas(lhs, rhs):
    nzlwm__igp = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    iwppt__qrub = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return nzlwm__igp or iwppt__qrub


def div_timedelta_and_int(lhs, rhs):
    wxq__uejhe = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    ydqrj__eoum = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return wxq__uejhe or ydqrj__eoum


def div_datetime_timedelta(lhs, rhs):
    wxq__uejhe = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    ydqrj__eoum = lhs == datetime_timedelta_type and rhs == types.int64
    return wxq__uejhe or ydqrj__eoum


def mod_timedeltas(lhs, rhs):
    mbiyh__ltb = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    fnped__alpv = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return mbiyh__ltb or fnped__alpv


def cmp_dt_index_to_string(lhs, rhs):
    hibrf__brkt = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    mpfl__dujdu = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return hibrf__brkt or mpfl__dujdu


def cmp_timestamp_or_date(lhs, rhs):
    wem__nwfz = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    ymagn__wsiy = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    mqmu__cgqy = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    afrp__xiewe = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    nfce__eyhf = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return wem__nwfz or ymagn__wsiy or mqmu__cgqy or afrp__xiewe or nfce__eyhf


def cmp_timeseries(lhs, rhs):
    agrz__aeq = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    wtdq__gawtd = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    cyj__pdn = agrz__aeq or wtdq__gawtd
    rkots__gtey = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    ndlx__llj = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    poxn__tbzr = rkots__gtey or ndlx__llj
    return cyj__pdn or poxn__tbzr


def cmp_timedeltas(lhs, rhs):
    wxq__uejhe = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in wxq__uejhe and rhs in wxq__uejhe


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    hyr__btl = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return hyr__btl


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    rorqx__klmq = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    psmz__lzuo = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    igs__uins = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    exh__brib = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return rorqx__klmq or psmz__lzuo or igs__uins or exh__brib


def args_td_and_int_array(lhs, rhs):
    syc__ywgu = (isinstance(lhs, IntegerArrayType) or isinstance(lhs, types
        .Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance(
        rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    arji__ievp = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return syc__ywgu and arji__ievp


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        iziyp__kftx = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        ime__dfy = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        wxyxq__lwb = iziyp__kftx or ime__dfy
        upw__iutfe = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        iocok__ystmo = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        ffh__atabz = upw__iutfe or iocok__ystmo
        hojxx__onauh = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        dhn__knc = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        aucmn__mrec = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        xie__zbom = hojxx__onauh or dhn__knc or aucmn__mrec
        jbhpi__ppzyt = isinstance(lhs, types.List) and isinstance(rhs,
            types.Integer) or isinstance(lhs, types.Integer) and isinstance(rhs
            , types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        eumqo__ksr = isinstance(lhs, tys) or isinstance(rhs, tys)
        kyb__wtier = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (wxyxq__lwb or ffh__atabz or xie__zbom or jbhpi__ppzyt or
            eumqo__ksr or kyb__wtier)
    if op == operator.pow:
        zpd__svf = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        zqa__babl = isinstance(lhs, types.Float) and isinstance(rhs, (types
            .IntegerLiteral, types.Float, types.Integer) or rhs in types.
            unsigned_domain or rhs in types.signed_domain)
        aucmn__mrec = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        kyb__wtier = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return zpd__svf or zqa__babl or aucmn__mrec or kyb__wtier
    if op == operator.floordiv:
        dhn__knc = lhs in types.real_domain and rhs in types.real_domain
        hojxx__onauh = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        xzo__zndn = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        wxq__uejhe = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        kyb__wtier = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (dhn__knc or hojxx__onauh or xzo__zndn or wxq__uejhe or
            kyb__wtier)
    if op == operator.truediv:
        avn__wibnl = lhs in machine_ints and rhs in machine_ints
        dhn__knc = lhs in types.real_domain and rhs in types.real_domain
        aucmn__mrec = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        hojxx__onauh = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        xzo__zndn = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        hvbq__xzkdo = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        wxq__uejhe = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        kyb__wtier = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (avn__wibnl or dhn__knc or aucmn__mrec or hojxx__onauh or
            xzo__zndn or hvbq__xzkdo or wxq__uejhe or kyb__wtier)
    if op == operator.mod:
        avn__wibnl = lhs in machine_ints and rhs in machine_ints
        dhn__knc = lhs in types.real_domain and rhs in types.real_domain
        hojxx__onauh = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        xzo__zndn = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        kyb__wtier = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (avn__wibnl or dhn__knc or hojxx__onauh or xzo__zndn or
            kyb__wtier)
    if op == operator.add or op == operator.sub:
        wxyxq__lwb = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        olp__ppi = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        yfq__htgk = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        smfzf__vmxd = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        hojxx__onauh = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        dhn__knc = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        aucmn__mrec = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        xie__zbom = hojxx__onauh or dhn__knc or aucmn__mrec
        kyb__wtier = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        cmxg__urvp = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        jbhpi__ppzyt = isinstance(lhs, types.List) and isinstance(rhs,
            types.List)
        jkhnd__udw = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        ggf__wreh = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        kintx__jpqb = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        nkfwq__mmdr = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        moqv__uigbp = jkhnd__udw or ggf__wreh or kintx__jpqb or nkfwq__mmdr
        ffh__atabz = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        epn__mkou = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        najc__wzw = ffh__atabz or epn__mkou
        mwlkz__yqlm = lhs == types.NPTimedelta and rhs == types.NPDatetime
        erxz__ghaui = (cmxg__urvp or jbhpi__ppzyt or moqv__uigbp or
            najc__wzw or mwlkz__yqlm)
        vmd__dpbtp = op == operator.add and erxz__ghaui
        return (wxyxq__lwb or olp__ppi or yfq__htgk or smfzf__vmxd or
            xie__zbom or kyb__wtier or vmd__dpbtp)


def cmp_op_supported_by_numba(lhs, rhs):
    kyb__wtier = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    jbhpi__ppzyt = isinstance(lhs, types.ListType) and isinstance(rhs,
        types.ListType)
    wxyxq__lwb = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    tbrav__ppvk = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    ffh__atabz = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    cmxg__urvp = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    smfzf__vmxd = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    xie__zbom = isinstance(lhs, types.Number) and isinstance(rhs, types.Number)
    prl__ybgl = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    itdeb__zyh = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    kob__cjjgf = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    qgcph__vzeh = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    eusnn__vzqyg = isinstance(lhs, types.Literal) and isinstance(rhs, types
        .Literal)
    return (jbhpi__ppzyt or wxyxq__lwb or tbrav__ppvk or ffh__atabz or
        cmxg__urvp or smfzf__vmxd or xie__zbom or prl__ybgl or itdeb__zyh or
        kob__cjjgf or kyb__wtier or qgcph__vzeh or eusnn__vzqyg)


def raise_error_if_not_numba_supported(op, lhs, rhs):
    if arith_op_supported_by_numba(op, lhs, rhs):
        return
    raise BodoError(
        f'{op} operator not supported for data types {lhs} and {rhs}.')


def _install_series_and_or():
    for op in (operator.or_, operator.and_):
        infer_global(op)(SeriesAndOrTyper)
        lower_impl = lower_series_and_or(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)


_install_series_and_or()


def _install_cmp_ops():
    for op in (operator.lt, operator.eq, operator.ne, operator.ge, operator
        .gt, operator.le):
        infer_global(op)(SeriesCmpOpTemplate)
        lower_impl = series_cmp_op_lower(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)
        uxa__wutcd = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(uxa__wutcd)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        uxa__wutcd = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(uxa__wutcd)


install_arith_ops()
