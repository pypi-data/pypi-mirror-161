"""implementations of rolling window functions (sequential and parallel)
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, register_jitable
import bodo
from bodo.libs.distributed_api import Reduce_Type
from bodo.utils.typing import BodoError, decode_if_dict_array, get_overload_const_func, get_overload_const_str, is_const_func_type, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true
from bodo.utils.utils import unliteral_all
supported_rolling_funcs = ('sum', 'mean', 'var', 'std', 'count', 'median',
    'min', 'max', 'cov', 'corr', 'apply')
unsupported_rolling_methods = ['skew', 'kurt', 'aggregate', 'quantile', 'sem']


def rolling_fixed(arr, win):
    return arr


def rolling_variable(arr, on_arr, win):
    return arr


def rolling_cov(arr, arr2, win):
    return arr


def rolling_corr(arr, arr2, win):
    return arr


@infer_global(rolling_cov)
@infer_global(rolling_corr)
class RollingCovType(AbstractTemplate):

    def generic(self, args, kws):
        arr = args[0]
        ttoid__dopmj = arr.copy(dtype=types.float64)
        return signature(ttoid__dopmj, *unliteral_all(args))


@lower_builtin(rolling_corr, types.VarArg(types.Any))
@lower_builtin(rolling_cov, types.VarArg(types.Any))
def lower_rolling_corr_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@overload(rolling_fixed, no_unliteral=True)
def overload_rolling_fixed(arr, index_arr, win, minp, center, fname, raw=
    True, parallel=False):
    assert is_overload_constant_bool(raw
        ), 'raw argument should be constant bool'
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    bjoiu__ebo = get_overload_const_str(fname)
    if bjoiu__ebo not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (fixed window) function {}'.format
            (bjoiu__ebo))
    if bjoiu__ebo in ('median', 'min', 'max'):
        fwlxq__kene = 'def kernel_func(A):\n'
        fwlxq__kene += '  if np.isnan(A).sum() != 0: return np.nan\n'
        fwlxq__kene += '  return np.{}(A)\n'.format(bjoiu__ebo)
        cpd__peoh = {}
        exec(fwlxq__kene, {'np': np}, cpd__peoh)
        kernel_func = register_jitable(cpd__peoh['kernel_func'])
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        bjoiu__ebo]
    return (lambda arr, index_arr, win, minp, center, fname, raw=True,
        parallel=False: roll_fixed_linear_generic(arr, win, minp, center,
        parallel, init_kernel, add_kernel, remove_kernel, calc_kernel))


@overload(rolling_variable, no_unliteral=True)
def overload_rolling_variable(arr, on_arr, index_arr, win, minp, center,
    fname, raw=True, parallel=False):
    assert is_overload_constant_bool(raw)
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    bjoiu__ebo = get_overload_const_str(fname)
    if bjoiu__ebo not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (variable window) function {}'.
            format(bjoiu__ebo))
    if bjoiu__ebo in ('median', 'min', 'max'):
        fwlxq__kene = 'def kernel_func(A):\n'
        fwlxq__kene += '  arr  = dropna(A)\n'
        fwlxq__kene += '  if len(arr) == 0: return np.nan\n'
        fwlxq__kene += '  return np.{}(arr)\n'.format(bjoiu__ebo)
        cpd__peoh = {}
        exec(fwlxq__kene, {'np': np, 'dropna': _dropna}, cpd__peoh)
        kernel_func = register_jitable(cpd__peoh['kernel_func'])
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        bjoiu__ebo]
    return (lambda arr, on_arr, index_arr, win, minp, center, fname, raw=
        True, parallel=False: roll_var_linear_generic(arr, on_arr, win,
        minp, center, parallel, init_kernel, add_kernel, remove_kernel,
        calc_kernel))


def _get_apply_func(f_type):
    func = get_overload_const_func(f_type, None)
    return bodo.compiler.udf_jit(func)


comm_border_tag = 22


@register_jitable
def roll_fixed_linear_generic(in_arr, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data(in_arr, win, minp, center, rank,
                n_pes, init_data, add_obs, remove_obs, calc_out)
        gsbxg__pmkfz = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            wmh__gbdss) = gsbxg__pmkfz
    output, data = roll_fixed_linear_generic_seq(in_arr, win, minp, center,
        init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(wmh__gbdss, True)
            for exna__tad in range(0, halo_size):
                data = add_obs(r_recv_buff[exna__tad], *data)
                xvihh__kjt = in_arr[N + exna__tad - win]
                data = remove_obs(xvihh__kjt, *data)
                output[N + exna__tad - offset] = calc_out(minp, *data)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            data = init_data()
            for exna__tad in range(0, halo_size):
                data = add_obs(l_recv_buff[exna__tad], *data)
            for exna__tad in range(0, win - 1):
                data = add_obs(in_arr[exna__tad], *data)
                if exna__tad > offset:
                    xvihh__kjt = l_recv_buff[exna__tad - offset - 1]
                    data = remove_obs(xvihh__kjt, *data)
                if exna__tad >= offset:
                    output[exna__tad - offset] = calc_out(minp, *data)
    return output


@register_jitable
def roll_fixed_linear_generic_seq(in_arr, win, minp, center, init_data,
    add_obs, remove_obs, calc_out):
    data = init_data()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    output = np.empty(N, dtype=np.float64)
    adhz__ortvs = max(minp, 1) - 1
    adhz__ortvs = min(adhz__ortvs, N)
    for exna__tad in range(0, adhz__ortvs):
        data = add_obs(in_arr[exna__tad], *data)
        if exna__tad >= offset:
            output[exna__tad - offset] = calc_out(minp, *data)
    for exna__tad in range(adhz__ortvs, N):
        val = in_arr[exna__tad]
        data = add_obs(val, *data)
        if exna__tad > win - 1:
            xvihh__kjt = in_arr[exna__tad - win]
            data = remove_obs(xvihh__kjt, *data)
        output[exna__tad - offset] = calc_out(minp, *data)
    einw__lyoq = data
    for exna__tad in range(N, N + offset):
        if exna__tad > win - 1:
            xvihh__kjt = in_arr[exna__tad - win]
            data = remove_obs(xvihh__kjt, *data)
        output[exna__tad - offset] = calc_out(minp, *data)
    return output, einw__lyoq


def roll_fixed_apply(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    pass


@overload(roll_fixed_apply, no_unliteral=True)
def overload_roll_fixed_apply(in_arr, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_fixed_apply_impl


def roll_fixed_apply_impl(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    index_arr = fix_index_arr(index_arr)
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_apply(in_arr, index_arr, win, minp,
                center, rank, n_pes, kernel_func, raw)
        gsbxg__pmkfz = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            wmh__gbdss) = gsbxg__pmkfz
        if raw == False:
            tfxuz__ghpc = _border_icomm(index_arr, rank, n_pes, halo_size, 
                True, center)
            (l_recv_buff_idx, r_recv_buff_idx, slcnf__ojuov, zljlo__nopkh,
                rpuen__nwjx, drio__yhh) = tfxuz__ghpc
    output = roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
        kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if raw == False:
            _border_send_wait(zljlo__nopkh, slcnf__ojuov, rank, n_pes, True,
                center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(wmh__gbdss, True)
            if raw == False:
                bodo.libs.distributed_api.wait(drio__yhh, True)
            recv_right_compute(output, in_arr, index_arr, N, win, minp,
                offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            if raw == False:
                bodo.libs.distributed_api.wait(rpuen__nwjx, True)
            recv_left_compute(output, in_arr, index_arr, win, minp, offset,
                l_recv_buff, l_recv_buff_idx, kernel_func, raw)
    return output


def recv_right_compute(output, in_arr, index_arr, N, win, minp, offset,
    r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_right_compute, no_unliteral=True)
def overload_recv_right_compute(output, in_arr, index_arr, N, win, minp,
    offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, N, win, minp, offset,
            r_recv_buff, r_recv_buff_idx, kernel_func, raw):
            einw__lyoq = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
            nwyuo__pflb = 0
            for exna__tad in range(max(N - offset, 0), N):
                data = einw__lyoq[nwyuo__pflb:nwyuo__pflb + win]
                if win - np.isnan(data).sum() < minp:
                    output[exna__tad] = np.nan
                else:
                    output[exna__tad] = kernel_func(data)
                nwyuo__pflb += 1
        return impl

    def impl_series(output, in_arr, index_arr, N, win, minp, offset,
        r_recv_buff, r_recv_buff_idx, kernel_func, raw):
        einw__lyoq = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
        iljpb__dayn = np.concatenate((index_arr[N - win + 1:], r_recv_buff_idx)
            )
        nwyuo__pflb = 0
        for exna__tad in range(max(N - offset, 0), N):
            data = einw__lyoq[nwyuo__pflb:nwyuo__pflb + win]
            if win - np.isnan(data).sum() < minp:
                output[exna__tad] = np.nan
            else:
                output[exna__tad] = kernel_func(pd.Series(data, iljpb__dayn
                    [nwyuo__pflb:nwyuo__pflb + win]))
            nwyuo__pflb += 1
    return impl_series


def recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_left_compute, no_unliteral=True)
def overload_recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, win, minp, offset, l_recv_buff,
            l_recv_buff_idx, kernel_func, raw):
            einw__lyoq = np.concatenate((l_recv_buff, in_arr[:win - 1]))
            for exna__tad in range(0, win - offset - 1):
                data = einw__lyoq[exna__tad:exna__tad + win]
                if win - np.isnan(data).sum() < minp:
                    output[exna__tad] = np.nan
                else:
                    output[exna__tad] = kernel_func(data)
        return impl

    def impl_series(output, in_arr, index_arr, win, minp, offset,
        l_recv_buff, l_recv_buff_idx, kernel_func, raw):
        einw__lyoq = np.concatenate((l_recv_buff, in_arr[:win - 1]))
        iljpb__dayn = np.concatenate((l_recv_buff_idx, index_arr[:win - 1]))
        for exna__tad in range(0, win - offset - 1):
            data = einw__lyoq[exna__tad:exna__tad + win]
            if win - np.isnan(data).sum() < minp:
                output[exna__tad] = np.nan
            else:
                output[exna__tad] = kernel_func(pd.Series(data, iljpb__dayn
                    [exna__tad:exna__tad + win]))
    return impl_series


def roll_fixed_apply_seq(in_arr, index_arr, win, minp, center, kernel_func,
    raw=True):
    pass


@overload(roll_fixed_apply_seq, no_unliteral=True)
def overload_roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
    kernel_func, raw=True):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"

    def roll_fixed_apply_seq_impl(in_arr, index_arr, win, minp, center,
        kernel_func, raw=True):
        N = len(in_arr)
        output = np.empty(N, dtype=np.float64)
        offset = (win - 1) // 2 if center else 0
        for exna__tad in range(0, N):
            start = max(exna__tad - win + 1 + offset, 0)
            end = min(exna__tad + 1 + offset, N)
            data = in_arr[start:end]
            if end - start - np.isnan(data).sum() < minp:
                output[exna__tad] = np.nan
            else:
                output[exna__tad] = apply_func(kernel_func, data, index_arr,
                    start, end, raw)
        return output
    return roll_fixed_apply_seq_impl


def apply_func(kernel_func, data, index_arr, start, end, raw):
    return kernel_func(data)


@overload(apply_func, no_unliteral=True)
def overload_apply_func(kernel_func, data, index_arr, start, end, raw):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"
    if is_overload_true(raw):
        return (lambda kernel_func, data, index_arr, start, end, raw:
            kernel_func(data))
    return lambda kernel_func, data, index_arr, start, end, raw: kernel_func(pd
        .Series(data, index_arr[start:end]))


def fix_index_arr(A):
    return A


@overload(fix_index_arr)
def overload_fix_index_arr(A):
    if is_overload_none(A):
        return lambda A: np.zeros(3)
    return lambda A: A


def get_offset_nanos(w):
    out = status = 0
    try:
        out = pd.tseries.frequencies.to_offset(w).nanos
    except:
        status = 1
    return out, status


def offset_to_nanos(w):
    return w


@overload(offset_to_nanos)
def overload_offset_to_nanos(w):
    if isinstance(w, types.Integer):
        return lambda w: w

    def impl(w):
        with numba.objmode(out='int64', status='int64'):
            out, status = get_offset_nanos(w)
        if status != 0:
            raise ValueError('Invalid offset value')
        return out
    return impl


@register_jitable
def roll_var_linear_generic(in_arr, on_arr_dt, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable(in_arr, on_arr, win, minp,
                rank, n_pes, init_data, add_obs, remove_obs, calc_out)
        gsbxg__pmkfz = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, uosl__hsmf, l_recv_req,
            ypmgr__bzk) = gsbxg__pmkfz
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start,
        end, init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(uosl__hsmf, uosl__hsmf, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(ypmgr__bzk, True)
            num_zero_starts = 0
            for exna__tad in range(0, N):
                if start[exna__tad] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            data = init_data()
            for ueafg__ufl in range(recv_starts[0], len(l_recv_t_buff)):
                data = add_obs(l_recv_buff[ueafg__ufl], *data)
            if right_closed:
                data = add_obs(in_arr[0], *data)
            output[0] = calc_out(minp, *data)
            for exna__tad in range(1, num_zero_starts):
                s = recv_starts[exna__tad]
                lezq__ftdy = end[exna__tad]
                for ueafg__ufl in range(recv_starts[exna__tad - 1], s):
                    data = remove_obs(l_recv_buff[ueafg__ufl], *data)
                for ueafg__ufl in range(end[exna__tad - 1], lezq__ftdy):
                    data = add_obs(in_arr[ueafg__ufl], *data)
                output[exna__tad] = calc_out(minp, *data)
    return output


@register_jitable(cache=True)
def _get_var_recv_starts(on_arr, l_recv_t_buff, num_zero_starts, win):
    recv_starts = np.zeros(num_zero_starts, np.int64)
    halo_size = len(l_recv_t_buff)
    hisob__nls = cast_dt64_arr_to_int(on_arr)
    left_closed = False
    yhwku__jgvff = hisob__nls[0] - win
    if left_closed:
        yhwku__jgvff -= 1
    recv_starts[0] = halo_size
    for ueafg__ufl in range(0, halo_size):
        if l_recv_t_buff[ueafg__ufl] > yhwku__jgvff:
            recv_starts[0] = ueafg__ufl
            break
    for exna__tad in range(1, num_zero_starts):
        yhwku__jgvff = hisob__nls[exna__tad] - win
        if left_closed:
            yhwku__jgvff -= 1
        recv_starts[exna__tad] = halo_size
        for ueafg__ufl in range(recv_starts[exna__tad - 1], halo_size):
            if l_recv_t_buff[ueafg__ufl] > yhwku__jgvff:
                recv_starts[exna__tad] = ueafg__ufl
                break
    return recv_starts


@register_jitable
def roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start, end,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    output = np.empty(N, np.float64)
    data = init_data()
    for ueafg__ufl in range(start[0], end[0]):
        data = add_obs(in_arr[ueafg__ufl], *data)
    output[0] = calc_out(minp, *data)
    for exna__tad in range(1, N):
        s = start[exna__tad]
        lezq__ftdy = end[exna__tad]
        for ueafg__ufl in range(start[exna__tad - 1], s):
            data = remove_obs(in_arr[ueafg__ufl], *data)
        for ueafg__ufl in range(end[exna__tad - 1], lezq__ftdy):
            data = add_obs(in_arr[ueafg__ufl], *data)
        output[exna__tad] = calc_out(minp, *data)
    return output


def roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    pass


@overload(roll_variable_apply, no_unliteral=True)
def overload_roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_variable_apply_impl


def roll_variable_apply_impl(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    index_arr = fix_index_arr(index_arr)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable_apply(in_arr, on_arr,
                index_arr, win, minp, rank, n_pes, kernel_func, raw)
        gsbxg__pmkfz = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, uosl__hsmf, l_recv_req,
            ypmgr__bzk) = gsbxg__pmkfz
        if raw == False:
            tfxuz__ghpc = _border_icomm_var(index_arr, on_arr, rank, n_pes, win
                )
            (l_recv_buff_idx, nviy__rvx, zljlo__nopkh, targc__camd,
                rpuen__nwjx, aqrpj__gxidc) = tfxuz__ghpc
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
        start, end, kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(uosl__hsmf, uosl__hsmf, rank, n_pes, True, False)
        if raw == False:
            _border_send_wait(zljlo__nopkh, zljlo__nopkh, rank, n_pes, True,
                False)
            _border_send_wait(targc__camd, targc__camd, rank, n_pes, True, 
                False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(ypmgr__bzk, True)
            if raw == False:
                bodo.libs.distributed_api.wait(rpuen__nwjx, True)
                bodo.libs.distributed_api.wait(aqrpj__gxidc, True)
            num_zero_starts = 0
            for exna__tad in range(0, N):
                if start[exna__tad] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            recv_left_var_compute(output, in_arr, index_arr,
                num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx,
                minp, kernel_func, raw)
    return output


def recv_left_var_compute(output, in_arr, index_arr, num_zero_starts,
    recv_starts, l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
    pass


@overload(recv_left_var_compute)
def overload_recv_left_var_compute(output, in_arr, index_arr,
    num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx, minp,
    kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, num_zero_starts, recv_starts,
            l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
            for exna__tad in range(0, num_zero_starts):
                vnt__pkgyt = recv_starts[exna__tad]
                skkc__ovunb = np.concatenate((l_recv_buff[vnt__pkgyt:],
                    in_arr[:exna__tad + 1]))
                if len(skkc__ovunb) - np.isnan(skkc__ovunb).sum() >= minp:
                    output[exna__tad] = kernel_func(skkc__ovunb)
                else:
                    output[exna__tad] = np.nan
        return impl

    def impl_series(output, in_arr, index_arr, num_zero_starts, recv_starts,
        l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
        for exna__tad in range(0, num_zero_starts):
            vnt__pkgyt = recv_starts[exna__tad]
            skkc__ovunb = np.concatenate((l_recv_buff[vnt__pkgyt:], in_arr[
                :exna__tad + 1]))
            fhvs__lsie = np.concatenate((l_recv_buff_idx[vnt__pkgyt:],
                index_arr[:exna__tad + 1]))
            if len(skkc__ovunb) - np.isnan(skkc__ovunb).sum() >= minp:
                output[exna__tad] = kernel_func(pd.Series(skkc__ovunb,
                    fhvs__lsie))
            else:
                output[exna__tad] = np.nan
    return impl_series


def roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp, start,
    end, kernel_func, raw):
    pass


@overload(roll_variable_apply_seq)
def overload_roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):
        return roll_variable_apply_seq_impl
    return roll_variable_apply_seq_impl_series


def roll_variable_apply_seq_impl(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for exna__tad in range(0, N):
        s = start[exna__tad]
        lezq__ftdy = end[exna__tad]
        data = in_arr[s:lezq__ftdy]
        if lezq__ftdy - s - np.isnan(data).sum() >= minp:
            output[exna__tad] = kernel_func(data)
        else:
            output[exna__tad] = np.nan
    return output


def roll_variable_apply_seq_impl_series(in_arr, on_arr, index_arr, win,
    minp, start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for exna__tad in range(0, N):
        s = start[exna__tad]
        lezq__ftdy = end[exna__tad]
        data = in_arr[s:lezq__ftdy]
        if lezq__ftdy - s - np.isnan(data).sum() >= minp:
            output[exna__tad] = kernel_func(pd.Series(data, index_arr[s:
                lezq__ftdy]))
        else:
            output[exna__tad] = np.nan
    return output


@register_jitable(cache=True)
def _build_indexer(on_arr, N, win, left_closed, right_closed):
    hisob__nls = cast_dt64_arr_to_int(on_arr)
    start = np.empty(N, np.int64)
    end = np.empty(N, np.int64)
    start[0] = 0
    if right_closed:
        end[0] = 1
    else:
        end[0] = 0
    for exna__tad in range(1, N):
        jvvxw__teg = hisob__nls[exna__tad]
        yhwku__jgvff = hisob__nls[exna__tad] - win
        if left_closed:
            yhwku__jgvff -= 1
        start[exna__tad] = exna__tad
        for ueafg__ufl in range(start[exna__tad - 1], exna__tad):
            if hisob__nls[ueafg__ufl] > yhwku__jgvff:
                start[exna__tad] = ueafg__ufl
                break
        if hisob__nls[end[exna__tad - 1]] <= jvvxw__teg:
            end[exna__tad] = exna__tad + 1
        else:
            end[exna__tad] = end[exna__tad - 1]
        if not right_closed:
            end[exna__tad] -= 1
    return start, end


@register_jitable
def init_data_sum():
    return 0, 0.0


@register_jitable
def add_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
    return nobs, sum_x


@register_jitable
def remove_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
    return nobs, sum_x


@register_jitable
def calc_sum(minp, nobs, sum_x):
    return sum_x if nobs >= minp else np.nan


@register_jitable
def init_data_mean():
    return 0, 0.0, 0


@register_jitable
def add_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
        if val < 0:
            neg_ct += 1
    return nobs, sum_x, neg_ct


@register_jitable
def remove_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
        if val < 0:
            neg_ct -= 1
    return nobs, sum_x, neg_ct


@register_jitable
def calc_mean(minp, nobs, sum_x, neg_ct):
    if nobs >= minp:
        xntke__omqv = sum_x / nobs
        if neg_ct == 0 and xntke__omqv < 0.0:
            xntke__omqv = 0
        elif neg_ct == nobs and xntke__omqv > 0.0:
            xntke__omqv = 0
    else:
        xntke__omqv = np.nan
    return xntke__omqv


@register_jitable
def init_data_var():
    return 0, 0.0, 0.0


@register_jitable
def add_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs += 1
        ciyqn__sok = val - mean_x
        mean_x += ciyqn__sok / nobs
        ssqdm_x += (nobs - 1) * ciyqn__sok ** 2 / nobs
    return nobs, mean_x, ssqdm_x


@register_jitable
def remove_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs -= 1
        if nobs != 0:
            ciyqn__sok = val - mean_x
            mean_x -= ciyqn__sok / nobs
            ssqdm_x -= (nobs + 1) * ciyqn__sok ** 2 / nobs
        else:
            mean_x = 0.0
            ssqdm_x = 0.0
    return nobs, mean_x, ssqdm_x


@register_jitable
def calc_var(minp, nobs, mean_x, ssqdm_x):
    wrhpi__ejix = 1.0
    xntke__omqv = np.nan
    if nobs >= minp and nobs > wrhpi__ejix:
        if nobs == 1:
            xntke__omqv = 0.0
        else:
            xntke__omqv = ssqdm_x / (nobs - wrhpi__ejix)
            if xntke__omqv < 0.0:
                xntke__omqv = 0.0
    return xntke__omqv


@register_jitable
def calc_std(minp, nobs, mean_x, ssqdm_x):
    ylvhy__rcpmj = calc_var(minp, nobs, mean_x, ssqdm_x)
    return np.sqrt(ylvhy__rcpmj)


@register_jitable
def init_data_count():
    return 0.0,


@register_jitable
def add_count(val, count_x):
    if not np.isnan(val):
        count_x += 1.0
    return count_x,


@register_jitable
def remove_count(val, count_x):
    if not np.isnan(val):
        count_x -= 1.0
    return count_x,


@register_jitable
def calc_count(minp, count_x):
    return count_x


@register_jitable
def calc_count_var(minp, count_x):
    return count_x if count_x >= minp else np.nan


linear_kernels = {'sum': (init_data_sum, add_sum, remove_sum, calc_sum),
    'mean': (init_data_mean, add_mean, remove_mean, calc_mean), 'var': (
    init_data_var, add_var, remove_var, calc_var), 'std': (init_data_var,
    add_var, remove_var, calc_std), 'count': (init_data_count, add_count,
    remove_count, calc_count)}


def shift():
    return


@overload(shift, jit_options={'cache': True})
def shift_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return shift_impl


def shift_impl(in_arr, shift, parallel):
    N = len(in_arr)
    in_arr = decode_if_dict_array(in_arr)
    output = alloc_shift(N, in_arr, (-1,))
    send_right = shift > 0
    send_left = shift <= 0
    is_parallel_str = False
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_shift(in_arr, shift, rank, n_pes)
        gsbxg__pmkfz = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            wmh__gbdss) = gsbxg__pmkfz
        if send_right and is_str_binary_array(in_arr):
            is_parallel_str = True
            shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
                l_recv_req, l_recv_buff, output)
    shift_seq(in_arr, shift, output, is_parallel_str)
    if parallel:
        if send_right:
            if not is_str_binary_array(in_arr):
                shift_left_recv(r_send_req, l_send_req, rank, n_pes,
                    halo_size, l_recv_req, l_recv_buff, output)
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(wmh__gbdss, True)
                for exna__tad in range(0, halo_size):
                    if bodo.libs.array_kernels.isna(r_recv_buff, exna__tad):
                        bodo.libs.array_kernels.setna(output, N - halo_size +
                            exna__tad)
                        continue
                    output[N - halo_size + exna__tad] = r_recv_buff[exna__tad]
    return output


@register_jitable(cache=True)
def shift_seq(in_arr, shift, output, is_parallel_str=False):
    N = len(in_arr)
    omvxt__awfh = 1 if shift > 0 else -1
    shift = omvxt__awfh * min(abs(shift), N)
    if shift > 0 and (not is_parallel_str or bodo.get_rank() == 0):
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    start = max(shift, 0)
    end = min(N, N + shift)
    for exna__tad in range(start, end):
        if bodo.libs.array_kernels.isna(in_arr, exna__tad - shift):
            bodo.libs.array_kernels.setna(output, exna__tad)
            continue
        output[exna__tad] = in_arr[exna__tad - shift]
    if shift < 0:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    return output


@register_jitable
def shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
    l_recv_req, l_recv_buff, output):
    _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
    if rank != 0:
        bodo.libs.distributed_api.wait(l_recv_req, True)
        for exna__tad in range(0, halo_size):
            if bodo.libs.array_kernels.isna(l_recv_buff, exna__tad):
                bodo.libs.array_kernels.setna(output, exna__tad)
                continue
            output[exna__tad] = l_recv_buff[exna__tad]


def is_str_binary_array(arr):
    return False


@overload(is_str_binary_array)
def overload_is_str_binary_array(arr):
    if arr in [bodo.string_array_type, bodo.binary_array_type]:
        return lambda arr: True
    return lambda arr: False


def is_supported_shift_array_type(arr_type):
    return isinstance(arr_type, types.Array) and (isinstance(arr_type.dtype,
        types.Number) or arr_type.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]) or isinstance(arr_type, (bodo.IntegerArrayType,
        bodo.DecimalArrayType)) or arr_type in (bodo.boolean_array, bodo.
        datetime_date_array_type, bodo.string_array_type, bodo.
        binary_array_type, bodo.dict_str_arr_type)


def pct_change():
    return


@overload(pct_change, jit_options={'cache': True})
def pct_change_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return pct_change_impl


def pct_change_impl(in_arr, shift, parallel):
    N = len(in_arr)
    send_right = shift > 0
    send_left = shift <= 0
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_pct_change(in_arr, shift, rank, n_pes)
        gsbxg__pmkfz = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            wmh__gbdss) = gsbxg__pmkfz
    output = pct_change_seq(in_arr, shift)
    if parallel:
        if send_right:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
            if rank != 0:
                bodo.libs.distributed_api.wait(l_recv_req, True)
                for exna__tad in range(0, halo_size):
                    nihei__bgern = l_recv_buff[exna__tad]
                    output[exna__tad] = (in_arr[exna__tad] - nihei__bgern
                        ) / nihei__bgern
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(wmh__gbdss, True)
                for exna__tad in range(0, halo_size):
                    nihei__bgern = r_recv_buff[exna__tad]
                    output[N - halo_size + exna__tad] = (in_arr[N -
                        halo_size + exna__tad] - nihei__bgern) / nihei__bgern
    return output


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_first_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[0]
    assert isinstance(arr.dtype, types.Float)
    jkw__zqkiu = np.nan
    if arr.dtype == types.float32:
        jkw__zqkiu = np.float32('nan')

    def impl(arr):
        for exna__tad in range(len(arr)):
            if not bodo.libs.array_kernels.isna(arr, exna__tad):
                return arr[exna__tad]
        return jkw__zqkiu
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_last_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[-1]
    assert isinstance(arr.dtype, types.Float)
    jkw__zqkiu = np.nan
    if arr.dtype == types.float32:
        jkw__zqkiu = np.float32('nan')

    def impl(arr):
        wjk__lniqe = len(arr)
        for exna__tad in range(len(arr)):
            nwyuo__pflb = wjk__lniqe - exna__tad - 1
            if not bodo.libs.array_kernels.isna(arr, nwyuo__pflb):
                return arr[nwyuo__pflb]
        return jkw__zqkiu
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_one_from_arr_dtype(arr):
    one = arr.dtype(1)
    return lambda arr: one


@register_jitable(cache=True)
def pct_change_seq(in_arr, shift):
    N = len(in_arr)
    output = alloc_pct_change(N, in_arr)
    omvxt__awfh = 1 if shift > 0 else -1
    shift = omvxt__awfh * min(abs(shift), N)
    if shift > 0:
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    else:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    if shift > 0:
        trx__kjsy = get_first_non_na(in_arr[:shift])
        uxc__hmhv = get_last_non_na(in_arr[:shift])
    else:
        trx__kjsy = get_last_non_na(in_arr[:-shift])
        uxc__hmhv = get_first_non_na(in_arr[:-shift])
    one = get_one_from_arr_dtype(output)
    start = max(shift, 0)
    end = min(N, N + shift)
    for exna__tad in range(start, end):
        nihei__bgern = in_arr[exna__tad - shift]
        if np.isnan(nihei__bgern):
            nihei__bgern = trx__kjsy
        else:
            trx__kjsy = nihei__bgern
        val = in_arr[exna__tad]
        if np.isnan(val):
            val = uxc__hmhv
        else:
            uxc__hmhv = val
        output[exna__tad] = val / nihei__bgern - one
    return output


@register_jitable(cache=True)
def _border_icomm(in_arr, rank, n_pes, halo_size, send_right=True,
    send_left=False):
    wwit__mms = np.int32(comm_border_tag)
    l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    r_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    if send_right and rank != n_pes - 1:
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            halo_size, np.int32(rank + 1), wwit__mms, True)
    if send_right and rank != 0:
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, halo_size,
            np.int32(rank - 1), wwit__mms, True)
    if send_left and rank != 0:
        l_send_req = bodo.libs.distributed_api.isend(in_arr[:halo_size],
            halo_size, np.int32(rank - 1), wwit__mms, True)
    if send_left and rank != n_pes - 1:
        wmh__gbdss = bodo.libs.distributed_api.irecv(r_recv_buff, halo_size,
            np.int32(rank + 1), wwit__mms, True)
    return (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
        wmh__gbdss)


@register_jitable(cache=True)
def _border_icomm_var(in_arr, on_arr, rank, n_pes, win_size):
    wwit__mms = np.int32(comm_border_tag)
    N = len(on_arr)
    halo_size = N
    end = on_arr[-1]
    for ueafg__ufl in range(-2, -N, -1):
        njg__xcmr = on_arr[ueafg__ufl]
        if end - njg__xcmr >= win_size:
            halo_size = -ueafg__ufl
            break
    if rank != n_pes - 1:
        bodo.libs.distributed_api.send(halo_size, np.int32(rank + 1), wwit__mms
            )
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), wwit__mms, True)
        uosl__hsmf = bodo.libs.distributed_api.isend(on_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), wwit__mms, True)
    if rank != 0:
        halo_size = bodo.libs.distributed_api.recv(np.int64, np.int32(rank -
            1), wwit__mms)
        l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr)
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, np.int32(
            halo_size), np.int32(rank - 1), wwit__mms, True)
        l_recv_t_buff = np.empty(halo_size, np.int64)
        ypmgr__bzk = bodo.libs.distributed_api.irecv(l_recv_t_buff, np.
            int32(halo_size), np.int32(rank - 1), wwit__mms, True)
    return (l_recv_buff, l_recv_t_buff, r_send_req, uosl__hsmf, l_recv_req,
        ypmgr__bzk)


@register_jitable
def _border_send_wait(r_send_req, l_send_req, rank, n_pes, right, left):
    if right and rank != n_pes - 1:
        bodo.libs.distributed_api.wait(r_send_req, True)
    if left and rank != 0:
        bodo.libs.distributed_api.wait(l_send_req, True)


@register_jitable
def _is_small_for_parallel(N, halo_size):
    qweay__pfuh = bodo.libs.distributed_api.dist_reduce(int(N <= 2 *
        halo_size + 1), np.int32(Reduce_Type.Sum.value))
    return qweay__pfuh != 0


@register_jitable
def _handle_small_data(in_arr, win, minp, center, rank, n_pes, init_data,
    add_obs, remove_obs, calc_out):
    N = len(in_arr)
    bvx__lmu = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32(
        Reduce_Type.Sum.value))
    vlgxw__fdt = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        acbs__uil, fdpqm__msl = roll_fixed_linear_generic_seq(vlgxw__fdt,
            win, minp, center, init_data, add_obs, remove_obs, calc_out)
    else:
        acbs__uil = np.empty(bvx__lmu, np.float64)
    bodo.libs.distributed_api.bcast(acbs__uil)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return acbs__uil[start:end]


@register_jitable
def _handle_small_data_apply(in_arr, index_arr, win, minp, center, rank,
    n_pes, kernel_func, raw=True):
    N = len(in_arr)
    bvx__lmu = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32(
        Reduce_Type.Sum.value))
    vlgxw__fdt = bodo.libs.distributed_api.gatherv(in_arr)
    bcc__dvyx = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        acbs__uil = roll_fixed_apply_seq(vlgxw__fdt, bcc__dvyx, win, minp,
            center, kernel_func, raw)
    else:
        acbs__uil = np.empty(bvx__lmu, np.float64)
    bodo.libs.distributed_api.bcast(acbs__uil)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return acbs__uil[start:end]


def bcast_n_chars_if_str_binary_arr(arr):
    pass


@overload(bcast_n_chars_if_str_binary_arr)
def overload_bcast_n_chars_if_str_binary_arr(arr):
    if arr in [bodo.binary_array_type, bodo.string_array_type]:

        def impl(arr):
            return bodo.libs.distributed_api.bcast_scalar(np.int64(bodo.
                libs.str_arr_ext.num_total_chars(arr)))
        return impl
    return lambda arr: -1


@register_jitable
def _handle_small_data_shift(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    bvx__lmu = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32(
        Reduce_Type.Sum.value))
    vlgxw__fdt = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        acbs__uil = alloc_shift(len(vlgxw__fdt), vlgxw__fdt, (-1,))
        shift_seq(vlgxw__fdt, shift, acbs__uil)
        utbu__ykqin = bcast_n_chars_if_str_binary_arr(acbs__uil)
    else:
        utbu__ykqin = bcast_n_chars_if_str_binary_arr(in_arr)
        acbs__uil = alloc_shift(bvx__lmu, in_arr, (utbu__ykqin,))
    bodo.libs.distributed_api.bcast(acbs__uil)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return acbs__uil[start:end]


@register_jitable
def _handle_small_data_pct_change(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    bvx__lmu = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    vlgxw__fdt = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        acbs__uil = pct_change_seq(vlgxw__fdt, shift)
    else:
        acbs__uil = alloc_pct_change(bvx__lmu, in_arr)
    bodo.libs.distributed_api.bcast(acbs__uil)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return acbs__uil[start:end]


def cast_dt64_arr_to_int(arr):
    return arr


@infer_global(cast_dt64_arr_to_int)
class DtArrToIntType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        assert args[0] == types.Array(types.NPDatetime('ns'), 1, 'C') or args[0
            ] == types.Array(types.int64, 1, 'C')
        return signature(types.Array(types.int64, 1, 'C'), *args)


@lower_builtin(cast_dt64_arr_to_int, types.Array(types.NPDatetime('ns'), 1,
    'C'))
@lower_builtin(cast_dt64_arr_to_int, types.Array(types.int64, 1, 'C'))
def lower_cast_dt64_arr_to_int(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@register_jitable
def _is_small_for_parallel_variable(on_arr, win_size):
    if len(on_arr) < 2:
        rfrnk__irb = 1
    else:
        start = on_arr[0]
        end = on_arr[-1]
        dpgh__ztzu = end - start
        rfrnk__irb = int(dpgh__ztzu <= win_size)
    qweay__pfuh = bodo.libs.distributed_api.dist_reduce(rfrnk__irb, np.
        int32(Reduce_Type.Sum.value))
    return qweay__pfuh != 0


@register_jitable
def _handle_small_data_variable(in_arr, on_arr, win, minp, rank, n_pes,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    bvx__lmu = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    vlgxw__fdt = bodo.libs.distributed_api.gatherv(in_arr)
    ftf__tly = bodo.libs.distributed_api.gatherv(on_arr)
    if rank == 0:
        start, end = _build_indexer(ftf__tly, bvx__lmu, win, False, True)
        acbs__uil = roll_var_linear_generic_seq(vlgxw__fdt, ftf__tly, win,
            minp, start, end, init_data, add_obs, remove_obs, calc_out)
    else:
        acbs__uil = np.empty(bvx__lmu, np.float64)
    bodo.libs.distributed_api.bcast(acbs__uil)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return acbs__uil[start:end]


@register_jitable
def _handle_small_data_variable_apply(in_arr, on_arr, index_arr, win, minp,
    rank, n_pes, kernel_func, raw):
    N = len(in_arr)
    bvx__lmu = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    vlgxw__fdt = bodo.libs.distributed_api.gatherv(in_arr)
    ftf__tly = bodo.libs.distributed_api.gatherv(on_arr)
    bcc__dvyx = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        start, end = _build_indexer(ftf__tly, bvx__lmu, win, False, True)
        acbs__uil = roll_variable_apply_seq(vlgxw__fdt, ftf__tly, bcc__dvyx,
            win, minp, start, end, kernel_func, raw)
    else:
        acbs__uil = np.empty(bvx__lmu, np.float64)
    bodo.libs.distributed_api.bcast(acbs__uil)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return acbs__uil[start:end]


@register_jitable(cache=True)
def _dropna(arr):
    mvppu__oes = len(arr)
    pxnw__eyv = mvppu__oes - np.isnan(arr).sum()
    A = np.empty(pxnw__eyv, arr.dtype)
    rmd__jhcf = 0
    for exna__tad in range(mvppu__oes):
        val = arr[exna__tad]
        if not np.isnan(val):
            A[rmd__jhcf] = val
            rmd__jhcf += 1
    return A


def alloc_shift(n, A, s=None):
    return np.empty(n, A.dtype)


@overload(alloc_shift, no_unliteral=True)
def alloc_shift_overload(n, A, s=None):
    if not isinstance(A, types.Array):
        return lambda n, A, s=None: bodo.utils.utils.alloc_type(n, A, s)
    if isinstance(A.dtype, types.Integer):
        return lambda n, A, s=None: np.empty(n, np.float64)
    return lambda n, A, s=None: np.empty(n, A.dtype)


def alloc_pct_change(n, A):
    return np.empty(n, A.dtype)


@overload(alloc_pct_change, no_unliteral=True)
def alloc_pct_change_overload(n, A):
    if isinstance(A.dtype, types.Integer):
        return lambda n, A: np.empty(n, np.float64)
    return lambda n, A: np.empty(n, A.dtype)


def prep_values(A):
    return A.astype('float64')


@overload(prep_values, no_unliteral=True)
def prep_values_overload(A):
    if A == types.Array(types.float64, 1, 'C'):
        return lambda A: A
    return lambda A: A.astype(np.float64)


@register_jitable
def _validate_roll_fixed_args(win, minp):
    if win < 0:
        raise ValueError('window must be non-negative')
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if minp > win:
        raise ValueError('min_periods must be <= window')


@register_jitable
def _validate_roll_var_args(minp, center):
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if center:
        raise NotImplementedError(
            'rolling: center is not implemented for datetimelike and offset based windows'
            )
