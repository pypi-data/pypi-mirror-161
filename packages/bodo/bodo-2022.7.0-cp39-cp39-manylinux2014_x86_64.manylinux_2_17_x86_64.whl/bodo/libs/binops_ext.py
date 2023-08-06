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
        yld__dog = lhs.data if isinstance(lhs, SeriesType) else lhs
        uhq__xyfzw = rhs.data if isinstance(rhs, SeriesType) else rhs
        if yld__dog in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and uhq__xyfzw.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            yld__dog = uhq__xyfzw.dtype
        elif uhq__xyfzw in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and yld__dog.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            uhq__xyfzw = yld__dog.dtype
        ukvx__npwkd = yld__dog, uhq__xyfzw
        upw__jyi = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            lpwz__yregg = self.context.resolve_function_type(self.key,
                ukvx__npwkd, {}).return_type
        except Exception as ewe__omuqn:
            raise BodoError(upw__jyi)
        if is_overload_bool(lpwz__yregg):
            raise BodoError(upw__jyi)
        ffzoz__ywshb = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        sdau__jqvzq = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        tfcvt__oqrlo = types.bool_
        ucw__qui = SeriesType(tfcvt__oqrlo, lpwz__yregg, ffzoz__ywshb,
            sdau__jqvzq)
        return ucw__qui(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        loz__yraln = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if loz__yraln is None:
            loz__yraln = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, loz__yraln, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        yld__dog = lhs.data if isinstance(lhs, SeriesType) else lhs
        uhq__xyfzw = rhs.data if isinstance(rhs, SeriesType) else rhs
        ukvx__npwkd = yld__dog, uhq__xyfzw
        upw__jyi = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            lpwz__yregg = self.context.resolve_function_type(self.key,
                ukvx__npwkd, {}).return_type
        except Exception as ighrk__juvu:
            raise BodoError(upw__jyi)
        ffzoz__ywshb = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        sdau__jqvzq = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        tfcvt__oqrlo = lpwz__yregg.dtype
        ucw__qui = SeriesType(tfcvt__oqrlo, lpwz__yregg, ffzoz__ywshb,
            sdau__jqvzq)
        return ucw__qui(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        loz__yraln = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if loz__yraln is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                loz__yraln = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, loz__yraln, sig, args)
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
            loz__yraln = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return loz__yraln(lhs, rhs)
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
            loz__yraln = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return loz__yraln(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    twge__wmkch = lhs == datetime_timedelta_type and rhs == datetime_date_type
    ecmk__ijst = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return twge__wmkch or ecmk__ijst


def add_timestamp(lhs, rhs):
    nvcy__asfa = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    zmz__ootj = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return nvcy__asfa or zmz__ootj


def add_datetime_and_timedeltas(lhs, rhs):
    onobq__vpegh = [datetime_timedelta_type, pd_timedelta_type]
    zunzl__rsceg = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    iixgy__jgyg = lhs in onobq__vpegh and rhs in onobq__vpegh
    aual__hjgbr = (lhs == datetime_datetime_type and rhs in onobq__vpegh or
        rhs == datetime_datetime_type and lhs in onobq__vpegh)
    return iixgy__jgyg or aual__hjgbr


def mul_string_arr_and_int(lhs, rhs):
    uhq__xyfzw = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    yld__dog = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return uhq__xyfzw or yld__dog


def mul_timedelta_and_int(lhs, rhs):
    twge__wmkch = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    ecmk__ijst = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return twge__wmkch or ecmk__ijst


def mul_date_offset_and_int(lhs, rhs):
    fmuu__nib = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    gtcyp__iuif = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return fmuu__nib or gtcyp__iuif


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    xfyol__vcael = [datetime_datetime_type, pd_timestamp_type,
        datetime_date_type]
    hdhv__umym = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in hdhv__umym and lhs in xfyol__vcael


def sub_dt_index_and_timestamp(lhs, rhs):
    eqnaw__sdcvv = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    dlpk__ruv = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return eqnaw__sdcvv or dlpk__ruv


def sub_dt_or_td(lhs, rhs):
    pxx__ftee = lhs == datetime_date_type and rhs == datetime_timedelta_type
    cvlwy__iyijg = lhs == datetime_date_type and rhs == datetime_date_type
    lyfbq__kezo = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return pxx__ftee or cvlwy__iyijg or lyfbq__kezo


def sub_datetime_and_timedeltas(lhs, rhs):
    rqt__wwji = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    njerb__kffwy = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return rqt__wwji or njerb__kffwy


def div_timedelta_and_int(lhs, rhs):
    iixgy__jgyg = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    zed__ounvn = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return iixgy__jgyg or zed__ounvn


def div_datetime_timedelta(lhs, rhs):
    iixgy__jgyg = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    zed__ounvn = lhs == datetime_timedelta_type and rhs == types.int64
    return iixgy__jgyg or zed__ounvn


def mod_timedeltas(lhs, rhs):
    qklk__sgo = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    oxwyu__aoti = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return qklk__sgo or oxwyu__aoti


def cmp_dt_index_to_string(lhs, rhs):
    eqnaw__sdcvv = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    dlpk__ruv = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return eqnaw__sdcvv or dlpk__ruv


def cmp_timestamp_or_date(lhs, rhs):
    reei__rqav = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    vmyri__ibag = (lhs == bodo.hiframes.datetime_date_ext.
        datetime_date_type and rhs == pd_timestamp_type)
    wdmm__gmz = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    zmfcj__eksx = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    vcfzs__mql = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return reei__rqav or vmyri__ibag or wdmm__gmz or zmfcj__eksx or vcfzs__mql


def cmp_timeseries(lhs, rhs):
    drn__eqnmc = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    hjddr__pgi = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    anz__beqhy = drn__eqnmc or hjddr__pgi
    jostu__uhphz = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    acb__lsold = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    hpza__maze = jostu__uhphz or acb__lsold
    return anz__beqhy or hpza__maze


def cmp_timedeltas(lhs, rhs):
    iixgy__jgyg = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in iixgy__jgyg and rhs in iixgy__jgyg


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    bjmew__fevmo = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return bjmew__fevmo


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    ytgpt__wal = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    ikzt__ivm = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    yugui__bev = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    xbt__ftom = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return ytgpt__wal or ikzt__ivm or yugui__bev or xbt__ftom


def args_td_and_int_array(lhs, rhs):
    jtaej__qac = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    arstu__ntk = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return jtaej__qac and arstu__ntk


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        ecmk__ijst = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        twge__wmkch = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        udui__stf = ecmk__ijst or twge__wmkch
        gzczl__nkd = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        jvgq__rglj = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        pywj__dru = gzczl__nkd or jvgq__rglj
        qop__jhq = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        wfrlr__gcern = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        xvjb__vvq = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        hev__daj = qop__jhq or wfrlr__gcern or xvjb__vvq
        ithkz__ljkf = isinstance(lhs, types.List) and isinstance(rhs, types
            .Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        mgri__qxkuz = isinstance(lhs, tys) or isinstance(rhs, tys)
        efas__phhvl = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (udui__stf or pywj__dru or hev__daj or ithkz__ljkf or
            mgri__qxkuz or efas__phhvl)
    if op == operator.pow:
        rlvak__ldjp = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        wnzs__mbd = isinstance(lhs, types.Float) and isinstance(rhs, (types
            .IntegerLiteral, types.Float, types.Integer) or rhs in types.
            unsigned_domain or rhs in types.signed_domain)
        xvjb__vvq = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        efas__phhvl = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return rlvak__ldjp or wnzs__mbd or xvjb__vvq or efas__phhvl
    if op == operator.floordiv:
        wfrlr__gcern = lhs in types.real_domain and rhs in types.real_domain
        qop__jhq = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        tpvpw__jgjdi = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        iixgy__jgyg = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        efas__phhvl = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (wfrlr__gcern or qop__jhq or tpvpw__jgjdi or iixgy__jgyg or
            efas__phhvl)
    if op == operator.truediv:
        jlwrk__sye = lhs in machine_ints and rhs in machine_ints
        wfrlr__gcern = lhs in types.real_domain and rhs in types.real_domain
        xvjb__vvq = lhs in types.complex_domain and rhs in types.complex_domain
        qop__jhq = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        tpvpw__jgjdi = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        odmp__ekkeu = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        iixgy__jgyg = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        efas__phhvl = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (jlwrk__sye or wfrlr__gcern or xvjb__vvq or qop__jhq or
            tpvpw__jgjdi or odmp__ekkeu or iixgy__jgyg or efas__phhvl)
    if op == operator.mod:
        jlwrk__sye = lhs in machine_ints and rhs in machine_ints
        wfrlr__gcern = lhs in types.real_domain and rhs in types.real_domain
        qop__jhq = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        tpvpw__jgjdi = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        efas__phhvl = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (jlwrk__sye or wfrlr__gcern or qop__jhq or tpvpw__jgjdi or
            efas__phhvl)
    if op == operator.add or op == operator.sub:
        udui__stf = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        bwqu__uvlk = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        wunfj__byh = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        mxbk__urpii = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        qop__jhq = isinstance(lhs, types.Integer) and isinstance(rhs, types
            .Integer)
        wfrlr__gcern = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        xvjb__vvq = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        hev__daj = qop__jhq or wfrlr__gcern or xvjb__vvq
        efas__phhvl = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        wim__tems = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        ithkz__ljkf = isinstance(lhs, types.List) and isinstance(rhs, types
            .List)
        mpl__vgxr = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        cls__udvl = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        apeyd__ypjpa = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs
            , types.UnicodeCharSeq)
        tbrth__sbp = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        fwao__gqunh = mpl__vgxr or cls__udvl or apeyd__ypjpa or tbrth__sbp
        pywj__dru = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        ofsqw__zxdc = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        ixwxq__kclk = pywj__dru or ofsqw__zxdc
        ccy__pcsjc = lhs == types.NPTimedelta and rhs == types.NPDatetime
        hhcak__ljngo = (wim__tems or ithkz__ljkf or fwao__gqunh or
            ixwxq__kclk or ccy__pcsjc)
        ubrmr__tpomg = op == operator.add and hhcak__ljngo
        return (udui__stf or bwqu__uvlk or wunfj__byh or mxbk__urpii or
            hev__daj or efas__phhvl or ubrmr__tpomg)


def cmp_op_supported_by_numba(lhs, rhs):
    efas__phhvl = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    ithkz__ljkf = isinstance(lhs, types.ListType) and isinstance(rhs, types
        .ListType)
    udui__stf = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    krwi__ddcmw = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    pywj__dru = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    wim__tems = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types.
        BaseTuple)
    mxbk__urpii = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    hev__daj = isinstance(lhs, types.Number) and isinstance(rhs, types.Number)
    lwxuz__xeyah = isinstance(lhs, types.Boolean) and isinstance(rhs, types
        .Boolean)
    cyr__itph = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    bhi__mrzz = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    ivtkd__rpgim = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    sfqb__afaf = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (ithkz__ljkf or udui__stf or krwi__ddcmw or pywj__dru or
        wim__tems or mxbk__urpii or hev__daj or lwxuz__xeyah or cyr__itph or
        bhi__mrzz or efas__phhvl or ivtkd__rpgim or sfqb__afaf)


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
        svih__jlwjo = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(svih__jlwjo)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        svih__jlwjo = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(svih__jlwjo)


install_arith_ops()
