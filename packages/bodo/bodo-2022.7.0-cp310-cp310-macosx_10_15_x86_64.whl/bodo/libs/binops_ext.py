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
        youvv__zpmb = lhs.data if isinstance(lhs, SeriesType) else lhs
        szbpl__gmj = rhs.data if isinstance(rhs, SeriesType) else rhs
        if youvv__zpmb in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and szbpl__gmj.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            youvv__zpmb = szbpl__gmj.dtype
        elif szbpl__gmj in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and youvv__zpmb.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            szbpl__gmj = youvv__zpmb.dtype
        zvg__iaxp = youvv__zpmb, szbpl__gmj
        egrg__agam = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            zit__ejbv = self.context.resolve_function_type(self.key,
                zvg__iaxp, {}).return_type
        except Exception as iagbl__cxwi:
            raise BodoError(egrg__agam)
        if is_overload_bool(zit__ejbv):
            raise BodoError(egrg__agam)
        ist__dwixc = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        xaiy__ozwx = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        smyur__ajml = types.bool_
        qpxe__ctexe = SeriesType(smyur__ajml, zit__ejbv, ist__dwixc, xaiy__ozwx
            )
        return qpxe__ctexe(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        uiu__aakt = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if uiu__aakt is None:
            uiu__aakt = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, uiu__aakt, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        youvv__zpmb = lhs.data if isinstance(lhs, SeriesType) else lhs
        szbpl__gmj = rhs.data if isinstance(rhs, SeriesType) else rhs
        zvg__iaxp = youvv__zpmb, szbpl__gmj
        egrg__agam = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            zit__ejbv = self.context.resolve_function_type(self.key,
                zvg__iaxp, {}).return_type
        except Exception as lpqpi__gxl:
            raise BodoError(egrg__agam)
        ist__dwixc = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        xaiy__ozwx = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        smyur__ajml = zit__ejbv.dtype
        qpxe__ctexe = SeriesType(smyur__ajml, zit__ejbv, ist__dwixc, xaiy__ozwx
            )
        return qpxe__ctexe(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        uiu__aakt = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if uiu__aakt is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                uiu__aakt = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, uiu__aakt, sig, args)
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
            uiu__aakt = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return uiu__aakt(lhs, rhs)
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
            uiu__aakt = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return uiu__aakt(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    tpfsq__wpsgl = lhs == datetime_timedelta_type and rhs == datetime_date_type
    ril__dnfcg = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return tpfsq__wpsgl or ril__dnfcg


def add_timestamp(lhs, rhs):
    hgtv__kcrbh = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    zqce__dkj = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return hgtv__kcrbh or zqce__dkj


def add_datetime_and_timedeltas(lhs, rhs):
    vcwh__xtj = [datetime_timedelta_type, pd_timedelta_type]
    lth__zkpi = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    ufcol__gpdjy = lhs in vcwh__xtj and rhs in vcwh__xtj
    rqtf__dlbn = (lhs == datetime_datetime_type and rhs in vcwh__xtj or rhs ==
        datetime_datetime_type and lhs in vcwh__xtj)
    return ufcol__gpdjy or rqtf__dlbn


def mul_string_arr_and_int(lhs, rhs):
    szbpl__gmj = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    youvv__zpmb = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return szbpl__gmj or youvv__zpmb


def mul_timedelta_and_int(lhs, rhs):
    tpfsq__wpsgl = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    ril__dnfcg = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return tpfsq__wpsgl or ril__dnfcg


def mul_date_offset_and_int(lhs, rhs):
    zdno__boxc = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    gdosz__qxmd = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return zdno__boxc or gdosz__qxmd


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    cgmfw__lmfwn = [datetime_datetime_type, pd_timestamp_type,
        datetime_date_type]
    dsv__lifyi = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in dsv__lifyi and lhs in cgmfw__lmfwn


def sub_dt_index_and_timestamp(lhs, rhs):
    kobu__ytsc = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    bno__jxv = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return kobu__ytsc or bno__jxv


def sub_dt_or_td(lhs, rhs):
    funwp__svryw = lhs == datetime_date_type and rhs == datetime_timedelta_type
    gdks__ifre = lhs == datetime_date_type and rhs == datetime_date_type
    yjnl__eqb = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return funwp__svryw or gdks__ifre or yjnl__eqb


def sub_datetime_and_timedeltas(lhs, rhs):
    ocnv__jiq = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    jvni__tsbs = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return ocnv__jiq or jvni__tsbs


def div_timedelta_and_int(lhs, rhs):
    ufcol__gpdjy = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    uca__yfyqg = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return ufcol__gpdjy or uca__yfyqg


def div_datetime_timedelta(lhs, rhs):
    ufcol__gpdjy = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    uca__yfyqg = lhs == datetime_timedelta_type and rhs == types.int64
    return ufcol__gpdjy or uca__yfyqg


def mod_timedeltas(lhs, rhs):
    vtzl__mbmws = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    ubzjw__ypv = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return vtzl__mbmws or ubzjw__ypv


def cmp_dt_index_to_string(lhs, rhs):
    kobu__ytsc = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    bno__jxv = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return kobu__ytsc or bno__jxv


def cmp_timestamp_or_date(lhs, rhs):
    hap__jud = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    but__wvx = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    pzgt__qssj = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    ryeyj__pffvj = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    caskl__ufr = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return hap__jud or but__wvx or pzgt__qssj or ryeyj__pffvj or caskl__ufr


def cmp_timeseries(lhs, rhs):
    itkil__zei = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    xpdz__stsw = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    low__zofa = itkil__zei or xpdz__stsw
    juol__mti = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    pobu__umvd = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    tujv__lyube = juol__mti or pobu__umvd
    return low__zofa or tujv__lyube


def cmp_timedeltas(lhs, rhs):
    ufcol__gpdjy = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in ufcol__gpdjy and rhs in ufcol__gpdjy


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    hwo__cszrv = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return hwo__cszrv


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    iivau__zxvbn = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    sbwf__cobe = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    lguz__jxkqe = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    edb__coyuc = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return iivau__zxvbn or sbwf__cobe or lguz__jxkqe or edb__coyuc


def args_td_and_int_array(lhs, rhs):
    hvel__oaj = (isinstance(lhs, IntegerArrayType) or isinstance(lhs, types
        .Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance(
        rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    cfghk__ubz = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return hvel__oaj and cfghk__ubz


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        ril__dnfcg = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        tpfsq__wpsgl = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        cbcvg__rxii = ril__dnfcg or tpfsq__wpsgl
        ius__cbbg = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        mbk__tdz = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        ldtro__miue = ius__cbbg or mbk__tdz
        jtocs__hdnd = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        mtvdx__agflu = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        xryyu__cid = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        fikzv__daocj = jtocs__hdnd or mtvdx__agflu or xryyu__cid
        pwueq__bpfa = isinstance(lhs, types.List) and isinstance(rhs, types
            .Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        rakma__qsuq = isinstance(lhs, tys) or isinstance(rhs, tys)
        zjo__hpml = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (cbcvg__rxii or ldtro__miue or fikzv__daocj or pwueq__bpfa or
            rakma__qsuq or zjo__hpml)
    if op == operator.pow:
        miw__fqmq = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        esma__opjec = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        xryyu__cid = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        zjo__hpml = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return miw__fqmq or esma__opjec or xryyu__cid or zjo__hpml
    if op == operator.floordiv:
        mtvdx__agflu = lhs in types.real_domain and rhs in types.real_domain
        jtocs__hdnd = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        zsn__quxv = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        ufcol__gpdjy = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        zjo__hpml = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (mtvdx__agflu or jtocs__hdnd or zsn__quxv or ufcol__gpdjy or
            zjo__hpml)
    if op == operator.truediv:
        vaqah__qbdg = lhs in machine_ints and rhs in machine_ints
        mtvdx__agflu = lhs in types.real_domain and rhs in types.real_domain
        xryyu__cid = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        jtocs__hdnd = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        zsn__quxv = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        fpva__wqpde = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ufcol__gpdjy = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        zjo__hpml = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (vaqah__qbdg or mtvdx__agflu or xryyu__cid or jtocs__hdnd or
            zsn__quxv or fpva__wqpde or ufcol__gpdjy or zjo__hpml)
    if op == operator.mod:
        vaqah__qbdg = lhs in machine_ints and rhs in machine_ints
        mtvdx__agflu = lhs in types.real_domain and rhs in types.real_domain
        jtocs__hdnd = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        zsn__quxv = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        zjo__hpml = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (vaqah__qbdg or mtvdx__agflu or jtocs__hdnd or zsn__quxv or
            zjo__hpml)
    if op == operator.add or op == operator.sub:
        cbcvg__rxii = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        uznu__ilix = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        gbuxa__rfv = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        xao__grqb = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        jtocs__hdnd = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        mtvdx__agflu = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        xryyu__cid = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        fikzv__daocj = jtocs__hdnd or mtvdx__agflu or xryyu__cid
        zjo__hpml = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        ajvpu__meap = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        pwueq__bpfa = isinstance(lhs, types.List) and isinstance(rhs, types
            .List)
        xgh__rrnj = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        jemjj__wdt = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        ipyjf__qgqne = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs
            , types.UnicodeCharSeq)
        nmd__kcu = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        kahg__eks = xgh__rrnj or jemjj__wdt or ipyjf__qgqne or nmd__kcu
        ldtro__miue = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        ahgzf__lta = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        nqnen__maikl = ldtro__miue or ahgzf__lta
        xxi__ngjak = lhs == types.NPTimedelta and rhs == types.NPDatetime
        zff__orenl = (ajvpu__meap or pwueq__bpfa or kahg__eks or
            nqnen__maikl or xxi__ngjak)
        msfyr__axgqk = op == operator.add and zff__orenl
        return (cbcvg__rxii or uznu__ilix or gbuxa__rfv or xao__grqb or
            fikzv__daocj or zjo__hpml or msfyr__axgqk)


def cmp_op_supported_by_numba(lhs, rhs):
    zjo__hpml = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    pwueq__bpfa = isinstance(lhs, types.ListType) and isinstance(rhs, types
        .ListType)
    cbcvg__rxii = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    uodp__snyww = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    ldtro__miue = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    ajvpu__meap = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
        types.BaseTuple)
    xao__grqb = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    fikzv__daocj = isinstance(lhs, types.Number) and isinstance(rhs, types.
        Number)
    ywb__tlml = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    flbx__vaau = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    qktrx__jqf = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    yuwtd__grh = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    jfyj__vaie = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (pwueq__bpfa or cbcvg__rxii or uodp__snyww or ldtro__miue or
        ajvpu__meap or xao__grqb or fikzv__daocj or ywb__tlml or flbx__vaau or
        qktrx__jqf or zjo__hpml or yuwtd__grh or jfyj__vaie)


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
        qnfp__hxxbp = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(qnfp__hxxbp)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        qnfp__hxxbp = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(qnfp__hxxbp)


install_arith_ops()
