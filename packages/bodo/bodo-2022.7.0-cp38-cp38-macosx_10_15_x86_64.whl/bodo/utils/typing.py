"""
Helper functions to enable typing.
"""
import copy
import itertools
import operator
import types as pytypes
import warnings
from inspect import getfullargspec
import numba
import numba.cpython.unicode
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, ir_utils, types
from numba.core.errors import NumbaError
from numba.core.imputils import RefType, iternext_impl
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, signature
from numba.extending import NativeValue, box, infer, intrinsic, lower_builtin, lower_cast, models, overload, overload_attribute, overload_method, register_jitable, register_model, unbox
import bodo
CONST_DICT_SENTINEL = '$_bodo_const_dict_$'
INDEX_SENTINEL = '$_bodo_index_'
list_cumulative = {'cumsum', 'cumprod', 'cummin', 'cummax'}


def is_timedelta_type(in_type):
    return in_type in [bodo.hiframes.datetime_timedelta_ext.
        pd_timedelta_type, bodo.hiframes.datetime_date_ext.
        datetime_timedelta_type]


def is_dtype_nullable(in_dtype):
    return isinstance(in_dtype, (types.Float, types.NPDatetime, types.
        NPTimedelta))


def is_nullable(typ):
    return bodo.utils.utils.is_array_typ(typ, False) and (not isinstance(
        typ, types.Array) or is_dtype_nullable(typ.dtype))


def is_str_arr_type(t):
    return t == bodo.string_array_type or t == bodo.dict_str_arr_type


def type_has_unknown_cats(typ):
    return isinstance(typ, bodo.CategoricalArrayType
        ) and typ.dtype.categories is None or isinstance(typ, bodo.TableType
        ) and any(type_has_unknown_cats(t) for t in typ.type_to_blk.keys())


def unwrap_typeref(typ):
    return typ.instance_type if isinstance(typ, types.TypeRef) else typ


def decode_if_dict_array(A):
    return A


@overload(decode_if_dict_array)
def decode_if_dict_array_overload(A):
    if isinstance(A, types.BaseTuple):
        irex__czefj = len(A.types)
        esdg__qgebo = 'def f(A):\n'
        rfpjx__dttz = ','.join(f'decode_if_dict_array(A[{i}])' for i in
            range(irex__czefj))
        esdg__qgebo += '  return ({}{})\n'.format(rfpjx__dttz, ',' if 
            irex__czefj == 1 else '')
        gfwy__xhq = {}
        exec(esdg__qgebo, {'decode_if_dict_array': decode_if_dict_array},
            gfwy__xhq)
        impl = gfwy__xhq['f']
        return impl
    if isinstance(A, types.List):

        def impl(A):
            irex__czefj = 0
            for a in A:
                irex__czefj += 1
            eehau__fcb = []
            for i in range(irex__czefj):
                eehau__fcb.append(decode_if_dict_array(A[i]))
            return eehau__fcb
        return impl
    if A == bodo.dict_str_arr_type:
        return lambda A: A._decode()
    if isinstance(A, bodo.SeriesType):

        def impl(A):
            kroxd__epvff = bodo.hiframes.pd_series_ext.get_series_data(A)
            behr__polhq = bodo.hiframes.pd_series_ext.get_series_index(A)
            name = bodo.hiframes.pd_series_ext.get_series_name(A)
            ukc__xrsa = decode_if_dict_array(kroxd__epvff)
            return bodo.hiframes.pd_series_ext.init_series(ukc__xrsa,
                behr__polhq, name)
        return impl
    if isinstance(A, bodo.DataFrameType):
        if A.is_table_format:
            gag__hfif = (
                'bodo.hiframes.table.decode_if_dict_table(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(A))'
                )
        else:
            gag__hfif = ', '.join(
                f'decode_if_dict_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(A, {i}))'
                 for i in range(len(A.columns)))
        impl = bodo.hiframes.dataframe_impl._gen_init_df('def impl(A):\n',
            A.columns, gag__hfif,
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(A)',
            extra_globals={'decode_if_dict_array': decode_if_dict_array,
            'bodo': bodo})
        return impl
    return lambda A: A


def to_str_arr_if_dict_array(t):
    if t == bodo.dict_str_arr_type:
        return bodo.string_array_type
    if isinstance(t, types.BaseTuple):
        return types.BaseTuple.from_types([to_str_arr_if_dict_array(a) for
            a in t.types])
    if isinstance(t, bodo.TableType):
        oig__gjvt = tuple(to_str_arr_if_dict_array(t) for t in t.arr_types)
        return bodo.TableType(oig__gjvt, t.has_runtime_cols)
    if isinstance(t, bodo.DataFrameType):
        return t.copy(data=tuple(to_str_arr_if_dict_array(t) for t in t.data))
    return t


class BodoError(NumbaError):

    def __init__(self, msg, loc=None, locs_in_msg=None):
        if locs_in_msg is None:
            self.locs_in_msg = []
        else:
            self.locs_in_msg = locs_in_msg
        cxps__rggrw = numba.core.errors.termcolor().errmsg
        super(BodoError, self).__init__(cxps__rggrw(msg), loc)


class BodoException(numba.core.errors.TypingError):
    pass


class BodoConstUpdatedError(Exception):
    pass


def raise_bodo_error(msg, loc=None):
    if bodo.transforms.typing_pass.in_partial_typing:
        bodo.transforms.typing_pass.typing_transform_required = True
        raise BodoException(msg)
    else:
        mjut__jjw = [] if loc is None else [loc]
        raise BodoError(msg, locs_in_msg=mjut__jjw)


class BodoWarning(Warning):
    pass


def get_udf_error_msg(context_str, error):
    msg = ''
    if hasattr(error, 'msg'):
        msg = str(error.msg)
    if hasattr(error, 'args') and error.args:
        msg = str(error.args[0])
    loc = ''
    if hasattr(error, 'loc') and error.loc is not None:
        loc = error.loc.strformat()
    return f'{context_str}: user-defined function not supported: {msg}\n{loc}'


class FileInfo:

    def __init__(self):
        self._concat_str = None
        self._concat_left = None

    def get_schema(self, fname):
        pafjd__wbegx = self.get_full_filename(fname)
        return self._get_schema(pafjd__wbegx)

    def set_concat(self, concat_str, is_left):
        self._concat_str = concat_str
        self._concat_left = is_left

    def _get_schema(self, fname):
        raise NotImplementedError

    def get_full_filename(self, fname):
        if self._concat_str is None:
            return fname
        if self._concat_left:
            return self._concat_str + fname
        return fname + self._concat_str


class FilenameType(types.Literal):

    def __init__(self, fname, finfo):
        self.fname = fname
        self._schema = finfo.get_schema(fname)
        super(FilenameType, self).__init__(self.fname)

    def __hash__(self):
        return 37

    def __eq__(self, other):
        if isinstance(other, types.FilenameType):
            assert self._schema is not None
            assert other._schema is not None
            return bodo.typeof(self.fname) == bodo.typeof(other.fname
                ) and self._schema == other._schema
        else:
            return False

    @property
    def schema(self):
        return copy.deepcopy(self._schema)


types.FilenameType = FilenameType


@register_model(types.FilenameType)
class FilenameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vdmc__bnhyk = dmm.lookup(bodo.typeof(fe_type.fname))
        ijo__qwx = [(a, uii__qho) for a, uii__qho in zip(vdmc__bnhyk.
            _fields, vdmc__bnhyk._members)]
        super().__init__(dmm, fe_type, ijo__qwx)


@unbox(FilenameType)
def unbox_file_name_type(typ, obj, c):
    return c.unbox(bodo.typeof(typ.fname), obj)


@lower_cast(types.FilenameType, types.unicode_type)
@lower_cast(types.FilenameType, types.List)
def cast_filename_to_unicode(context, builder, fromty, toty, val):
    return val


@box(FilenameType)
def box_filename_type(typ, val, c):
    return c.box(bodo.typeof(typ.fname), val)


class NotConstant:
    pass


NOT_CONSTANT = NotConstant()


def is_overload_none(val):
    return val is None or val == types.none or getattr(val, 'value', False
        ) is None


def is_overload_constant_bool(val):
    return isinstance(val, bool) or isinstance(val, types.BooleanLiteral
        ) or isinstance(val, types.Omitted) and isinstance(val.value, bool)


def is_overload_bool(val):
    return isinstance(val, types.Boolean) or is_overload_constant_bool(val)


def is_overload_constant_str(val):
    return isinstance(val, str) or isinstance(val, types.StringLiteral
        ) and isinstance(val.literal_value, str) or isinstance(val, types.
        Omitted) and isinstance(val.value, str)


def is_overload_constant_bytes(val):
    return isinstance(val, bytes) or isinstance(val, types.Omitted
        ) and isinstance(val.value, bytes)


def is_overload_constant_list(val):
    return isinstance(val, (list, tuple)) or isinstance(val, types.Omitted
        ) and isinstance(val.value, tuple) or is_initial_value_list_type(val
        ) or isinstance(val, types.LiteralList) or isinstance(val, bodo.
        utils.typing.ListLiteral) or isinstance(val, types.BaseTuple) and all(
        is_literal_type(t) for t in val.types) and (not val.types or val.
        types[0] != types.StringLiteral(CONST_DICT_SENTINEL))


def is_overload_constant_tuple(val):
    return isinstance(val, tuple) or isinstance(val, types.Omitted
        ) and isinstance(val.value, tuple) or isinstance(val, types.BaseTuple
        ) and all(get_overload_const(t) is not NOT_CONSTANT for t in val.types)


def is_initial_value_type(t):
    if not isinstance(t, types.InitialValue) or t.initial_value is None:
        return False
    ovfxr__zhvb = t.initial_value
    if isinstance(ovfxr__zhvb, dict):
        ovfxr__zhvb = ovfxr__zhvb.values()
    return not any(isinstance(vgn__cuh, (types.Poison, numba.core.
        interpreter._UNKNOWN_VALUE)) for vgn__cuh in ovfxr__zhvb)


def is_initial_value_list_type(t):
    return isinstance(t, types.List) and is_initial_value_type(t)


def is_initial_value_dict_type(t):
    return isinstance(t, types.DictType) and is_initial_value_type(t)


def is_overload_constant_dict(val):
    return isinstance(val, types.LiteralStrKeyDict) and all(is_literal_type
        (vgn__cuh) for vgn__cuh in val.types) or is_initial_value_dict_type(val
        ) or isinstance(val, DictLiteral) or isinstance(val, types.BaseTuple
        ) and val.types and val.types[0] == types.StringLiteral(
        CONST_DICT_SENTINEL) or isinstance(val, dict)


def is_overload_constant_number(val):
    return is_overload_constant_int(val) or is_overload_constant_float(val)


def is_overload_constant_nan(val):
    return is_overload_constant_float(val) and np.isnan(
        get_overload_const_float(val))


def is_overload_constant_float(val):
    return isinstance(val, float) or isinstance(val, types.Omitted
        ) and isinstance(val.value, float)


def is_overload_int(val):
    return is_overload_constant_int(val) or isinstance(val, types.Integer)


def is_overload_constant_int(val):
    return isinstance(val, int) or isinstance(val, types.IntegerLiteral
        ) and isinstance(val.literal_value, int) or isinstance(val, types.
        Omitted) and isinstance(val.value, int)


def is_overload_bool_list(val):
    return is_overload_constant_list(val) and all(is_overload_constant_bool
        (vgn__cuh) for vgn__cuh in get_overload_const_list(val))


def is_overload_true(val):
    return val == True or val == types.BooleanLiteral(True) or getattr(val,
        'value', False) is True


def is_overload_false(val):
    return val == False or val == types.BooleanLiteral(False) or getattr(val,
        'value', True) is False


def is_overload_zero(val):
    return val == 0 or val == types.IntegerLiteral(0) or getattr(val,
        'value', -1) == 0


def is_overload_str(val, const):
    return val == const or val == types.StringLiteral(const) or getattr(val,
        'value', -1) == const


def get_overload_const(val):
    from bodo.hiframes.datetime_timedelta_ext import _no_input
    if isinstance(val, types.TypeRef):
        val = val.instance_type
    if val == types.none:
        return None
    if val is _no_input:
        return _no_input
    if val is None or isinstance(val, (bool, int, float, str, tuple, types.
        Dispatcher)):
        return val
    if isinstance(val, types.Omitted):
        return val.value
    if isinstance(val, types.LiteralList):
        yxug__qpckr = []
        for vgn__cuh in val.literal_value:
            ycqk__sico = get_overload_const(vgn__cuh)
            if ycqk__sico == NOT_CONSTANT:
                return NOT_CONSTANT
            else:
                yxug__qpckr.append(ycqk__sico)
        return yxug__qpckr
    if isinstance(val, types.Literal):
        return val.literal_value
    if isinstance(val, types.Dispatcher):
        return val
    if isinstance(val, types.BaseTuple):
        yxug__qpckr = []
        for vgn__cuh in val.types:
            ycqk__sico = get_overload_const(vgn__cuh)
            if ycqk__sico == NOT_CONSTANT:
                return NOT_CONSTANT
            else:
                yxug__qpckr.append(ycqk__sico)
        return tuple(yxug__qpckr)
    if is_initial_value_list_type(val):
        return val.initial_value
    if is_literal_type(val):
        return get_literal_value(val)
    return NOT_CONSTANT


def element_type(val):
    if isinstance(val, (types.List, types.ArrayCompatible)):
        if isinstance(val.dtype, bodo.hiframes.pd_categorical_ext.
            PDCategoricalDtype):
            return val.dtype.elem_type
        if val == bodo.bytes_type:
            return bodo.bytes_type
        return val.dtype
    return types.unliteral(val)


def can_replace(to_replace, value):
    return is_common_scalar_dtype([to_replace, value]) and not (isinstance(
        to_replace, types.Integer) and isinstance(value, types.Float)
        ) and not (isinstance(to_replace, types.Boolean) and isinstance(
        value, (types.Integer, types.Float)))


_const_type_repr = {str: 'string', bool: 'boolean', int: 'integer'}


def ensure_constant_arg(fname, arg_name, val, const_type):
    ycqk__sico = get_overload_const(val)
    wtbuv__gqisv = _const_type_repr.get(const_type, str(const_type))
    if not isinstance(ycqk__sico, const_type):
        raise BodoError(
            f"{fname}(): argument '{arg_name}' should be a constant {wtbuv__gqisv} not {val}"
            )


def ensure_constant_values(fname, arg_name, val, const_values):
    ycqk__sico = get_overload_const(val)
    if ycqk__sico not in const_values:
        raise BodoError(
            f"{fname}(): argument '{arg_name}' should be a constant value in {const_values} not '{ycqk__sico}'"
            )


def check_unsupported_args(fname, args_dict, arg_defaults_dict,
    package_name='pandas', fn_str=None, module_name=''):
    from bodo.hiframes.datetime_timedelta_ext import _no_input
    assert len(args_dict) == len(arg_defaults_dict)
    if fn_str == None:
        fn_str = f'{fname}()'
    bfep__nek = ''
    dvzg__zydfa = False
    for a in args_dict:
        kjwad__hemim = get_overload_const(args_dict[a])
        ghk__oewsu = arg_defaults_dict[a]
        if (kjwad__hemim is NOT_CONSTANT or kjwad__hemim is not None and 
            ghk__oewsu is None or kjwad__hemim is None and ghk__oewsu is not
            None or kjwad__hemim != ghk__oewsu or kjwad__hemim is not
            _no_input and ghk__oewsu is _no_input or kjwad__hemim is
            _no_input and ghk__oewsu is not _no_input):
            bfep__nek = (
                f'{fn_str}: {a} parameter only supports default value {ghk__oewsu}'
                )
            dvzg__zydfa = True
            break
    if dvzg__zydfa and package_name == 'pandas':
        if module_name == 'IO':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/io/).
"""
        elif module_name == 'General':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/general/).
"""
        elif module_name == 'DataFrame':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/dataframe/).
"""
        elif module_name == 'Window':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/window/).
"""
        elif module_name == 'GroupBy':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/groupby/).
"""
        elif module_name == 'Series':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/series/).
"""
        elif module_name == 'HeterogeneousSeries':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/series/#heterogeneous_series).
"""
        elif module_name == 'Index':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/indexapi/).
"""
        elif module_name == 'Timestamp':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/timestamp/).
"""
        elif module_name == 'Timedelta':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/timedelta/).
"""
        elif module_name == 'DateOffsets':
            bfep__nek += """
Please check supported Pandas operations here (https://docs.bodo.ai/latest/api_docs/pandas/dateoffsets/).
"""
    elif dvzg__zydfa and package_name == 'ml':
        bfep__nek += """
Please check supported ML operations here (https://docs.bodo.ai/latest/api_docs/ml/).
"""
    elif dvzg__zydfa and package_name == 'numpy':
        bfep__nek += """
Please check supported Numpy operations here (https://docs.bodo.ai/latest/api_docs/numpy/).
"""
    if dvzg__zydfa:
        raise BodoError(bfep__nek)


def get_overload_const_tuple(val):
    if isinstance(val, tuple):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, tuple)
        return val.value
    if isinstance(val, types.BaseTuple):
        return tuple(get_overload_const(t) for t in val.types)


def get_overload_constant_dict(val):
    if isinstance(val, types.LiteralStrKeyDict):
        return {get_literal_value(qmn__vixt): get_literal_value(vgn__cuh) for
            qmn__vixt, vgn__cuh in val.literal_value.items()}
    if isinstance(val, DictLiteral):
        return val.literal_value
    if isinstance(val, dict):
        return val
    assert is_initial_value_dict_type(val) or isinstance(val, types.BaseTuple
        ) and val.types and val.types[0] == types.StringLiteral(
        CONST_DICT_SENTINEL), 'invalid const dict'
    if isinstance(val, types.DictType):
        assert val.initial_value is not None, 'invalid dict initial value'
        return val.initial_value
    lxh__ojk = [get_overload_const(vgn__cuh) for vgn__cuh in val.types[1:]]
    return {lxh__ojk[2 * i]: lxh__ojk[2 * i + 1] for i in range(len(
        lxh__ojk) // 2)}


def get_overload_const_str_len(val):
    if isinstance(val, str):
        return len(val)
    if isinstance(val, types.StringLiteral) and isinstance(val.
        literal_value, str):
        return len(val.literal_value)
    if isinstance(val, types.Omitted) and isinstance(val.value, str):
        return len(val.value)


def get_overload_const_list(val):
    if isinstance(val, (list, tuple)):
        return val
    if isinstance(val, types.Omitted) and isinstance(val.value, tuple):
        return val.value
    if is_initial_value_list_type(val):
        return val.initial_value
    if isinstance(val, types.LiteralList):
        return [get_literal_value(vgn__cuh) for vgn__cuh in val.literal_value]
    if isinstance(val, bodo.utils.typing.ListLiteral):
        return val.literal_value
    if isinstance(val, types.Omitted):
        return [val.value]
    if isinstance(val, types.Literal):
        return [val.literal_value]
    if isinstance(val, types.BaseTuple) and all(is_literal_type(t) for t in
        val.types):
        return tuple(get_literal_value(t) for t in val.types)


def get_overload_const_str(val):
    if isinstance(val, str):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, str)
        return val.value
    if isinstance(val, types.StringLiteral):
        assert isinstance(val.literal_value, str)
        return val.literal_value
    raise BodoError('{} not constant string'.format(val))


def get_overload_const_bytes(val):
    if isinstance(val, bytes):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, bytes)
        return val.value
    raise BodoError('{} not constant binary'.format(val))


def get_overload_const_int(val):
    if isinstance(val, int):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, int)
        return val.value
    if isinstance(val, types.IntegerLiteral):
        assert isinstance(val.literal_value, int)
        return val.literal_value
    raise BodoError('{} not constant integer'.format(val))


def get_overload_const_float(val):
    if isinstance(val, float):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, float)
        return val.value
    raise BodoError('{} not constant float'.format(val))


def get_overload_const_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, types.Omitted):
        assert isinstance(val.value, bool)
        return val.value
    if isinstance(val, types.BooleanLiteral):
        assert isinstance(val.literal_value, bool)
        return val.literal_value
    raise BodoError('{} not constant boolean'.format(val))


def is_const_func_type(t):
    return isinstance(t, (types.MakeFunctionLiteral, bodo.utils.typing.
        FunctionLiteral, types.Dispatcher))


def get_overload_const_func(val, func_ir):
    if isinstance(val, (types.MakeFunctionLiteral, bodo.utils.typing.
        FunctionLiteral)):
        func = val.literal_value
        if isinstance(func, ir.Expr) and func.op == 'make_function':
            assert func_ir is not None, 'Function expression is make_function but there is no existing IR'
            func = numba.core.ir_utils.convert_code_obj_to_function(func,
                func_ir)
        return func
    if isinstance(val, types.Dispatcher):
        return val.dispatcher.py_func
    if isinstance(val, CPUDispatcher):
        return val.py_func
    raise BodoError("'{}' not a constant function type".format(val))


def is_heterogeneous_tuple_type(t):
    if is_overload_constant_list(t):
        if isinstance(t, types.LiteralList):
            t = types.BaseTuple.from_types(t.types)
        else:
            t = bodo.typeof(tuple(get_overload_const_list(t)))
    if isinstance(t, bodo.NullableTupleType):
        t = t.tuple_typ
    return isinstance(t, types.BaseTuple) and not isinstance(t, types.UniTuple)


def parse_dtype(dtype, func_name=None):
    if isinstance(dtype, types.TypeRef):
        return dtype.instance_type
    if isinstance(dtype, types.Function):
        if dtype.key[0] == float:
            dtype = types.StringLiteral('float')
        elif dtype.key[0] == int:
            dtype = types.StringLiteral('int')
        elif dtype.key[0] == bool:
            dtype = types.StringLiteral('bool')
        elif dtype.key[0] == str:
            dtype = bodo.string_type
    if type(dtype) in bodo.libs.int_arr_ext.pd_int_dtype_classes:
        dtype = types.StringLiteral(dtype.name)
    if isinstance(dtype, types.DTypeSpec):
        return dtype.dtype
    if isinstance(dtype, types.Number) or dtype == bodo.string_type:
        return dtype
    try:
        dsl__dxvw = get_overload_const_str(dtype)
        if dsl__dxvw.startswith('Int') or dsl__dxvw.startswith('UInt'):
            return bodo.libs.int_arr_ext.typeof_pd_int_dtype(pd.api.types.
                pandas_dtype(dsl__dxvw), None)
        if dsl__dxvw == 'boolean':
            return bodo.libs.bool_arr_ext.boolean_dtype
        if dsl__dxvw == 'str':
            return bodo.string_type
        return numba.np.numpy_support.from_dtype(np.dtype(dsl__dxvw))
    except:
        pass
    if func_name is not None:
        raise BodoError(f'{func_name}(): invalid dtype {dtype}')
    else:
        raise BodoError(f'invalid dtype {dtype}')


def is_list_like_index_type(t):
    from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.libs.bool_arr_ext import boolean_array
    return isinstance(t, types.List) or isinstance(t, types.Array
        ) and t.ndim == 1 or isinstance(t, (NumericIndexType, RangeIndexType)
        ) or isinstance(t, SeriesType) or t == boolean_array


def is_tuple_like_type(t):
    return isinstance(t, types.BaseTuple) or is_heterogeneous_tuple_type(t
        ) or isinstance(t, bodo.hiframes.pd_index_ext.HeterogeneousIndexType)


def get_index_names(t, func_name, default_name):
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    htgrd__yurac = '{}: index name should be a constant string'.format(
        func_name)
    if isinstance(t, MultiIndexType):
        mxd__erghk = []
        for i, riy__pnr in enumerate(t.names_typ):
            if riy__pnr == types.none:
                mxd__erghk.append('level_{}'.format(i))
                continue
            if not is_overload_constant_str(riy__pnr):
                raise BodoError(htgrd__yurac)
            mxd__erghk.append(get_overload_const_str(riy__pnr))
        return tuple(mxd__erghk)
    if t.name_typ == types.none:
        return default_name,
    if not is_overload_constant_str(t.name_typ):
        raise BodoError(htgrd__yurac)
    return get_overload_const_str(t.name_typ),


def get_index_data_arr_types(t):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, IntervalIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    if isinstance(t, MultiIndexType):
        return tuple(t.array_types)
    if isinstance(t, (RangeIndexType, PeriodIndexType)):
        return types.Array(types.int64, 1, 'C'),
    if isinstance(t, (NumericIndexType, StringIndexType, BinaryIndexType,
        DatetimeIndexType, TimedeltaIndexType, CategoricalIndexType,
        IntervalIndexType)):
        return t.data,
    raise BodoError(f'Invalid index type {t}')


def to_numeric_index_if_range_index(t):
    from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
    return NumericIndexType(types.int64, t.name_typ) if isinstance(t,
        RangeIndexType) else t


def get_index_type_from_dtype(t):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, StringIndexType, TimedeltaIndexType
    if t in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type, bodo.
        datetime64ns, bodo.datetime_date_type]:
        return DatetimeIndexType(types.none)
    if isinstance(t, bodo.hiframes.pd_timestamp_ext.PandasTimestampType
        ) and t.tz is not None:
        return DatetimeIndexType(types.none, bodo.libs.pd_datetime_arr_ext.
            DatetimeArrayType(t.tz))
    if t in [bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type, bodo.
        timedelta64ns]:
        return TimedeltaIndexType(types.none)
    if t == bodo.string_type:
        return StringIndexType(types.none)
    if t == bodo.bytes_type:
        return BinaryIndexType(types.none)
    if isinstance(t, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(t, types.none)
    if isinstance(t, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        return CategoricalIndexType(bodo.CategoricalArrayType(t))
    raise BodoError(f'Cannot convert dtype {t} to index type')


def get_val_type_maybe_str_literal(value):
    t = numba.typeof(value)
    if isinstance(value, str):
        t = types.StringLiteral(value)
    return t


def get_index_name_types(t):
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    if isinstance(t, MultiIndexType):
        return t.names_typ
    return t.name_typ,


if types.SliceLiteral in numba.core.pythonapi._boxers.functions:
    warnings.warn('SliceLiteral boxing has been implemented in Numba')
else:

    @box(types.SliceLiteral)
    def box_slice_literal(typ, val, c):
        lia__zcsgw = typ.literal_value
        udwny__jsxw = []
        for gjqt__bxf in ('start', 'stop', 'step'):
            ctom__qeyk = getattr(typ.literal_value, gjqt__bxf)
            uqosd__nthej = c.pyapi.make_none(
                ) if ctom__qeyk is None else c.pyapi.from_native_value(types
                .literal(ctom__qeyk), ctom__qeyk, c.env_manager)
            udwny__jsxw.append(uqosd__nthej)
        rsd__nsyxa = c.pyapi.unserialize(c.pyapi.serialize_object(slice))
        wqll__bseb = c.pyapi.call_function_objargs(rsd__nsyxa, udwny__jsxw)
        for a in udwny__jsxw:
            c.pyapi.decref(a)
        c.pyapi.decref(rsd__nsyxa)
        return wqll__bseb


class ListLiteral(types.Literal):
    pass


types.Literal.ctor_map[list] = ListLiteral
register_model(ListLiteral)(models.OpaqueModel)


@unbox(ListLiteral)
def unbox_list_literal(typ, obj, c):
    return NativeValue(c.context.get_dummy_value())


@box(ListLiteral)
def box_list_literal(typ, val, c):
    goks__oozcs = typ.literal_value
    ujp__vrk = [c.pyapi.from_native_value(types.literal(vgn__cuh), vgn__cuh,
        c.env_manager) for vgn__cuh in goks__oozcs]
    zrbjt__yrh = c.pyapi.list_pack(ujp__vrk)
    for a in ujp__vrk:
        c.pyapi.decref(a)
    return zrbjt__yrh


@lower_cast(ListLiteral, types.List)
def list_literal_to_list(context, builder, fromty, toty, val):
    list_vals = tuple(fromty.literal_value)
    kwk__oxmhr = types.List(toty.dtype)
    return context.compile_internal(builder, lambda : list(list_vals),
        kwk__oxmhr(), [])


class DictLiteral(types.Literal):
    pass


types.Literal.ctor_map[dict] = DictLiteral
register_model(DictLiteral)(models.OpaqueModel)


@unbox(DictLiteral)
def unbox_dict_literal(typ, obj, c):
    return NativeValue(c.context.get_dummy_value())


class FunctionLiteral(types.Literal, types.Opaque):
    pass


types.Literal.ctor_map[pytypes.FunctionType] = FunctionLiteral
register_model(FunctionLiteral)(models.OpaqueModel)


@unbox(FunctionLiteral)
def unbox_func_literal(typ, obj, c):
    return NativeValue(obj)


types.MakeFunctionLiteral._literal_type_cache = types.MakeFunctionLiteral(
    lambda : 0)


class MetaType(types.Type):

    def __init__(self, meta):
        self.meta = meta
        super(MetaType, self).__init__('MetaType({})'.format(meta))

    def can_convert_from(self, typingctx, other):
        return True

    @property
    def key(self):
        return tuple(self.meta)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def __len__(self):
        return len(self.meta)


register_model(MetaType)(models.OpaqueModel)


class ColNamesMetaType(MetaType):

    def __init__(self, meta):
        self.meta = meta
        types.Type.__init__(self, f'ColNamesMetaType({meta})')


register_model(ColNamesMetaType)(models.OpaqueModel)


def is_literal_type(t):
    if isinstance(t, types.TypeRef):
        t = t.instance_type
    return isinstance(t, (types.Literal, types.Omitted)) and not isinstance(t,
        types.LiteralStrKeyDict) or t == types.none or isinstance(t, types.
        Dispatcher) or isinstance(t, types.BaseTuple) and all(
        is_literal_type(vgn__cuh) for vgn__cuh in t.types
        ) or is_initial_value_type(t) or isinstance(t, (types.DTypeSpec,
        types.Function)) or isinstance(t, bodo.libs.int_arr_ext.IntDtype
        ) or t in (bodo.libs.bool_arr_ext.boolean_dtype, bodo.libs.
        str_arr_ext.string_dtype) or isinstance(t, types.Function
        ) or is_overload_constant_index(t) or is_overload_constant_series(t
        ) or is_overload_constant_dict(t)


def is_overload_constant_index(t):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    return isinstance(t, HeterogeneousIndexType) and is_literal_type(t.data
        ) and is_literal_type(t.name_typ)


def get_overload_constant_index(t):
    assert is_overload_constant_index(t)
    return pd.Index(get_literal_value(t.data), name=get_literal_value(t.
        name_typ))


def is_overload_constant_series(t):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    return isinstance(t, (SeriesType, HeterogeneousSeriesType)
        ) and is_literal_type(t.data) and is_literal_type(t.index
        ) and is_literal_type(t.name_typ)


def get_overload_constant_series(t):
    assert is_overload_constant_series(t)
    return pd.Series(get_literal_value(t.data), get_literal_value(t.index),
        name=get_literal_value(t.name_typ))


def get_literal_value(t):
    if isinstance(t, types.TypeRef):
        t = t.instance_type
    assert is_literal_type(t)
    if t == types.none:
        return None
    if isinstance(t, types.Literal):
        if isinstance(t, types.LiteralStrKeyDict):
            return {get_literal_value(qmn__vixt): get_literal_value(
                vgn__cuh) for qmn__vixt, vgn__cuh in t.literal_value.items()}
        if isinstance(t, types.LiteralList):
            return [get_literal_value(vgn__cuh) for vgn__cuh in t.literal_value
                ]
        return t.literal_value
    if isinstance(t, types.Omitted):
        return t.value
    if isinstance(t, types.BaseTuple):
        return tuple(get_literal_value(vgn__cuh) for vgn__cuh in t.types)
    if isinstance(t, types.Dispatcher):
        return t
    if is_initial_value_type(t):
        return t.initial_value
    if isinstance(t, (types.DTypeSpec, types.Function)):
        return t
    if isinstance(t, bodo.libs.int_arr_ext.IntDtype):
        return getattr(pd, str(t)[:-2])()
    if t == bodo.libs.bool_arr_ext.boolean_dtype:
        return pd.BooleanDtype()
    if t == bodo.libs.str_arr_ext.string_dtype:
        return pd.StringDtype()
    if is_overload_constant_index(t):
        return get_overload_constant_index(t)
    if is_overload_constant_series(t):
        return get_overload_constant_series(t)
    if is_overload_constant_dict(t):
        return get_overload_constant_dict(t)


def can_literalize_type(t, pyobject_to_literal=False):
    return t in (bodo.string_type, types.bool_) or isinstance(t, (types.
        Integer, types.List, types.SliceType, types.DictType)
        ) or pyobject_to_literal and t == types.pyobject


def dtype_to_array_type(dtype):
    dtype = types.unliteral(dtype)
    if isinstance(dtype, types.List):
        dtype = dtype_to_array_type(dtype.dtype)
    kthh__tft = False
    if isinstance(dtype, types.Optional):
        dtype = dtype.type
        kthh__tft = True
    if dtype == bodo.string_type:
        return bodo.string_array_type
    if dtype == bodo.bytes_type:
        return bodo.binary_array_type
    if bodo.utils.utils.is_array_typ(dtype, False):
        return bodo.ArrayItemArrayType(dtype)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        return bodo.CategoricalArrayType(dtype)
    if isinstance(dtype, bodo.libs.int_arr_ext.IntDtype):
        return bodo.IntegerArrayType(dtype.dtype)
    if dtype == types.bool_:
        return bodo.boolean_array
    if dtype == bodo.datetime_date_type:
        return bodo.hiframes.datetime_date_ext.datetime_date_array_type
    if isinstance(dtype, bodo.Decimal128Type):
        return bodo.DecimalArrayType(dtype.precision, dtype.scale)
    if isinstance(dtype, bodo.libs.struct_arr_ext.StructType):
        return bodo.StructArrayType(tuple(dtype_to_array_type(t) for t in
            dtype.data), dtype.names)
    if isinstance(dtype, types.BaseTuple):
        return bodo.TupleArrayType(tuple(dtype_to_array_type(t) for t in
            dtype.types))
    if isinstance(dtype, types.DictType):
        return bodo.MapArrayType(dtype_to_array_type(dtype.key_type),
            dtype_to_array_type(dtype.value_type))
    if isinstance(dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype):
        return bodo.DatetimeArrayType(dtype.tz)
    if dtype in (bodo.pd_timestamp_type, bodo.hiframes.
        datetime_datetime_ext.datetime_datetime_type):
        return types.Array(bodo.datetime64ns, 1, 'C')
    if dtype in (bodo.pd_timedelta_type, bodo.hiframes.
        datetime_timedelta_ext.datetime_timedelta_type):
        return types.Array(bodo.timedelta64ns, 1, 'C')
    if isinstance(dtype, (types.Number, types.Boolean, types.NPDatetime,
        types.NPTimedelta)):
        kroxd__epvff = types.Array(dtype, 1, 'C')
        if kthh__tft:
            return to_nullable_type(kroxd__epvff)
        return kroxd__epvff
    raise BodoError(f'dtype {dtype} cannot be stored in arrays')


def get_udf_out_arr_type(f_return_type, return_nullable=False):
    if isinstance(f_return_type, types.Optional):
        f_return_type = f_return_type.type
        return_nullable = True
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(f_return_type,
        'Series.apply')
    if f_return_type == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        f_return_type = types.NPDatetime('ns')
    if f_return_type == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        f_return_type = types.NPTimedelta('ns')
    kjcbj__xajl = dtype_to_array_type(f_return_type)
    kjcbj__xajl = to_nullable_type(kjcbj__xajl
        ) if return_nullable else kjcbj__xajl
    return kjcbj__xajl


def equality_always_false(t1, t2):
    string_types = types.UnicodeType, types.StringLiteral, types.UnicodeCharSeq
    return isinstance(t1, string_types) and not isinstance(t2, string_types
        ) or isinstance(t2, string_types) and not isinstance(t1, string_types)


def types_equality_exists(t1, t2):
    jdqzr__qhduv = numba.core.registry.cpu_target.typing_context
    try:
        jdqzr__qhduv.resolve_function_type(operator.eq, (t1, t2), {})
        return True
    except:
        return False


def is_hashable_type(t):
    whitelist_types = (types.UnicodeType, types.StringLiteral, types.
        UnicodeCharSeq, types.Number, bodo.hiframes.pd_timestamp_ext.
        PandasTimestampType)
    dexy__thno = (types.bool_, bodo.datetime64ns, bodo.timedelta64ns, bodo.
        pd_timedelta_type)
    if isinstance(t, whitelist_types) or t in dexy__thno:
        return True
    jdqzr__qhduv = numba.core.registry.cpu_target.typing_context
    try:
        jdqzr__qhduv.resolve_function_type(hash, (t,), {})
        return True
    except:
        return False


def to_nullable_type(t):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(t, DataFrameType):
        xhw__bpd = tuple(to_nullable_type(t) for t in t.data)
        return DataFrameType(xhw__bpd, t.index, t.columns, t.dist, t.
            is_table_format)
    if isinstance(t, SeriesType):
        return SeriesType(t.dtype, to_nullable_type(t.data), t.index, t.
            name_typ)
    if isinstance(t, types.Array):
        if t.dtype == types.bool_:
            return bodo.libs.bool_arr_ext.boolean_array
        if isinstance(t.dtype, types.Integer):
            return bodo.libs.int_arr_ext.IntegerArrayType(t.dtype)
    return t


def is_nullable_type(t):
    return t == to_nullable_type(t)


def is_iterable_type(t):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    return bodo.utils.utils.is_array_typ(t, False) or isinstance(t, (
        SeriesType, DataFrameType, types.List, types.BaseTuple, types.
        LiteralList, types.RangeType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(t)


def is_scalar_type(t):
    return isinstance(t, (types.Boolean, types.Number, types.StringLiteral,
        bodo.hiframes.pd_timestamp_ext.PandasTimestampType)) or t in (bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, bodo.bytes_type,
        bodo.datetime_date_type, bodo.datetime_datetime_type, bodo.
        datetime_timedelta_type, bodo.pd_timedelta_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type, types.none)


def is_common_scalar_dtype(scalar_types):
    miyi__iij, ish__yefmz = get_common_scalar_dtype(scalar_types)
    return ish__yefmz


def get_common_scalar_dtype(scalar_types):
    scalar_types = [types.unliteral(a) for a in scalar_types]
    if len(scalar_types) == 0:
        raise_bodo_error(
            'Internal error, length of argument passed to get_common_scalar_dtype scalar_types is 0'
            )
    try:
        kmrxq__fwnlm = np.find_common_type([numba.np.numpy_support.as_dtype
            (t) for t in scalar_types], [])
        if kmrxq__fwnlm != object:
            return numba.np.numpy_support.from_dtype(kmrxq__fwnlm), True
    except numba.core.errors.NumbaNotImplementedError as bqd__yja:
        pass
    if scalar_types[0] in (bodo.datetime64ns, bodo.pd_timestamp_type):
        for typ in scalar_types[1:]:
            if typ not in (bodo.datetime64ns, bodo.pd_timestamp_type):
                return None, False
        return bodo.datetime64ns, True
    if scalar_types[0] in (bodo.timedelta64ns, bodo.pd_timedelta_type):
        for typ in scalar_types[1:]:
            if scalar_types[0] not in (bodo.timedelta64ns, bodo.
                pd_timedelta_type):
                return None, False
        return bodo.timedelta64ns, True
    fvk__cfcbn = itertools.groupby(scalar_types)
    if next(fvk__cfcbn, True) and not next(fvk__cfcbn, False):
        return scalar_types[0], True
    return None, False


def find_common_np_dtype(arr_types):
    return numba.np.numpy_support.from_dtype(np.find_common_type([numba.np.
        numpy_support.as_dtype(t.dtype) for t in arr_types], []))


def is_immutable_array(typ):
    return isinstance(typ, (bodo.ArrayItemArrayType, bodo.MapArrayType))


def get_nullable_and_non_nullable_types(array_of_types):
    jhesc__oeu = []
    for typ in array_of_types:
        if typ == bodo.libs.bool_arr_ext.boolean_array:
            jhesc__oeu.append(types.Array(types.bool_, 1, 'C'))
        elif isinstance(typ, bodo.libs.int_arr_ext.IntegerArrayType):
            jhesc__oeu.append(types.Array(typ.dtype, 1, 'C'))
        elif isinstance(typ, types.Array):
            if typ.dtype == types.bool_:
                jhesc__oeu.append(bodo.libs.bool_arr_ext.boolean_array)
            if isinstance(typ.dtype, types.Integer):
                jhesc__oeu.append(bodo.libs.int_arr_ext.IntegerArrayType(
                    typ.dtype))
        jhesc__oeu.append(typ)
    return jhesc__oeu


def is_np_arr_typ(t, dtype, ndim=1):
    return isinstance(t, types.Array) and t.dtype == dtype and t.ndim == ndim


def _gen_objmode_overload(func, output_type, attr_name=None, is_function=
    True, single_rank=False):
    if is_function:
        shsw__bisj = getfullargspec(func)
        assert shsw__bisj.varargs is None, 'varargs not supported'
        assert shsw__bisj.varkw is None, 'varkw not supported'
        defaults = [] if shsw__bisj.defaults is None else shsw__bisj.defaults
        ezo__tvq = len(shsw__bisj.args) - len(defaults)
        args = shsw__bisj.args[1:] if attr_name else shsw__bisj.args[:]
        nnud__iqw = []
        for i, vckci__hmos in enumerate(shsw__bisj.args):
            if i < ezo__tvq:
                nnud__iqw.append(vckci__hmos)
            elif str(defaults[i - ezo__tvq]) != '<deprecated parameter>':
                nnud__iqw.append(vckci__hmos + '=' + str(defaults[i -
                    ezo__tvq]))
            else:
                args.remove(vckci__hmos)
        if shsw__bisj.kwonlyargs is not None:
            for vckci__hmos in shsw__bisj.kwonlyargs:
                args.append(f'{vckci__hmos}={vckci__hmos}')
                nnud__iqw.append(
                    f'{vckci__hmos}={str(shsw__bisj.kwonlydefaults[vckci__hmos])}'
                    )
        sig = ', '.join(nnud__iqw)
        args = ', '.join(args)
    else:
        sig = 'self'
    type_name = str(output_type)
    if not hasattr(types, type_name):
        type_name = f'objmode_type{ir_utils.next_label()}'
        setattr(types, type_name, output_type)
    if not attr_name:
        func_name = func.__module__.replace('.', '_'
            ) + '_' + func.__name__ + '_func'
    rur__wwsls = f'self.{attr_name}' if attr_name else f'{func_name}'
    esdg__qgebo = f'def overload_impl({sig}):\n'
    esdg__qgebo += f'    def impl({sig}):\n'
    if single_rank:
        esdg__qgebo += f'        if bodo.get_rank() == 0:\n'
        hac__opq = '    '
    else:
        hac__opq = ''
    esdg__qgebo += (
        f"        {hac__opq}with numba.objmode(res='{type_name}'):\n")
    if is_function:
        esdg__qgebo += f'            {hac__opq}res = {rur__wwsls}({args})\n'
    else:
        esdg__qgebo += f'            {hac__opq}res = {rur__wwsls}\n'
    esdg__qgebo += f'        return res\n'
    esdg__qgebo += f'    return impl\n'
    gfwy__xhq = {}
    tnd__sxwf = globals()
    if not attr_name:
        tnd__sxwf[func_name] = func
    exec(esdg__qgebo, tnd__sxwf, gfwy__xhq)
    ryi__enj = gfwy__xhq['overload_impl']
    return ryi__enj


def gen_objmode_func_overload(func, output_type=None, single_rank=False):
    try:
        ryi__enj = _gen_objmode_overload(func, output_type, is_function=
            True, single_rank=single_rank)
        overload(func, no_unliteral=True)(ryi__enj)
    except Exception as bqd__yja:
        pass


def gen_objmode_method_overload(obj_type, method_name, method, output_type=
    None, single_rank=False):
    try:
        ryi__enj = _gen_objmode_overload(method, output_type, method_name, 
            True, single_rank)
        overload_method(obj_type, method_name, no_unliteral=True)(ryi__enj)
    except Exception as bqd__yja:
        pass


def gen_objmode_attr_overload(obj_type, attr_name, attr, output_type=None,
    single_rank=False):
    try:
        ryi__enj = _gen_objmode_overload(attr, output_type, attr_name, 
            False, single_rank)
        overload_attribute(obj_type, attr_name, no_unliteral=True)(ryi__enj)
    except Exception as bqd__yja:
        pass


@infer
class NumTypeStaticGetItem(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        val, zjwc__dvfed = args
        if isinstance(zjwc__dvfed, slice) and (isinstance(val, types.
            NumberClass) or isinstance(val, types.TypeRef) and isinstance(
            val.instance_type, (types.NPDatetime, types.NPTimedelta))):
            return signature(types.TypeRef(val.instance_type[zjwc__dvfed]),
                *args)


@lower_builtin('static_getitem', types.NumberClass, types.SliceLiteral)
def num_class_type_static_getitem(context, builder, sig, args):
    return context.get_dummy_value()


@overload(itertools.chain, no_unliteral=True)
def chain_overload():
    return lambda : [0]


@register_jitable
def from_iterable_impl(A):
    return bodo.utils.conversion.flatten_array(bodo.utils.conversion.
        coerce_to_array(A))


@intrinsic
def unliteral_val(typingctx, val=None):

    def codegen(context, builder, signature, args):
        return args[0]
    return types.unliteral(val)(val), codegen


def create_unsupported_overload(fname):

    def overload_f(*a, **kws):
        raise BodoError('{} not supported yet'.format(fname))
    return overload_f


def is_numpy_ufunc(func):
    return isinstance(func, types.Function) and isinstance(func.typing_key,
        np.ufunc)


def is_builtin_function(func):
    return isinstance(func, types.Function) and isinstance(func.typing_key,
        pytypes.BuiltinFunctionType)


def get_builtin_function_name(func):
    return func.typing_key.__name__


def construct_pysig(arg_names, defaults):
    esdg__qgebo = f'def stub('
    for vckci__hmos in arg_names:
        esdg__qgebo += vckci__hmos
        if vckci__hmos in defaults:
            if isinstance(defaults[vckci__hmos], str):
                esdg__qgebo += f"='{defaults[vckci__hmos]}'"
            else:
                esdg__qgebo += f'={defaults[vckci__hmos]}'
        esdg__qgebo += ', '
    esdg__qgebo += '):\n'
    esdg__qgebo += '    pass\n'
    gfwy__xhq = {}
    exec(esdg__qgebo, {}, gfwy__xhq)
    loz__euc = gfwy__xhq['stub']
    return numba.core.utils.pysignature(loz__euc)


def fold_typing_args(func_name, args, kws, arg_names, defaults,
    unsupported_arg_names=()):
    kws = dict(kws)
    huvw__lxco = len(arg_names)
    jvfpa__vpr = len(args) + len(kws)
    if jvfpa__vpr > huvw__lxco:
        hmexw__gzj = 'argument' if huvw__lxco == 1 else 'arguments'
        ojaj__kow = 'was' if jvfpa__vpr == 1 else 'were'
        raise BodoError(
            f'{func_name}(): Too many arguments specified. Function takes {huvw__lxco} {hmexw__gzj}, but {jvfpa__vpr} {ojaj__kow} provided.'
            )
    nwu__jwyq = bodo.utils.typing.construct_pysig(arg_names, defaults)
    try:
        klu__chnv = bodo.utils.transform.fold_argument_types(nwu__jwyq,
            args, kws)
    except Exception as xpps__thqe:
        raise_bodo_error(f'{func_name}(): {xpps__thqe}')
    if unsupported_arg_names:
        rzgrv__brjmk = {}
        zcalg__zii = {}
        for i, arg_name in enumerate(arg_names):
            if arg_name in unsupported_arg_names:
                assert arg_name in defaults, f"{func_name}(): '{arg_name}' is unsupported but no default is provided"
                rzgrv__brjmk[arg_name] = klu__chnv[i]
                zcalg__zii[arg_name] = defaults[arg_name]
        check_unsupported_args(func_name, rzgrv__brjmk, zcalg__zii)
    return nwu__jwyq, klu__chnv


def _is_pandas_numeric_dtype(dtype):
    return isinstance(dtype, types.Number) or dtype == types.bool_


def type_col_to_index(col_names):
    if all(isinstance(a, str) for a in col_names):
        return bodo.StringIndexType(None)
    elif all(isinstance(a, bytes) for a in col_names):
        return bodo.BinaryIndexType(None)
    elif all(isinstance(a, (int, float)) for a in col_names):
        if any(isinstance(a, float) for a in col_names):
            return bodo.NumericIndexType(types.float64)
        else:
            return bodo.NumericIndexType(types.int64)
    else:
        return bodo.hiframes.pd_index_ext.HeterogeneousIndexType(col_names)


class BodoArrayIterator(types.SimpleIteratorType):

    def __init__(self, arr_type, yield_type=None):
        self.arr_type = arr_type
        name = f'iter({arr_type})'
        if yield_type == None:
            yield_type = arr_type.dtype
        super(BodoArrayIterator, self).__init__(name, yield_type)


@register_model(BodoArrayIterator)
class BodoArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ijo__qwx = [('index', types.EphemeralPointer(types.uintp)), (
            'array', fe_type.arr_type)]
        super(BodoArrayIteratorModel, self).__init__(dmm, fe_type, ijo__qwx)


@lower_builtin('iternext', BodoArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_bodo_array(context, builder, sig, args, result):
    [ppez__nowy] = sig.args
    [zuent__tvrja] = args
    rrp__kfuy = context.make_helper(builder, ppez__nowy, value=zuent__tvrja)
    ctm__edk = signature(types.intp, ppez__nowy.arr_type)
    qid__ylzxs = context.compile_internal(builder, lambda a: len(a),
        ctm__edk, [rrp__kfuy.array])
    behr__polhq = builder.load(rrp__kfuy.index)
    yzzsw__vib = builder.icmp_signed('<', behr__polhq, qid__ylzxs)
    result.set_valid(yzzsw__vib)
    with builder.if_then(yzzsw__vib):
        zikcs__amx = signature(ppez__nowy.yield_type, ppez__nowy.arr_type,
            types.intp)
        value = context.compile_internal(builder, lambda a, i: a[i],
            zikcs__amx, [rrp__kfuy.array, behr__polhq])
        result.yield_(value)
        cjzv__iwdb = cgutils.increment_index(builder, behr__polhq)
        builder.store(cjzv__iwdb, rrp__kfuy.index)


def index_typ_from_dtype_name_arr(elem_dtype, name, arr_typ):
    hkh__nbly = type(get_index_type_from_dtype(elem_dtype))
    if name is None:
        iuzk__emss = None
    else:
        iuzk__emss = types.StringLiteral(name)
    if hkh__nbly == bodo.hiframes.pd_index_ext.NumericIndexType:
        huhjw__bfkc = hkh__nbly(elem_dtype, iuzk__emss, arr_typ)
    elif hkh__nbly == bodo.hiframes.pd_index_ext.CategoricalIndexType:
        huhjw__bfkc = hkh__nbly(bodo.CategoricalArrayType(elem_dtype),
            iuzk__emss, arr_typ)
    else:
        huhjw__bfkc = hkh__nbly(iuzk__emss, arr_typ)
    return huhjw__bfkc


def is_safe_arrow_cast(lhs_scalar_typ, rhs_scalar_typ):
    if lhs_scalar_typ == types.unicode_type:
        return rhs_scalar_typ in (bodo.datetime64ns, bodo.pd_timestamp_type)
    elif rhs_scalar_typ == types.unicode_type:
        return lhs_scalar_typ in (bodo.datetime64ns, bodo.pd_timestamp_type)
    elif lhs_scalar_typ == bodo.datetime_date_type:
        return rhs_scalar_typ in (bodo.datetime64ns, bodo.pd_timestamp_type)
    elif rhs_scalar_typ == bodo.datetime_date_type:
        return lhs_scalar_typ in (bodo.datetime64ns, bodo.pd_timestamp_type)
    return False


def register_type(type_name, type_value):
    if not isinstance(type_name, str):
        raise BodoError(
            f'register_type(): type name should be a string, not {type(type_name)}'
            )
    if not isinstance(type_value, types.Type):
        raise BodoError(
            f'register_type(): type value should be a valid data type, not {type(type_value)}'
            )
    if hasattr(types, type_name):
        raise BodoError(
            f"register_type(): type name '{type_name}' already exists")
    setattr(types, type_name, type_value)


@box(types.TypeRef)
def box_typeref(typ, val, c):
    return c.pyapi.unserialize(c.pyapi.serialize_object(typ.instance_type))


def check_objmode_output_type(ret_tup, ret_type):
    return tuple(_check_objmode_type(vgn__cuh, t) for vgn__cuh, t in zip(
        ret_tup, ret_type.types))


def _is_equiv_array_type(A, B):
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.struct_arr_ext import StructArrayType
    return isinstance(A, StructArrayType) and isinstance(B, MapArrayType
        ) and set(A.data) == {B.value_arr_type
        } and B.key_arr_type.dtype == bodo.string_type or isinstance(A,
        types.Array) and isinstance(B, types.Array
        ) and A.ndim == B.ndim and A.dtype == B.dtype and B.layout in ('A',
        A.layout) and (A.mutable or not B.mutable) and (A.aligned or not B.
        aligned)


def _fix_objmode_df_type(val, val_typ, typ):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if val_typ.dist != typ.dist:
        val_typ = val_typ.copy(dist=typ.dist)
    if isinstance(typ.index, RangeIndexType) and not isinstance(val_typ.
        index, RangeIndexType):
        warnings.warn(BodoWarning(
            f'Dropping Index of objmode output dataframe since RangeIndexType specified in type annotation ({val_typ.index} to {typ.index})'
            ))
        val.reset_index(drop=True, inplace=True)
        val_typ = val_typ.copy(index=typ.index)
    if (val_typ.index.name_typ != types.none and typ.index.name_typ ==
        types.none):
        warnings.warn(BodoWarning(
            f'Dropping name field in Index of objmode output dataframe since none specified in type annotation ({val_typ.index} to {typ.index})'
            ))
        val_typ = val_typ.copy(index=typ.index)
        val.index.name = None
    for i, (A, B) in enumerate(zip(val_typ.data, typ.data)):
        if _is_equiv_array_type(A, B):
            val_typ = val_typ.replace_col_type(val_typ.columns[i], B)
    if val_typ.is_table_format and not typ.is_table_format:
        val_typ = val_typ.copy(is_table_format=False)
    if val_typ != typ:
        dmpjf__mlof = pd.Index(val_typ.columns)
        ckkwl__ixolm = pd.Index(typ.columns)
        cgni__hbgmo = dmpjf__mlof.argsort()
        dqht__jdbf = ckkwl__ixolm.argsort()
        tswu__iya = val_typ.copy(data=tuple(np.array(val_typ.data)[
            cgni__hbgmo]), columns=tuple(dmpjf__mlof[cgni__hbgmo]))
        bnm__bomjm = typ.copy(data=tuple(np.array(typ.data)[dqht__jdbf]),
            columns=tuple(ckkwl__ixolm[dqht__jdbf]))
        if tswu__iya == bnm__bomjm:
            val_typ = typ
            val = val.reindex(columns=typ.columns)
    return val, val_typ


def _check_objmode_type(val, typ):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    val_typ = bodo.typeof(val)
    if isinstance(typ, DataFrameType) and isinstance(val_typ, DataFrameType):
        val, val_typ = _fix_objmode_df_type(val, val_typ, typ)
    if _is_equiv_array_type(val_typ, typ):
        val_typ = typ
    if isinstance(val_typ, (types.List, types.Set)):
        val_typ = val_typ.copy(reflected=False)
    if isinstance(val_typ, (types.Integer, types.Float)) and isinstance(typ,
        (types.Integer, types.Float)):
        return val
    if val_typ != typ:
        raise BodoError(
            f"""Invalid objmode data type specified.
User specified:	{typ}
Value type:	{val_typ}"""
            )
    return val


gen_objmode_func_overload(warnings.warn, 'none')
