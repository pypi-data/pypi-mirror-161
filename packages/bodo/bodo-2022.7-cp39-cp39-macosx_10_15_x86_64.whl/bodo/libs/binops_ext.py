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
        vza__szco = lhs.data if isinstance(lhs, SeriesType) else lhs
        kdvj__suz = rhs.data if isinstance(rhs, SeriesType) else rhs
        if vza__szco in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and kdvj__suz.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            vza__szco = kdvj__suz.dtype
        elif kdvj__suz in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and vza__szco.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            kdvj__suz = vza__szco.dtype
        iqrh__poh = vza__szco, kdvj__suz
        pwv__nxbet = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            xej__vxn = self.context.resolve_function_type(self.key,
                iqrh__poh, {}).return_type
        except Exception as zshac__syett:
            raise BodoError(pwv__nxbet)
        if is_overload_bool(xej__vxn):
            raise BodoError(pwv__nxbet)
        olik__edva = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        fnpc__varh = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        nuu__hlq = types.bool_
        fwier__xkbt = SeriesType(nuu__hlq, xej__vxn, olik__edva, fnpc__varh)
        return fwier__xkbt(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        nilp__usfi = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if nilp__usfi is None:
            nilp__usfi = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, nilp__usfi, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        vza__szco = lhs.data if isinstance(lhs, SeriesType) else lhs
        kdvj__suz = rhs.data if isinstance(rhs, SeriesType) else rhs
        iqrh__poh = vza__szco, kdvj__suz
        pwv__nxbet = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            xej__vxn = self.context.resolve_function_type(self.key,
                iqrh__poh, {}).return_type
        except Exception as lgzo__yhzyg:
            raise BodoError(pwv__nxbet)
        olik__edva = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        fnpc__varh = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        nuu__hlq = xej__vxn.dtype
        fwier__xkbt = SeriesType(nuu__hlq, xej__vxn, olik__edva, fnpc__varh)
        return fwier__xkbt(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        nilp__usfi = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if nilp__usfi is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                nilp__usfi = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, nilp__usfi, sig, args)
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
            nilp__usfi = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return nilp__usfi(lhs, rhs)
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
            nilp__usfi = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return nilp__usfi(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    oeeo__znegw = lhs == datetime_timedelta_type and rhs == datetime_date_type
    xuga__vlw = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return oeeo__znegw or xuga__vlw


def add_timestamp(lhs, rhs):
    wskc__hips = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    sxb__asxdq = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return wskc__hips or sxb__asxdq


def add_datetime_and_timedeltas(lhs, rhs):
    deh__bjo = [datetime_timedelta_type, pd_timedelta_type]
    uiv__yju = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    qfdax__vxau = lhs in deh__bjo and rhs in deh__bjo
    tbbi__zpzoa = (lhs == datetime_datetime_type and rhs in deh__bjo or rhs ==
        datetime_datetime_type and lhs in deh__bjo)
    return qfdax__vxau or tbbi__zpzoa


def mul_string_arr_and_int(lhs, rhs):
    kdvj__suz = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    vza__szco = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return kdvj__suz or vza__szco


def mul_timedelta_and_int(lhs, rhs):
    oeeo__znegw = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    xuga__vlw = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return oeeo__znegw or xuga__vlw


def mul_date_offset_and_int(lhs, rhs):
    okw__qdprr = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    fcjs__nwtsl = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return okw__qdprr or fcjs__nwtsl


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    lphg__fnh = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    pyia__ssvo = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in pyia__ssvo and lhs in lphg__fnh


def sub_dt_index_and_timestamp(lhs, rhs):
    rixc__jjc = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    nrtty__ilz = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return rixc__jjc or nrtty__ilz


def sub_dt_or_td(lhs, rhs):
    epd__xutkt = lhs == datetime_date_type and rhs == datetime_timedelta_type
    vof__dvy = lhs == datetime_date_type and rhs == datetime_date_type
    aav__wvid = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return epd__xutkt or vof__dvy or aav__wvid


def sub_datetime_and_timedeltas(lhs, rhs):
    cpj__eeebi = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    czxo__afdl = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return cpj__eeebi or czxo__afdl


def div_timedelta_and_int(lhs, rhs):
    qfdax__vxau = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    majfr__qsuu = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return qfdax__vxau or majfr__qsuu


def div_datetime_timedelta(lhs, rhs):
    qfdax__vxau = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    majfr__qsuu = lhs == datetime_timedelta_type and rhs == types.int64
    return qfdax__vxau or majfr__qsuu


def mod_timedeltas(lhs, rhs):
    ljvh__kxf = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    lbueq__hvbw = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return ljvh__kxf or lbueq__hvbw


def cmp_dt_index_to_string(lhs, rhs):
    rixc__jjc = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    nrtty__ilz = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return rixc__jjc or nrtty__ilz


def cmp_timestamp_or_date(lhs, rhs):
    uxzcw__whde = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    tir__pvwzv = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    arozo__uop = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    vaqr__rjqz = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    ngbcn__bnn = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return uxzcw__whde or tir__pvwzv or arozo__uop or vaqr__rjqz or ngbcn__bnn


def cmp_timeseries(lhs, rhs):
    pofzd__qipgn = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (
        bodo.utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs
        .str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    zrrut__lpzzl = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (
        bodo.utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs
        .str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    dap__kht = pofzd__qipgn or zrrut__lpzzl
    vrw__mjrke = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    dwl__sbj = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    jvgc__trszr = vrw__mjrke or dwl__sbj
    return dap__kht or jvgc__trszr


def cmp_timedeltas(lhs, rhs):
    qfdax__vxau = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in qfdax__vxau and rhs in qfdax__vxau


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    cwxy__ofup = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return cwxy__ofup


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    ptkq__wolz = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    wqt__yib = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    lavq__kmni = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    jgbhh__imkct = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return ptkq__wolz or wqt__yib or lavq__kmni or jgbhh__imkct


def args_td_and_int_array(lhs, rhs):
    jfo__lgdz = (isinstance(lhs, IntegerArrayType) or isinstance(lhs, types
        .Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance(
        rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    vkipf__fbx = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return jfo__lgdz and vkipf__fbx


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        xuga__vlw = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        oeeo__znegw = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        dgo__giqfv = xuga__vlw or oeeo__znegw
        fkbgh__wjq = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        fnq__tby = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        jsgj__lmtvk = fkbgh__wjq or fnq__tby
        qgtiy__qlyv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        nclwk__wvmz = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        vofni__slwy = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        yiwid__cei = qgtiy__qlyv or nclwk__wvmz or vofni__slwy
        pbd__luv = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        reior__oxyi = isinstance(lhs, tys) or isinstance(rhs, tys)
        wljni__dnmj = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (dgo__giqfv or jsgj__lmtvk or yiwid__cei or pbd__luv or
            reior__oxyi or wljni__dnmj)
    if op == operator.pow:
        hpyb__djfi = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        bdful__bgg = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        vofni__slwy = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        wljni__dnmj = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return hpyb__djfi or bdful__bgg or vofni__slwy or wljni__dnmj
    if op == operator.floordiv:
        nclwk__wvmz = lhs in types.real_domain and rhs in types.real_domain
        qgtiy__qlyv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        prp__nwo = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        qfdax__vxau = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        wljni__dnmj = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (nclwk__wvmz or qgtiy__qlyv or prp__nwo or qfdax__vxau or
            wljni__dnmj)
    if op == operator.truediv:
        rdlto__djd = lhs in machine_ints and rhs in machine_ints
        nclwk__wvmz = lhs in types.real_domain and rhs in types.real_domain
        vofni__slwy = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        qgtiy__qlyv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        prp__nwo = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        qyklc__rvhm = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        qfdax__vxau = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        wljni__dnmj = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (rdlto__djd or nclwk__wvmz or vofni__slwy or qgtiy__qlyv or
            prp__nwo or qyklc__rvhm or qfdax__vxau or wljni__dnmj)
    if op == operator.mod:
        rdlto__djd = lhs in machine_ints and rhs in machine_ints
        nclwk__wvmz = lhs in types.real_domain and rhs in types.real_domain
        qgtiy__qlyv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        prp__nwo = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        wljni__dnmj = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (rdlto__djd or nclwk__wvmz or qgtiy__qlyv or prp__nwo or
            wljni__dnmj)
    if op == operator.add or op == operator.sub:
        dgo__giqfv = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        xgql__gknhs = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        owqyr__gfhs = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        yrlaw__qmfk = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        qgtiy__qlyv = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        nclwk__wvmz = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        vofni__slwy = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        yiwid__cei = qgtiy__qlyv or nclwk__wvmz or vofni__slwy
        wljni__dnmj = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        kgpa__hqp = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        pbd__luv = isinstance(lhs, types.List) and isinstance(rhs, types.List)
        lfhbh__aiuul = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs
            , types.UnicodeType)
        apyp__xazcf = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        ukn__twwj = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        jahjc__cbj = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        fmt__nur = lfhbh__aiuul or apyp__xazcf or ukn__twwj or jahjc__cbj
        jsgj__lmtvk = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        cbgb__hljjx = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        evxu__wdd = jsgj__lmtvk or cbgb__hljjx
        yzt__ucrzl = lhs == types.NPTimedelta and rhs == types.NPDatetime
        uav__obkt = (kgpa__hqp or pbd__luv or fmt__nur or evxu__wdd or
            yzt__ucrzl)
        stdd__rezn = op == operator.add and uav__obkt
        return (dgo__giqfv or xgql__gknhs or owqyr__gfhs or yrlaw__qmfk or
            yiwid__cei or wljni__dnmj or stdd__rezn)


def cmp_op_supported_by_numba(lhs, rhs):
    wljni__dnmj = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    pbd__luv = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    dgo__giqfv = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    dilys__xheio = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    jsgj__lmtvk = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    kgpa__hqp = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types.
        BaseTuple)
    yrlaw__qmfk = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    yiwid__cei = isinstance(lhs, types.Number) and isinstance(rhs, types.Number
        )
    khszk__jfdj = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    fqy__axouf = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    oie__lzdu = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    utqse__sakzf = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    tnspt__cvhy = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (pbd__luv or dgo__giqfv or dilys__xheio or jsgj__lmtvk or
        kgpa__hqp or yrlaw__qmfk or yiwid__cei or khszk__jfdj or fqy__axouf or
        oie__lzdu or wljni__dnmj or utqse__sakzf or tnspt__cvhy)


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
        mkx__gxlbg = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(mkx__gxlbg)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        mkx__gxlbg = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(mkx__gxlbg)


install_arith_ops()
