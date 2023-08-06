import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    denrw__kxyzh = hi - lo
    if denrw__kxyzh < 2:
        return
    if denrw__kxyzh < MIN_MERGE:
        iey__flmo = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + iey__flmo, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    ttc__wmx = minRunLength(denrw__kxyzh)
    while True:
        sfpcs__jck = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if sfpcs__jck < ttc__wmx:
            varq__jzi = denrw__kxyzh if denrw__kxyzh <= ttc__wmx else ttc__wmx
            binarySort(key_arrs, lo, lo + varq__jzi, lo + sfpcs__jck, data)
            sfpcs__jck = varq__jzi
        stackSize = pushRun(stackSize, runBase, runLen, lo, sfpcs__jck)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += sfpcs__jck
        denrw__kxyzh -= sfpcs__jck
        if denrw__kxyzh == 0:
            break
    assert lo == hi
    stackSize, tmpLength, tmp, tmp_data, minGallop = mergeForceCollapse(
        stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
        tmp_data, minGallop)
    assert stackSize == 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def binarySort(key_arrs, lo, hi, start, data):
    assert lo <= start and start <= hi
    if start == lo:
        start += 1
    while start < hi:
        agjp__rfrpn = getitem_arr_tup(key_arrs, start)
        vkwz__mmrt = getitem_arr_tup(data, start)
        jidwq__qxex = lo
        bcow__kkbws = start
        assert jidwq__qxex <= bcow__kkbws
        while jidwq__qxex < bcow__kkbws:
            ohzw__zsr = jidwq__qxex + bcow__kkbws >> 1
            if agjp__rfrpn < getitem_arr_tup(key_arrs, ohzw__zsr):
                bcow__kkbws = ohzw__zsr
            else:
                jidwq__qxex = ohzw__zsr + 1
        assert jidwq__qxex == bcow__kkbws
        n = start - jidwq__qxex
        copyRange_tup(key_arrs, jidwq__qxex, key_arrs, jidwq__qxex + 1, n)
        copyRange_tup(data, jidwq__qxex, data, jidwq__qxex + 1, n)
        setitem_arr_tup(key_arrs, jidwq__qxex, agjp__rfrpn)
        setitem_arr_tup(data, jidwq__qxex, vkwz__mmrt)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    idtmh__vow = lo + 1
    if idtmh__vow == hi:
        return 1
    if getitem_arr_tup(key_arrs, idtmh__vow) < getitem_arr_tup(key_arrs, lo):
        idtmh__vow += 1
        while idtmh__vow < hi and getitem_arr_tup(key_arrs, idtmh__vow
            ) < getitem_arr_tup(key_arrs, idtmh__vow - 1):
            idtmh__vow += 1
        reverseRange(key_arrs, lo, idtmh__vow, data)
    else:
        idtmh__vow += 1
        while idtmh__vow < hi and getitem_arr_tup(key_arrs, idtmh__vow
            ) >= getitem_arr_tup(key_arrs, idtmh__vow - 1):
            idtmh__vow += 1
    return idtmh__vow - lo


@numba.njit(no_cpython_wrapper=True, cache=True)
def reverseRange(key_arrs, lo, hi, data):
    hi -= 1
    while lo < hi:
        swap_arrs(key_arrs, lo, hi)
        swap_arrs(data, lo, hi)
        lo += 1
        hi -= 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def minRunLength(n):
    assert n >= 0
    gxdq__ywkan = 0
    while n >= MIN_MERGE:
        gxdq__ywkan |= n & 1
        n >>= 1
    return n + gxdq__ywkan


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    rxv__wyf = len(key_arrs[0])
    tmpLength = (rxv__wyf >> 1 if rxv__wyf < 2 * INITIAL_TMP_STORAGE_LENGTH
         else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    wrrak__gau = (5 if rxv__wyf < 120 else 10 if rxv__wyf < 1542 else 19 if
        rxv__wyf < 119151 else 40)
    runBase = np.empty(wrrak__gau, np.int64)
    runLen = np.empty(wrrak__gau, np.int64)
    return stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def pushRun(stackSize, runBase, runLen, runBase_val, runLen_val):
    runBase[stackSize] = runBase_val
    runLen[stackSize] = runLen_val
    stackSize += 1
    return stackSize


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeCollapse(stackSize, runBase, runLen, key_arrs, data, tmpLength,
    tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n >= 1 and runLen[n - 1] <= runLen[n] + runLen[n + 1
            ] or n >= 2 and runLen[n - 2] <= runLen[n] + runLen[n - 1]:
            if runLen[n - 1] < runLen[n + 1]:
                n -= 1
        elif runLen[n] > runLen[n + 1]:
            break
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeForceCollapse(stackSize, runBase, runLen, key_arrs, data,
    tmpLength, tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n > 0 and runLen[n - 1] < runLen[n + 1]:
            n -= 1
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeAt(stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
    tmp_data, minGallop, i):
    assert stackSize >= 2
    assert i >= 0
    assert i == stackSize - 2 or i == stackSize - 3
    base1 = runBase[i]
    len1 = runLen[i]
    base2 = runBase[i + 1]
    len2 = runLen[i + 1]
    assert len1 > 0 and len2 > 0
    assert base1 + len1 == base2
    runLen[i] = len1 + len2
    if i == stackSize - 3:
        runBase[i + 1] = runBase[i + 2]
        runLen[i + 1] = runLen[i + 2]
    stackSize -= 1
    lxyft__hrnee = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert lxyft__hrnee >= 0
    base1 += lxyft__hrnee
    len1 -= lxyft__hrnee
    if len1 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    len2 = gallopLeft(getitem_arr_tup(key_arrs, base1 + len1 - 1), key_arrs,
        base2, len2, len2 - 1)
    assert len2 >= 0
    if len2 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    if len1 <= len2:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len1)
        minGallop = mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    else:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len2)
        minGallop = mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopLeft(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    hwu__utt = 0
    frrc__inj = 1
    if key > getitem_arr_tup(arr, base + hint):
        pgylp__adj = _len - hint
        while frrc__inj < pgylp__adj and key > getitem_arr_tup(arr, base +
            hint + frrc__inj):
            hwu__utt = frrc__inj
            frrc__inj = (frrc__inj << 1) + 1
            if frrc__inj <= 0:
                frrc__inj = pgylp__adj
        if frrc__inj > pgylp__adj:
            frrc__inj = pgylp__adj
        hwu__utt += hint
        frrc__inj += hint
    else:
        pgylp__adj = hint + 1
        while frrc__inj < pgylp__adj and key <= getitem_arr_tup(arr, base +
            hint - frrc__inj):
            hwu__utt = frrc__inj
            frrc__inj = (frrc__inj << 1) + 1
            if frrc__inj <= 0:
                frrc__inj = pgylp__adj
        if frrc__inj > pgylp__adj:
            frrc__inj = pgylp__adj
        tmp = hwu__utt
        hwu__utt = hint - frrc__inj
        frrc__inj = hint - tmp
    assert -1 <= hwu__utt and hwu__utt < frrc__inj and frrc__inj <= _len
    hwu__utt += 1
    while hwu__utt < frrc__inj:
        qjje__jxtt = hwu__utt + (frrc__inj - hwu__utt >> 1)
        if key > getitem_arr_tup(arr, base + qjje__jxtt):
            hwu__utt = qjje__jxtt + 1
        else:
            frrc__inj = qjje__jxtt
    assert hwu__utt == frrc__inj
    return frrc__inj


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    frrc__inj = 1
    hwu__utt = 0
    if key < getitem_arr_tup(arr, base + hint):
        pgylp__adj = hint + 1
        while frrc__inj < pgylp__adj and key < getitem_arr_tup(arr, base +
            hint - frrc__inj):
            hwu__utt = frrc__inj
            frrc__inj = (frrc__inj << 1) + 1
            if frrc__inj <= 0:
                frrc__inj = pgylp__adj
        if frrc__inj > pgylp__adj:
            frrc__inj = pgylp__adj
        tmp = hwu__utt
        hwu__utt = hint - frrc__inj
        frrc__inj = hint - tmp
    else:
        pgylp__adj = _len - hint
        while frrc__inj < pgylp__adj and key >= getitem_arr_tup(arr, base +
            hint + frrc__inj):
            hwu__utt = frrc__inj
            frrc__inj = (frrc__inj << 1) + 1
            if frrc__inj <= 0:
                frrc__inj = pgylp__adj
        if frrc__inj > pgylp__adj:
            frrc__inj = pgylp__adj
        hwu__utt += hint
        frrc__inj += hint
    assert -1 <= hwu__utt and hwu__utt < frrc__inj and frrc__inj <= _len
    hwu__utt += 1
    while hwu__utt < frrc__inj:
        qjje__jxtt = hwu__utt + (frrc__inj - hwu__utt >> 1)
        if key < getitem_arr_tup(arr, base + qjje__jxtt):
            frrc__inj = qjje__jxtt
        else:
            hwu__utt = qjje__jxtt + 1
    assert hwu__utt == frrc__inj
    return frrc__inj


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base1, tmp, 0, len1)
    copyRange_tup(arr_data, base1, tmp_data, 0, len1)
    cursor1 = 0
    cursor2 = base2
    dest = base1
    setitem_arr_tup(arr, dest, getitem_arr_tup(arr, cursor2))
    copyElement_tup(arr_data, cursor2, arr_data, dest)
    cursor2 += 1
    dest += 1
    len2 -= 1
    if len2 == 0:
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
        return minGallop
    if len1 == 1:
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
        return minGallop
    len1, len2, cursor1, cursor2, dest, minGallop = mergeLo_inner(key_arrs,
        data, tmp_data, len1, len2, tmp, cursor1, cursor2, dest, minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len1 == 1:
        assert len2 > 0
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
    elif len1 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len2 == 0
        assert len1 > 1
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo_inner(arr, arr_data, tmp_data, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        xvez__mcooh = 0
        lqav__fckk = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                lqav__fckk += 1
                xvez__mcooh = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                xvez__mcooh += 1
                lqav__fckk = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not xvez__mcooh | lqav__fckk < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            xvez__mcooh = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if xvez__mcooh != 0:
                copyRange_tup(tmp, cursor1, arr, dest, xvez__mcooh)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, xvez__mcooh)
                dest += xvez__mcooh
                cursor1 += xvez__mcooh
                len1 -= xvez__mcooh
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            lqav__fckk = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if lqav__fckk != 0:
                copyRange_tup(arr, cursor2, arr, dest, lqav__fckk)
                copyRange_tup(arr_data, cursor2, arr_data, dest, lqav__fckk)
                dest += lqav__fckk
                cursor2 += lqav__fckk
                len2 -= lqav__fckk
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor1, arr, dest)
            copyElement_tup(tmp_data, cursor1, arr_data, dest)
            cursor1 += 1
            dest += 1
            len1 -= 1
            if len1 == 1:
                return len1, len2, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not xvez__mcooh >= MIN_GALLOP | lqav__fckk >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base2, tmp, 0, len2)
    copyRange_tup(arr_data, base2, tmp_data, 0, len2)
    cursor1 = base1 + len1 - 1
    cursor2 = len2 - 1
    dest = base2 + len2 - 1
    copyElement_tup(arr, cursor1, arr, dest)
    copyElement_tup(arr_data, cursor1, arr_data, dest)
    cursor1 -= 1
    dest -= 1
    len1 -= 1
    if len1 == 0:
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
        return minGallop
    if len2 == 1:
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
        return minGallop
    len1, len2, tmp, cursor1, cursor2, dest, minGallop = mergeHi_inner(key_arrs
        , data, tmp_data, base1, len1, len2, tmp, cursor1, cursor2, dest,
        minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len2 == 1:
        assert len1 > 0
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
    elif len2 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len1 == 0
        assert len2 > 0
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi_inner(arr, arr_data, tmp_data, base1, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        xvez__mcooh = 0
        lqav__fckk = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                xvez__mcooh += 1
                lqav__fckk = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                lqav__fckk += 1
                xvez__mcooh = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not xvez__mcooh | lqav__fckk < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            xvez__mcooh = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if xvez__mcooh != 0:
                dest -= xvez__mcooh
                cursor1 -= xvez__mcooh
                len1 -= xvez__mcooh
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, xvez__mcooh)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    xvez__mcooh)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            lqav__fckk = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if lqav__fckk != 0:
                dest -= lqav__fckk
                cursor2 -= lqav__fckk
                len2 -= lqav__fckk
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, lqav__fckk)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    lqav__fckk)
                if len2 <= 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor1, arr, dest)
            copyElement_tup(arr_data, cursor1, arr_data, dest)
            cursor1 -= 1
            dest -= 1
            len1 -= 1
            if len1 == 0:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not xvez__mcooh >= MIN_GALLOP | lqav__fckk >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    yivzr__sao = len(key_arrs[0])
    if tmpLength < minCapacity:
        vlnak__dwwqc = minCapacity
        vlnak__dwwqc |= vlnak__dwwqc >> 1
        vlnak__dwwqc |= vlnak__dwwqc >> 2
        vlnak__dwwqc |= vlnak__dwwqc >> 4
        vlnak__dwwqc |= vlnak__dwwqc >> 8
        vlnak__dwwqc |= vlnak__dwwqc >> 16
        vlnak__dwwqc += 1
        if vlnak__dwwqc < 0:
            vlnak__dwwqc = minCapacity
        else:
            vlnak__dwwqc = min(vlnak__dwwqc, yivzr__sao >> 1)
        tmp = alloc_arr_tup(vlnak__dwwqc, key_arrs)
        tmp_data = alloc_arr_tup(vlnak__dwwqc, data)
        tmpLength = vlnak__dwwqc
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        ypdu__qhokg = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = ypdu__qhokg


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    dnp__haoc = arr_tup.count
    jxy__zoe = 'def f(arr_tup, lo, hi):\n'
    for i in range(dnp__haoc):
        jxy__zoe += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        jxy__zoe += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        jxy__zoe += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    jxy__zoe += '  return\n'
    gaim__nuqd = {}
    exec(jxy__zoe, {}, gaim__nuqd)
    wfyjv__pxp = gaim__nuqd['f']
    return wfyjv__pxp


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    dnp__haoc = src_arr_tup.count
    assert dnp__haoc == dst_arr_tup.count
    jxy__zoe = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(dnp__haoc):
        jxy__zoe += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    jxy__zoe += '  return\n'
    gaim__nuqd = {}
    exec(jxy__zoe, {'copyRange': copyRange}, gaim__nuqd)
    iqrrx__llk = gaim__nuqd['f']
    return iqrrx__llk


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    dnp__haoc = src_arr_tup.count
    assert dnp__haoc == dst_arr_tup.count
    jxy__zoe = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(dnp__haoc):
        jxy__zoe += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    jxy__zoe += '  return\n'
    gaim__nuqd = {}
    exec(jxy__zoe, {'copyElement': copyElement}, gaim__nuqd)
    iqrrx__llk = gaim__nuqd['f']
    return iqrrx__llk


def getitem_arr_tup(arr_tup, ind):
    jlcub__une = [arr[ind] for arr in arr_tup]
    return tuple(jlcub__une)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    dnp__haoc = arr_tup.count
    jxy__zoe = 'def f(arr_tup, ind):\n'
    jxy__zoe += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(dnp__haoc)]), ',' if dnp__haoc == 1 else '')
    gaim__nuqd = {}
    exec(jxy__zoe, {}, gaim__nuqd)
    swqq__ksb = gaim__nuqd['f']
    return swqq__ksb


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, nne__qcb in zip(arr_tup, val_tup):
        arr[ind] = nne__qcb


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    dnp__haoc = arr_tup.count
    jxy__zoe = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(dnp__haoc):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            jxy__zoe += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            jxy__zoe += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    jxy__zoe += '  return\n'
    gaim__nuqd = {}
    exec(jxy__zoe, {}, gaim__nuqd)
    swqq__ksb = gaim__nuqd['f']
    return swqq__ksb


def test():
    import time
    xhkap__ogwuh = time.time()
    xlnhk__nqf = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((xlnhk__nqf,), 0, 3, data)
    print('compile time', time.time() - xhkap__ogwuh)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    jppju__gdwi = np.random.ranf(n)
    egwx__hooty = pd.DataFrame({'A': jppju__gdwi, 'B': data[0], 'C': data[1]})
    xhkap__ogwuh = time.time()
    bybky__dyif = egwx__hooty.sort_values('A', inplace=False)
    gic__asmpm = time.time()
    sort((jppju__gdwi,), 0, n, data)
    print('Bodo', time.time() - gic__asmpm, 'Numpy', gic__asmpm - xhkap__ogwuh)
    np.testing.assert_almost_equal(data[0], bybky__dyif.B.values)
    np.testing.assert_almost_equal(data[1], bybky__dyif.C.values)


if __name__ == '__main__':
    test()
