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
        lbs__wwj = arr.copy(dtype=types.float64)
        return signature(lbs__wwj, *unliteral_all(args))


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
    esv__aoobo = get_overload_const_str(fname)
    if esv__aoobo not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (fixed window) function {}'.format
            (esv__aoobo))
    if esv__aoobo in ('median', 'min', 'max'):
        mjuja__fnli = 'def kernel_func(A):\n'
        mjuja__fnli += '  if np.isnan(A).sum() != 0: return np.nan\n'
        mjuja__fnli += '  return np.{}(A)\n'.format(esv__aoobo)
        wuu__nbcp = {}
        exec(mjuja__fnli, {'np': np}, wuu__nbcp)
        kernel_func = register_jitable(wuu__nbcp['kernel_func'])
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        esv__aoobo]
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
    esv__aoobo = get_overload_const_str(fname)
    if esv__aoobo not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (variable window) function {}'.
            format(esv__aoobo))
    if esv__aoobo in ('median', 'min', 'max'):
        mjuja__fnli = 'def kernel_func(A):\n'
        mjuja__fnli += '  arr  = dropna(A)\n'
        mjuja__fnli += '  if len(arr) == 0: return np.nan\n'
        mjuja__fnli += '  return np.{}(arr)\n'.format(esv__aoobo)
        wuu__nbcp = {}
        exec(mjuja__fnli, {'np': np, 'dropna': _dropna}, wuu__nbcp)
        kernel_func = register_jitable(wuu__nbcp['kernel_func'])
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        esv__aoobo]
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
        mok__zrk = _border_icomm(in_arr, rank, n_pes, halo_size, True, center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            urhup__hgy) = mok__zrk
    output, data = roll_fixed_linear_generic_seq(in_arr, win, minp, center,
        init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(urhup__hgy, True)
            for cqsxy__zvi in range(0, halo_size):
                data = add_obs(r_recv_buff[cqsxy__zvi], *data)
                slnxf__dze = in_arr[N + cqsxy__zvi - win]
                data = remove_obs(slnxf__dze, *data)
                output[N + cqsxy__zvi - offset] = calc_out(minp, *data)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            data = init_data()
            for cqsxy__zvi in range(0, halo_size):
                data = add_obs(l_recv_buff[cqsxy__zvi], *data)
            for cqsxy__zvi in range(0, win - 1):
                data = add_obs(in_arr[cqsxy__zvi], *data)
                if cqsxy__zvi > offset:
                    slnxf__dze = l_recv_buff[cqsxy__zvi - offset - 1]
                    data = remove_obs(slnxf__dze, *data)
                if cqsxy__zvi >= offset:
                    output[cqsxy__zvi - offset] = calc_out(minp, *data)
    return output


@register_jitable
def roll_fixed_linear_generic_seq(in_arr, win, minp, center, init_data,
    add_obs, remove_obs, calc_out):
    data = init_data()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    output = np.empty(N, dtype=np.float64)
    fxd__hgqxc = max(minp, 1) - 1
    fxd__hgqxc = min(fxd__hgqxc, N)
    for cqsxy__zvi in range(0, fxd__hgqxc):
        data = add_obs(in_arr[cqsxy__zvi], *data)
        if cqsxy__zvi >= offset:
            output[cqsxy__zvi - offset] = calc_out(minp, *data)
    for cqsxy__zvi in range(fxd__hgqxc, N):
        val = in_arr[cqsxy__zvi]
        data = add_obs(val, *data)
        if cqsxy__zvi > win - 1:
            slnxf__dze = in_arr[cqsxy__zvi - win]
            data = remove_obs(slnxf__dze, *data)
        output[cqsxy__zvi - offset] = calc_out(minp, *data)
    dldlw__jxza = data
    for cqsxy__zvi in range(N, N + offset):
        if cqsxy__zvi > win - 1:
            slnxf__dze = in_arr[cqsxy__zvi - win]
            data = remove_obs(slnxf__dze, *data)
        output[cqsxy__zvi - offset] = calc_out(minp, *data)
    return output, dldlw__jxza


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
        mok__zrk = _border_icomm(in_arr, rank, n_pes, halo_size, True, center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            urhup__hgy) = mok__zrk
        if raw == False:
            zkkt__ulqbv = _border_icomm(index_arr, rank, n_pes, halo_size, 
                True, center)
            (l_recv_buff_idx, r_recv_buff_idx, xmugy__xoh, cyzd__ebmq,
                aluy__poii, xpo__lgz) = zkkt__ulqbv
    output = roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
        kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if raw == False:
            _border_send_wait(cyzd__ebmq, xmugy__xoh, rank, n_pes, True, center
                )
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(urhup__hgy, True)
            if raw == False:
                bodo.libs.distributed_api.wait(xpo__lgz, True)
            recv_right_compute(output, in_arr, index_arr, N, win, minp,
                offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            if raw == False:
                bodo.libs.distributed_api.wait(aluy__poii, True)
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
            dldlw__jxza = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
            itm__hxo = 0
            for cqsxy__zvi in range(max(N - offset, 0), N):
                data = dldlw__jxza[itm__hxo:itm__hxo + win]
                if win - np.isnan(data).sum() < minp:
                    output[cqsxy__zvi] = np.nan
                else:
                    output[cqsxy__zvi] = kernel_func(data)
                itm__hxo += 1
        return impl

    def impl_series(output, in_arr, index_arr, N, win, minp, offset,
        r_recv_buff, r_recv_buff_idx, kernel_func, raw):
        dldlw__jxza = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
        kfmni__chbhq = np.concatenate((index_arr[N - win + 1:],
            r_recv_buff_idx))
        itm__hxo = 0
        for cqsxy__zvi in range(max(N - offset, 0), N):
            data = dldlw__jxza[itm__hxo:itm__hxo + win]
            if win - np.isnan(data).sum() < minp:
                output[cqsxy__zvi] = np.nan
            else:
                output[cqsxy__zvi] = kernel_func(pd.Series(data,
                    kfmni__chbhq[itm__hxo:itm__hxo + win]))
            itm__hxo += 1
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
            dldlw__jxza = np.concatenate((l_recv_buff, in_arr[:win - 1]))
            for cqsxy__zvi in range(0, win - offset - 1):
                data = dldlw__jxza[cqsxy__zvi:cqsxy__zvi + win]
                if win - np.isnan(data).sum() < minp:
                    output[cqsxy__zvi] = np.nan
                else:
                    output[cqsxy__zvi] = kernel_func(data)
        return impl

    def impl_series(output, in_arr, index_arr, win, minp, offset,
        l_recv_buff, l_recv_buff_idx, kernel_func, raw):
        dldlw__jxza = np.concatenate((l_recv_buff, in_arr[:win - 1]))
        kfmni__chbhq = np.concatenate((l_recv_buff_idx, index_arr[:win - 1]))
        for cqsxy__zvi in range(0, win - offset - 1):
            data = dldlw__jxza[cqsxy__zvi:cqsxy__zvi + win]
            if win - np.isnan(data).sum() < minp:
                output[cqsxy__zvi] = np.nan
            else:
                output[cqsxy__zvi] = kernel_func(pd.Series(data,
                    kfmni__chbhq[cqsxy__zvi:cqsxy__zvi + win]))
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
        for cqsxy__zvi in range(0, N):
            start = max(cqsxy__zvi - win + 1 + offset, 0)
            end = min(cqsxy__zvi + 1 + offset, N)
            data = in_arr[start:end]
            if end - start - np.isnan(data).sum() < minp:
                output[cqsxy__zvi] = np.nan
            else:
                output[cqsxy__zvi] = apply_func(kernel_func, data,
                    index_arr, start, end, raw)
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
        mok__zrk = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, qct__lew, l_recv_req,
            qzz__yrfsm) = mok__zrk
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start,
        end, init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(qct__lew, qct__lew, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(qzz__yrfsm, True)
            num_zero_starts = 0
            for cqsxy__zvi in range(0, N):
                if start[cqsxy__zvi] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            data = init_data()
            for ate__cnx in range(recv_starts[0], len(l_recv_t_buff)):
                data = add_obs(l_recv_buff[ate__cnx], *data)
            if right_closed:
                data = add_obs(in_arr[0], *data)
            output[0] = calc_out(minp, *data)
            for cqsxy__zvi in range(1, num_zero_starts):
                s = recv_starts[cqsxy__zvi]
                wzjr__foqp = end[cqsxy__zvi]
                for ate__cnx in range(recv_starts[cqsxy__zvi - 1], s):
                    data = remove_obs(l_recv_buff[ate__cnx], *data)
                for ate__cnx in range(end[cqsxy__zvi - 1], wzjr__foqp):
                    data = add_obs(in_arr[ate__cnx], *data)
                output[cqsxy__zvi] = calc_out(minp, *data)
    return output


@register_jitable(cache=True)
def _get_var_recv_starts(on_arr, l_recv_t_buff, num_zero_starts, win):
    recv_starts = np.zeros(num_zero_starts, np.int64)
    halo_size = len(l_recv_t_buff)
    yuz__hrri = cast_dt64_arr_to_int(on_arr)
    left_closed = False
    apr__idjp = yuz__hrri[0] - win
    if left_closed:
        apr__idjp -= 1
    recv_starts[0] = halo_size
    for ate__cnx in range(0, halo_size):
        if l_recv_t_buff[ate__cnx] > apr__idjp:
            recv_starts[0] = ate__cnx
            break
    for cqsxy__zvi in range(1, num_zero_starts):
        apr__idjp = yuz__hrri[cqsxy__zvi] - win
        if left_closed:
            apr__idjp -= 1
        recv_starts[cqsxy__zvi] = halo_size
        for ate__cnx in range(recv_starts[cqsxy__zvi - 1], halo_size):
            if l_recv_t_buff[ate__cnx] > apr__idjp:
                recv_starts[cqsxy__zvi] = ate__cnx
                break
    return recv_starts


@register_jitable
def roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start, end,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    output = np.empty(N, np.float64)
    data = init_data()
    for ate__cnx in range(start[0], end[0]):
        data = add_obs(in_arr[ate__cnx], *data)
    output[0] = calc_out(minp, *data)
    for cqsxy__zvi in range(1, N):
        s = start[cqsxy__zvi]
        wzjr__foqp = end[cqsxy__zvi]
        for ate__cnx in range(start[cqsxy__zvi - 1], s):
            data = remove_obs(in_arr[ate__cnx], *data)
        for ate__cnx in range(end[cqsxy__zvi - 1], wzjr__foqp):
            data = add_obs(in_arr[ate__cnx], *data)
        output[cqsxy__zvi] = calc_out(minp, *data)
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
        mok__zrk = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, qct__lew, l_recv_req,
            qzz__yrfsm) = mok__zrk
        if raw == False:
            zkkt__ulqbv = _border_icomm_var(index_arr, on_arr, rank, n_pes, win
                )
            (l_recv_buff_idx, wcth__evk, cyzd__ebmq, nwicv__zmz, aluy__poii,
                mtsmy__ojmz) = zkkt__ulqbv
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
        start, end, kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(qct__lew, qct__lew, rank, n_pes, True, False)
        if raw == False:
            _border_send_wait(cyzd__ebmq, cyzd__ebmq, rank, n_pes, True, False)
            _border_send_wait(nwicv__zmz, nwicv__zmz, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(qzz__yrfsm, True)
            if raw == False:
                bodo.libs.distributed_api.wait(aluy__poii, True)
                bodo.libs.distributed_api.wait(mtsmy__ojmz, True)
            num_zero_starts = 0
            for cqsxy__zvi in range(0, N):
                if start[cqsxy__zvi] != 0:
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
            for cqsxy__zvi in range(0, num_zero_starts):
                smb__uyeu = recv_starts[cqsxy__zvi]
                xexki__inhx = np.concatenate((l_recv_buff[smb__uyeu:],
                    in_arr[:cqsxy__zvi + 1]))
                if len(xexki__inhx) - np.isnan(xexki__inhx).sum() >= minp:
                    output[cqsxy__zvi] = kernel_func(xexki__inhx)
                else:
                    output[cqsxy__zvi] = np.nan
        return impl

    def impl_series(output, in_arr, index_arr, num_zero_starts, recv_starts,
        l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
        for cqsxy__zvi in range(0, num_zero_starts):
            smb__uyeu = recv_starts[cqsxy__zvi]
            xexki__inhx = np.concatenate((l_recv_buff[smb__uyeu:], in_arr[:
                cqsxy__zvi + 1]))
            cpfad__cjes = np.concatenate((l_recv_buff_idx[smb__uyeu:],
                index_arr[:cqsxy__zvi + 1]))
            if len(xexki__inhx) - np.isnan(xexki__inhx).sum() >= minp:
                output[cqsxy__zvi] = kernel_func(pd.Series(xexki__inhx,
                    cpfad__cjes))
            else:
                output[cqsxy__zvi] = np.nan
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
    for cqsxy__zvi in range(0, N):
        s = start[cqsxy__zvi]
        wzjr__foqp = end[cqsxy__zvi]
        data = in_arr[s:wzjr__foqp]
        if wzjr__foqp - s - np.isnan(data).sum() >= minp:
            output[cqsxy__zvi] = kernel_func(data)
        else:
            output[cqsxy__zvi] = np.nan
    return output


def roll_variable_apply_seq_impl_series(in_arr, on_arr, index_arr, win,
    minp, start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for cqsxy__zvi in range(0, N):
        s = start[cqsxy__zvi]
        wzjr__foqp = end[cqsxy__zvi]
        data = in_arr[s:wzjr__foqp]
        if wzjr__foqp - s - np.isnan(data).sum() >= minp:
            output[cqsxy__zvi] = kernel_func(pd.Series(data, index_arr[s:
                wzjr__foqp]))
        else:
            output[cqsxy__zvi] = np.nan
    return output


@register_jitable(cache=True)
def _build_indexer(on_arr, N, win, left_closed, right_closed):
    yuz__hrri = cast_dt64_arr_to_int(on_arr)
    start = np.empty(N, np.int64)
    end = np.empty(N, np.int64)
    start[0] = 0
    if right_closed:
        end[0] = 1
    else:
        end[0] = 0
    for cqsxy__zvi in range(1, N):
        gcyri__xjpjh = yuz__hrri[cqsxy__zvi]
        apr__idjp = yuz__hrri[cqsxy__zvi] - win
        if left_closed:
            apr__idjp -= 1
        start[cqsxy__zvi] = cqsxy__zvi
        for ate__cnx in range(start[cqsxy__zvi - 1], cqsxy__zvi):
            if yuz__hrri[ate__cnx] > apr__idjp:
                start[cqsxy__zvi] = ate__cnx
                break
        if yuz__hrri[end[cqsxy__zvi - 1]] <= gcyri__xjpjh:
            end[cqsxy__zvi] = cqsxy__zvi + 1
        else:
            end[cqsxy__zvi] = end[cqsxy__zvi - 1]
        if not right_closed:
            end[cqsxy__zvi] -= 1
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
        usysh__ezco = sum_x / nobs
        if neg_ct == 0 and usysh__ezco < 0.0:
            usysh__ezco = 0
        elif neg_ct == nobs and usysh__ezco > 0.0:
            usysh__ezco = 0
    else:
        usysh__ezco = np.nan
    return usysh__ezco


@register_jitable
def init_data_var():
    return 0, 0.0, 0.0


@register_jitable
def add_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs += 1
        fhi__bznfm = val - mean_x
        mean_x += fhi__bznfm / nobs
        ssqdm_x += (nobs - 1) * fhi__bznfm ** 2 / nobs
    return nobs, mean_x, ssqdm_x


@register_jitable
def remove_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs -= 1
        if nobs != 0:
            fhi__bznfm = val - mean_x
            mean_x -= fhi__bznfm / nobs
            ssqdm_x -= (nobs + 1) * fhi__bznfm ** 2 / nobs
        else:
            mean_x = 0.0
            ssqdm_x = 0.0
    return nobs, mean_x, ssqdm_x


@register_jitable
def calc_var(minp, nobs, mean_x, ssqdm_x):
    rwdd__iytf = 1.0
    usysh__ezco = np.nan
    if nobs >= minp and nobs > rwdd__iytf:
        if nobs == 1:
            usysh__ezco = 0.0
        else:
            usysh__ezco = ssqdm_x / (nobs - rwdd__iytf)
            if usysh__ezco < 0.0:
                usysh__ezco = 0.0
    return usysh__ezco


@register_jitable
def calc_std(minp, nobs, mean_x, ssqdm_x):
    xyykg__qok = calc_var(minp, nobs, mean_x, ssqdm_x)
    return np.sqrt(xyykg__qok)


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
        mok__zrk = _border_icomm(in_arr, rank, n_pes, halo_size, send_right,
            send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            urhup__hgy) = mok__zrk
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
                bodo.libs.distributed_api.wait(urhup__hgy, True)
                for cqsxy__zvi in range(0, halo_size):
                    if bodo.libs.array_kernels.isna(r_recv_buff, cqsxy__zvi):
                        bodo.libs.array_kernels.setna(output, N - halo_size +
                            cqsxy__zvi)
                        continue
                    output[N - halo_size + cqsxy__zvi] = r_recv_buff[cqsxy__zvi
                        ]
    return output


@register_jitable(cache=True)
def shift_seq(in_arr, shift, output, is_parallel_str=False):
    N = len(in_arr)
    nwbth__tqorw = 1 if shift > 0 else -1
    shift = nwbth__tqorw * min(abs(shift), N)
    if shift > 0 and (not is_parallel_str or bodo.get_rank() == 0):
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    start = max(shift, 0)
    end = min(N, N + shift)
    for cqsxy__zvi in range(start, end):
        if bodo.libs.array_kernels.isna(in_arr, cqsxy__zvi - shift):
            bodo.libs.array_kernels.setna(output, cqsxy__zvi)
            continue
        output[cqsxy__zvi] = in_arr[cqsxy__zvi - shift]
    if shift < 0:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    return output


@register_jitable
def shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
    l_recv_req, l_recv_buff, output):
    _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
    if rank != 0:
        bodo.libs.distributed_api.wait(l_recv_req, True)
        for cqsxy__zvi in range(0, halo_size):
            if bodo.libs.array_kernels.isna(l_recv_buff, cqsxy__zvi):
                bodo.libs.array_kernels.setna(output, cqsxy__zvi)
                continue
            output[cqsxy__zvi] = l_recv_buff[cqsxy__zvi]


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
        mok__zrk = _border_icomm(in_arr, rank, n_pes, halo_size, send_right,
            send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            urhup__hgy) = mok__zrk
    output = pct_change_seq(in_arr, shift)
    if parallel:
        if send_right:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
            if rank != 0:
                bodo.libs.distributed_api.wait(l_recv_req, True)
                for cqsxy__zvi in range(0, halo_size):
                    ixk__hgs = l_recv_buff[cqsxy__zvi]
                    output[cqsxy__zvi] = (in_arr[cqsxy__zvi] - ixk__hgs
                        ) / ixk__hgs
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(urhup__hgy, True)
                for cqsxy__zvi in range(0, halo_size):
                    ixk__hgs = r_recv_buff[cqsxy__zvi]
                    output[N - halo_size + cqsxy__zvi] = (in_arr[N -
                        halo_size + cqsxy__zvi] - ixk__hgs) / ixk__hgs
    return output


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_first_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[0]
    assert isinstance(arr.dtype, types.Float)
    osuki__xlc = np.nan
    if arr.dtype == types.float32:
        osuki__xlc = np.float32('nan')

    def impl(arr):
        for cqsxy__zvi in range(len(arr)):
            if not bodo.libs.array_kernels.isna(arr, cqsxy__zvi):
                return arr[cqsxy__zvi]
        return osuki__xlc
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_last_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[-1]
    assert isinstance(arr.dtype, types.Float)
    osuki__xlc = np.nan
    if arr.dtype == types.float32:
        osuki__xlc = np.float32('nan')

    def impl(arr):
        ujet__jkcym = len(arr)
        for cqsxy__zvi in range(len(arr)):
            itm__hxo = ujet__jkcym - cqsxy__zvi - 1
            if not bodo.libs.array_kernels.isna(arr, itm__hxo):
                return arr[itm__hxo]
        return osuki__xlc
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_one_from_arr_dtype(arr):
    one = arr.dtype(1)
    return lambda arr: one


@register_jitable(cache=True)
def pct_change_seq(in_arr, shift):
    N = len(in_arr)
    output = alloc_pct_change(N, in_arr)
    nwbth__tqorw = 1 if shift > 0 else -1
    shift = nwbth__tqorw * min(abs(shift), N)
    if shift > 0:
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    else:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    if shift > 0:
        zbzx__ote = get_first_non_na(in_arr[:shift])
        fjpj__oajnl = get_last_non_na(in_arr[:shift])
    else:
        zbzx__ote = get_last_non_na(in_arr[:-shift])
        fjpj__oajnl = get_first_non_na(in_arr[:-shift])
    one = get_one_from_arr_dtype(output)
    start = max(shift, 0)
    end = min(N, N + shift)
    for cqsxy__zvi in range(start, end):
        ixk__hgs = in_arr[cqsxy__zvi - shift]
        if np.isnan(ixk__hgs):
            ixk__hgs = zbzx__ote
        else:
            zbzx__ote = ixk__hgs
        val = in_arr[cqsxy__zvi]
        if np.isnan(val):
            val = fjpj__oajnl
        else:
            fjpj__oajnl = val
        output[cqsxy__zvi] = val / ixk__hgs - one
    return output


@register_jitable(cache=True)
def _border_icomm(in_arr, rank, n_pes, halo_size, send_right=True,
    send_left=False):
    apdwa__lyls = np.int32(comm_border_tag)
    l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    r_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    if send_right and rank != n_pes - 1:
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            halo_size, np.int32(rank + 1), apdwa__lyls, True)
    if send_right and rank != 0:
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, halo_size,
            np.int32(rank - 1), apdwa__lyls, True)
    if send_left and rank != 0:
        l_send_req = bodo.libs.distributed_api.isend(in_arr[:halo_size],
            halo_size, np.int32(rank - 1), apdwa__lyls, True)
    if send_left and rank != n_pes - 1:
        urhup__hgy = bodo.libs.distributed_api.irecv(r_recv_buff, halo_size,
            np.int32(rank + 1), apdwa__lyls, True)
    return (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
        urhup__hgy)


@register_jitable(cache=True)
def _border_icomm_var(in_arr, on_arr, rank, n_pes, win_size):
    apdwa__lyls = np.int32(comm_border_tag)
    N = len(on_arr)
    halo_size = N
    end = on_arr[-1]
    for ate__cnx in range(-2, -N, -1):
        nrqwm__vov = on_arr[ate__cnx]
        if end - nrqwm__vov >= win_size:
            halo_size = -ate__cnx
            break
    if rank != n_pes - 1:
        bodo.libs.distributed_api.send(halo_size, np.int32(rank + 1),
            apdwa__lyls)
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), apdwa__lyls, True)
        qct__lew = bodo.libs.distributed_api.isend(on_arr[-halo_size:], np.
            int32(halo_size), np.int32(rank + 1), apdwa__lyls, True)
    if rank != 0:
        halo_size = bodo.libs.distributed_api.recv(np.int64, np.int32(rank -
            1), apdwa__lyls)
        l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr)
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, np.int32(
            halo_size), np.int32(rank - 1), apdwa__lyls, True)
        l_recv_t_buff = np.empty(halo_size, np.int64)
        qzz__yrfsm = bodo.libs.distributed_api.irecv(l_recv_t_buff, np.
            int32(halo_size), np.int32(rank - 1), apdwa__lyls, True)
    return (l_recv_buff, l_recv_t_buff, r_send_req, qct__lew, l_recv_req,
        qzz__yrfsm)


@register_jitable
def _border_send_wait(r_send_req, l_send_req, rank, n_pes, right, left):
    if right and rank != n_pes - 1:
        bodo.libs.distributed_api.wait(r_send_req, True)
    if left and rank != 0:
        bodo.libs.distributed_api.wait(l_send_req, True)


@register_jitable
def _is_small_for_parallel(N, halo_size):
    ppyit__con = bodo.libs.distributed_api.dist_reduce(int(N <= 2 *
        halo_size + 1), np.int32(Reduce_Type.Sum.value))
    return ppyit__con != 0


@register_jitable
def _handle_small_data(in_arr, win, minp, center, rank, n_pes, init_data,
    add_obs, remove_obs, calc_out):
    N = len(in_arr)
    egeh__ogg = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32
        (Reduce_Type.Sum.value))
    dohl__rzqgd = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        gayut__uxclz, vpiuj__ncbf = roll_fixed_linear_generic_seq(dohl__rzqgd,
            win, minp, center, init_data, add_obs, remove_obs, calc_out)
    else:
        gayut__uxclz = np.empty(egeh__ogg, np.float64)
    bodo.libs.distributed_api.bcast(gayut__uxclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return gayut__uxclz[start:end]


@register_jitable
def _handle_small_data_apply(in_arr, index_arr, win, minp, center, rank,
    n_pes, kernel_func, raw=True):
    N = len(in_arr)
    egeh__ogg = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32
        (Reduce_Type.Sum.value))
    dohl__rzqgd = bodo.libs.distributed_api.gatherv(in_arr)
    zggz__zccka = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        gayut__uxclz = roll_fixed_apply_seq(dohl__rzqgd, zggz__zccka, win,
            minp, center, kernel_func, raw)
    else:
        gayut__uxclz = np.empty(egeh__ogg, np.float64)
    bodo.libs.distributed_api.bcast(gayut__uxclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return gayut__uxclz[start:end]


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
    egeh__ogg = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.int32
        (Reduce_Type.Sum.value))
    dohl__rzqgd = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        gayut__uxclz = alloc_shift(len(dohl__rzqgd), dohl__rzqgd, (-1,))
        shift_seq(dohl__rzqgd, shift, gayut__uxclz)
        lhsw__mvat = bcast_n_chars_if_str_binary_arr(gayut__uxclz)
    else:
        lhsw__mvat = bcast_n_chars_if_str_binary_arr(in_arr)
        gayut__uxclz = alloc_shift(egeh__ogg, in_arr, (lhsw__mvat,))
    bodo.libs.distributed_api.bcast(gayut__uxclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return gayut__uxclz[start:end]


@register_jitable
def _handle_small_data_pct_change(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    egeh__ogg = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    dohl__rzqgd = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        gayut__uxclz = pct_change_seq(dohl__rzqgd, shift)
    else:
        gayut__uxclz = alloc_pct_change(egeh__ogg, in_arr)
    bodo.libs.distributed_api.bcast(gayut__uxclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return gayut__uxclz[start:end]


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
        mkkm__xkx = 1
    else:
        start = on_arr[0]
        end = on_arr[-1]
        alm__jscl = end - start
        mkkm__xkx = int(alm__jscl <= win_size)
    ppyit__con = bodo.libs.distributed_api.dist_reduce(mkkm__xkx, np.int32(
        Reduce_Type.Sum.value))
    return ppyit__con != 0


@register_jitable
def _handle_small_data_variable(in_arr, on_arr, win, minp, rank, n_pes,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    egeh__ogg = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    dohl__rzqgd = bodo.libs.distributed_api.gatherv(in_arr)
    wvtf__bkyi = bodo.libs.distributed_api.gatherv(on_arr)
    if rank == 0:
        start, end = _build_indexer(wvtf__bkyi, egeh__ogg, win, False, True)
        gayut__uxclz = roll_var_linear_generic_seq(dohl__rzqgd, wvtf__bkyi,
            win, minp, start, end, init_data, add_obs, remove_obs, calc_out)
    else:
        gayut__uxclz = np.empty(egeh__ogg, np.float64)
    bodo.libs.distributed_api.bcast(gayut__uxclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return gayut__uxclz[start:end]


@register_jitable
def _handle_small_data_variable_apply(in_arr, on_arr, index_arr, win, minp,
    rank, n_pes, kernel_func, raw):
    N = len(in_arr)
    egeh__ogg = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    dohl__rzqgd = bodo.libs.distributed_api.gatherv(in_arr)
    wvtf__bkyi = bodo.libs.distributed_api.gatherv(on_arr)
    zggz__zccka = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        start, end = _build_indexer(wvtf__bkyi, egeh__ogg, win, False, True)
        gayut__uxclz = roll_variable_apply_seq(dohl__rzqgd, wvtf__bkyi,
            zggz__zccka, win, minp, start, end, kernel_func, raw)
    else:
        gayut__uxclz = np.empty(egeh__ogg, np.float64)
    bodo.libs.distributed_api.bcast(gayut__uxclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return gayut__uxclz[start:end]


@register_jitable(cache=True)
def _dropna(arr):
    biui__klwh = len(arr)
    llgs__xrao = biui__klwh - np.isnan(arr).sum()
    A = np.empty(llgs__xrao, arr.dtype)
    vjofp__cxq = 0
    for cqsxy__zvi in range(biui__klwh):
        val = arr[cqsxy__zvi]
        if not np.isnan(val):
            A[vjofp__cxq] = val
            vjofp__cxq += 1
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
