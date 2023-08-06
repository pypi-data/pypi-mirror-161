"""
Collection of utility functions for indexing implementation (getitem/setitem)
"""
import operator
import numba
import numpy as np
from numba.core import types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import intrinsic, overload, register_jitable
import bodo
from bodo.utils.typing import BodoError


@register_jitable
def get_new_null_mask_bool_index(old_mask, ind, n):
    arizw__uan = n + 7 >> 3
    muosq__bpooy = np.empty(arizw__uan, np.uint8)
    nnlh__bzu = 0
    for fccf__bql in range(len(ind)):
        if ind[fccf__bql]:
            rhdg__nkxno = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask,
                fccf__bql)
            bodo.libs.int_arr_ext.set_bit_to_arr(muosq__bpooy, nnlh__bzu,
                rhdg__nkxno)
            nnlh__bzu += 1
    return muosq__bpooy


@register_jitable
def array_getitem_bool_index(A, ind):
    ind = bodo.utils.conversion.coerce_to_ndarray(ind)
    old_mask = A._null_bitmap
    lwwt__idr = A._data[ind]
    n = len(lwwt__idr)
    muosq__bpooy = get_new_null_mask_bool_index(old_mask, ind, n)
    return lwwt__idr, muosq__bpooy


@register_jitable
def get_new_null_mask_int_index(old_mask, ind, n):
    arizw__uan = n + 7 >> 3
    muosq__bpooy = np.empty(arizw__uan, np.uint8)
    nnlh__bzu = 0
    for fccf__bql in range(len(ind)):
        rhdg__nkxno = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask,
            ind[fccf__bql])
        bodo.libs.int_arr_ext.set_bit_to_arr(muosq__bpooy, nnlh__bzu,
            rhdg__nkxno)
        nnlh__bzu += 1
    return muosq__bpooy


@register_jitable
def array_getitem_int_index(A, ind):
    oswdr__amdhx = bodo.utils.conversion.coerce_to_ndarray(ind)
    old_mask = A._null_bitmap
    lwwt__idr = A._data[oswdr__amdhx]
    n = len(lwwt__idr)
    muosq__bpooy = get_new_null_mask_int_index(old_mask, oswdr__amdhx, n)
    return lwwt__idr, muosq__bpooy


@register_jitable
def get_new_null_mask_slice_index(old_mask, ind, n):
    bmpgf__gjjo = numba.cpython.unicode._normalize_slice(ind, n)
    veh__chiqt = numba.cpython.unicode._slice_span(bmpgf__gjjo)
    arizw__uan = veh__chiqt + 7 >> 3
    muosq__bpooy = np.empty(arizw__uan, np.uint8)
    nnlh__bzu = 0
    for fccf__bql in range(bmpgf__gjjo.start, bmpgf__gjjo.stop, bmpgf__gjjo
        .step):
        rhdg__nkxno = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask,
            fccf__bql)
        bodo.libs.int_arr_ext.set_bit_to_arr(muosq__bpooy, nnlh__bzu,
            rhdg__nkxno)
        nnlh__bzu += 1
    return muosq__bpooy


@register_jitable
def array_getitem_slice_index(A, ind):
    n = len(A._data)
    old_mask = A._null_bitmap
    lwwt__idr = np.ascontiguousarray(A._data[ind])
    muosq__bpooy = get_new_null_mask_slice_index(old_mask, ind, n)
    return lwwt__idr, muosq__bpooy


def array_setitem_int_index(A, idx, val):
    return


@overload(array_setitem_int_index, no_unliteral=True)
def array_setitem_int_index_overload(A, idx, val):
    if bodo.utils.utils.is_array_typ(val
        ) or bodo.utils.typing.is_iterable_type(val):

        def impl_arr(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            n = len(val._data)
            for fccf__bql in range(n):
                A._data[idx[fccf__bql]] = val._data[fccf__bql]
                rhdg__nkxno = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val.
                    _null_bitmap, fccf__bql)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx[
                    fccf__bql], rhdg__nkxno)
        return impl_arr
    if bodo.utils.typing.is_scalar_type(val):

        def impl_scalar(A, idx, val):
            for fccf__bql in idx:
                A._data[fccf__bql] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                    fccf__bql, 1)
        return impl_scalar
    raise BodoError(f'setitem not supported for {A} with value {val}')


def array_setitem_bool_index(A, idx, val):
    A[idx] = val


@overload(array_setitem_bool_index, no_unliteral=True)
def array_setitem_bool_index_overload(A, idx, val):
    if bodo.utils.utils.is_array_typ(val
        ) or bodo.utils.typing.is_iterable_type(val):

        def impl_arr(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            n = len(idx)
            xkiz__jmhnh = 0
            for fccf__bql in range(n):
                if not bodo.libs.array_kernels.isna(idx, fccf__bql) and idx[
                    fccf__bql]:
                    A._data[fccf__bql] = val._data[xkiz__jmhnh]
                    rhdg__nkxno = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, xkiz__jmhnh)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        fccf__bql, rhdg__nkxno)
                    xkiz__jmhnh += 1
        return impl_arr
    if bodo.utils.typing.is_scalar_type(val):

        def impl_scalar(A, idx, val):
            n = len(idx)
            xkiz__jmhnh = 0
            for fccf__bql in range(n):
                if not bodo.libs.array_kernels.isna(idx, fccf__bql) and idx[
                    fccf__bql]:
                    A._data[fccf__bql] = val
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        fccf__bql, 1)
                    xkiz__jmhnh += 1
        return impl_scalar
    raise BodoError(f'setitem not supported for {A} with value {val}')


@register_jitable
def setitem_slice_index_null_bits(dst_bitmap, src_bitmap, idx, n):
    bmpgf__gjjo = numba.cpython.unicode._normalize_slice(idx, n)
    xkiz__jmhnh = 0
    for fccf__bql in range(bmpgf__gjjo.start, bmpgf__gjjo.stop, bmpgf__gjjo
        .step):
        rhdg__nkxno = bodo.libs.int_arr_ext.get_bit_bitmap_arr(src_bitmap,
            xkiz__jmhnh)
        bodo.libs.int_arr_ext.set_bit_to_arr(dst_bitmap, fccf__bql, rhdg__nkxno
            )
        xkiz__jmhnh += 1


def array_setitem_slice_index(A, idx, val):
    return


@overload(array_setitem_slice_index, no_unliteral=True)
def array_setitem_slice_index_overload(A, idx, val):
    if bodo.utils.utils.is_array_typ(val
        ) or bodo.utils.typing.is_iterable_type(val):

        def impl_arr(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            n = len(A._data)
            A._data[idx] = val._data
            src_bitmap = val._null_bitmap.copy()
            setitem_slice_index_null_bits(A._null_bitmap, src_bitmap, idx, n)
        return impl_arr
    if bodo.utils.typing.is_scalar_type(val):

        def impl_scalar(A, idx, val):
            bmpgf__gjjo = numba.cpython.unicode._normalize_slice(idx, len(A))
            for fccf__bql in range(bmpgf__gjjo.start, bmpgf__gjjo.stop,
                bmpgf__gjjo.step):
                A._data[fccf__bql] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                    fccf__bql, 1)
        return impl_scalar
    raise BodoError(f'setitem not supported for {A} with value {val}')


def untuple_if_one_tuple(v):
    return v


@overload(untuple_if_one_tuple)
def untuple_if_one_tuple_overload(v):
    if isinstance(v, types.BaseTuple) and len(v.types) == 1:
        return lambda v: v[0]
    return lambda v: v


def init_nested_counts(arr_typ):
    return 0,


@overload(init_nested_counts)
def overload_init_nested_counts(arr_typ):
    arr_typ = arr_typ.instance_type
    if isinstance(arr_typ, bodo.libs.array_item_arr_ext.ArrayItemArrayType
        ) or arr_typ == bodo.string_array_type:
        data_arr_typ = arr_typ.dtype
        return lambda arr_typ: (0,) + init_nested_counts(data_arr_typ)
    if bodo.utils.utils.is_array_typ(arr_typ, False
        ) or arr_typ == bodo.string_type:
        return lambda arr_typ: (0,)
    return lambda arr_typ: ()


def add_nested_counts(nested_counts, arr_item):
    return 0,


@overload(add_nested_counts)
def overload_add_nested_counts(nested_counts, arr_item):
    from bodo.libs.str_arr_ext import get_utf8_size
    arr_item = arr_item.type if isinstance(arr_item, types.Optional
        ) else arr_item
    if isinstance(arr_item, bodo.libs.array_item_arr_ext.ArrayItemArrayType):
        return lambda nested_counts, arr_item: (nested_counts[0] + len(
            arr_item),) + add_nested_counts(nested_counts[1:], bodo.libs.
            array_item_arr_ext.get_data(arr_item))
    if isinstance(arr_item, types.List):
        return lambda nested_counts, arr_item: add_nested_counts(nested_counts,
            bodo.utils.conversion.coerce_to_array(arr_item))
    if arr_item == bodo.string_array_type:
        return lambda nested_counts, arr_item: (nested_counts[0] + len(
            arr_item), nested_counts[1] + np.int64(bodo.libs.str_arr_ext.
            num_total_chars(arr_item)))
    if bodo.utils.utils.is_array_typ(arr_item, False):
        return lambda nested_counts, arr_item: (nested_counts[0] + len(
            arr_item),)
    if arr_item == bodo.string_type:
        return lambda nested_counts, arr_item: (nested_counts[0] +
            get_utf8_size(arr_item),)
    return lambda nested_counts, arr_item: ()


@overload(operator.setitem)
def none_optional_setitem_overload(A, idx, val):
    if not bodo.utils.utils.is_array_typ(A, False):
        return
    elif val == types.none:
        if isinstance(idx, types.Integer):
            return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)
        elif bodo.utils.typing.is_list_like_index_type(idx) and isinstance(idx
            .dtype, types.Integer):

            def setitem_none_int_arr(A, idx, val):
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                for fccf__bql in idx:
                    bodo.libs.array_kernels.setna(A, fccf__bql)
            return setitem_none_int_arr
        elif bodo.utils.typing.is_list_like_index_type(idx
            ) and idx.dtype == types.bool_:
            if A == bodo.string_array_type:

                def string_arr_impl(A, idx, val):
                    n = len(A)
                    idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                    eupud__zmu = bodo.libs.str_arr_ext.pre_alloc_string_array(n
                        , -1)
                    for fccf__bql in numba.parfors.parfor.internal_prange(n):
                        if idx[fccf__bql] or bodo.libs.array_kernels.isna(A,
                            fccf__bql):
                            eupud__zmu[fccf__bql] = ''
                            bodo.libs.str_arr_ext.str_arr_set_na(eupud__zmu,
                                fccf__bql)
                        else:
                            eupud__zmu[fccf__bql] = A[fccf__bql]
                    bodo.libs.str_arr_ext.move_str_binary_arr_payload(A,
                        eupud__zmu)
                return string_arr_impl

            def setitem_none_bool_arr(A, idx, val):
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                n = len(idx)
                for fccf__bql in range(n):
                    if not bodo.libs.array_kernels.isna(idx, fccf__bql
                        ) and idx[fccf__bql]:
                        bodo.libs.array_kernels.setna(A, fccf__bql)
            return setitem_none_bool_arr
        elif isinstance(idx, types.SliceType):

            def setitem_none_slice(A, idx, val):
                n = len(A)
                bmpgf__gjjo = numba.cpython.unicode._normalize_slice(idx, n)
                for fccf__bql in range(bmpgf__gjjo.start, bmpgf__gjjo.stop,
                    bmpgf__gjjo.step):
                    bodo.libs.array_kernels.setna(A, fccf__bql)
            return setitem_none_slice
        raise BodoError(
            f'setitem for {A} with indexing type {idx} and None value not supported.'
            )
    elif isinstance(val, types.optional):
        if isinstance(idx, types.Integer):

            def impl_optional(A, idx, val):
                if val is None:
                    bodo.libs.array_kernels.setna(A, idx)
                else:
                    A[idx] = bodo.utils.indexing.unoptional(val)
            return impl_optional
        elif bodo.utils.typing.is_list_like_index_type(idx) and isinstance(idx
            .dtype, types.Integer):

            def setitem_optional_int_arr(A, idx, val):
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                for fccf__bql in idx:
                    if val is None:
                        bodo.libs.array_kernels.setna(A, fccf__bql)
                        continue
                    A[fccf__bql] = bodo.utils.indexing.unoptional(val)
            return setitem_optional_int_arr
        elif bodo.utils.typing.is_list_like_index_type(idx
            ) and idx.dtype == types.bool_:
            if A == bodo.string_array_type:

                def string_arr_impl(A, idx, val):
                    if val is None:
                        A[idx] = None
                    else:
                        A[idx] = bodo.utils.indexing.unoptional(val)
                return string_arr_impl

            def setitem_optional_bool_arr(A, idx, val):
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                n = len(idx)
                for fccf__bql in range(n):
                    if not bodo.libs.array_kernels.isna(idx, fccf__bql
                        ) and idx[fccf__bql]:
                        if val is None:
                            bodo.libs.array_kernels.setna(A, fccf__bql)
                            continue
                        A[fccf__bql] = bodo.utils.indexing.unoptional(val)
            return setitem_optional_bool_arr
        elif isinstance(idx, types.SliceType):

            def setitem_optional_slice(A, idx, val):
                n = len(A)
                bmpgf__gjjo = numba.cpython.unicode._normalize_slice(idx, n)
                for fccf__bql in range(bmpgf__gjjo.start, bmpgf__gjjo.stop,
                    bmpgf__gjjo.step):
                    if val is None:
                        bodo.libs.array_kernels.setna(A, fccf__bql)
                        continue
                    A[fccf__bql] = bodo.utils.indexing.unoptional(val)
            return setitem_optional_slice
        raise BodoError(
            f'setitem for {A} with indexing type {idx} and optional value not supported.'
            )


@intrinsic
def unoptional(typingctx, val_t=None):
    if not isinstance(val_t, types.Optional):
        return val_t(val_t), lambda c, b, s, args: impl_ret_borrowed(c, b,
            val_t, args[0])

    def codegen(context, builder, signature, args):
        eht__ihi = context.make_helper(builder, val_t, args[0])
        mizx__exlqf = eht__ihi.data
        context.nrt.incref(builder, val_t.type, mizx__exlqf)
        return mizx__exlqf
    return val_t.type(val_t), codegen
