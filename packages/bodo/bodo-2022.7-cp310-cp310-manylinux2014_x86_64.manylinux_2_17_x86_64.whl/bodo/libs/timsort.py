import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    otbwx__dtr = hi - lo
    if otbwx__dtr < 2:
        return
    if otbwx__dtr < MIN_MERGE:
        hwvv__hyuoi = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + hwvv__hyuoi, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    sqw__wcncl = minRunLength(otbwx__dtr)
    while True:
        isah__tvg = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if isah__tvg < sqw__wcncl:
            wkd__bgk = otbwx__dtr if otbwx__dtr <= sqw__wcncl else sqw__wcncl
            binarySort(key_arrs, lo, lo + wkd__bgk, lo + isah__tvg, data)
            isah__tvg = wkd__bgk
        stackSize = pushRun(stackSize, runBase, runLen, lo, isah__tvg)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += isah__tvg
        otbwx__dtr -= isah__tvg
        if otbwx__dtr == 0:
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
        kly__ekgkv = getitem_arr_tup(key_arrs, start)
        ixne__piy = getitem_arr_tup(data, start)
        xoo__ztg = lo
        gofpl__yomil = start
        assert xoo__ztg <= gofpl__yomil
        while xoo__ztg < gofpl__yomil:
            ebz__imwvw = xoo__ztg + gofpl__yomil >> 1
            if kly__ekgkv < getitem_arr_tup(key_arrs, ebz__imwvw):
                gofpl__yomil = ebz__imwvw
            else:
                xoo__ztg = ebz__imwvw + 1
        assert xoo__ztg == gofpl__yomil
        n = start - xoo__ztg
        copyRange_tup(key_arrs, xoo__ztg, key_arrs, xoo__ztg + 1, n)
        copyRange_tup(data, xoo__ztg, data, xoo__ztg + 1, n)
        setitem_arr_tup(key_arrs, xoo__ztg, kly__ekgkv)
        setitem_arr_tup(data, xoo__ztg, ixne__piy)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    ahna__xvzi = lo + 1
    if ahna__xvzi == hi:
        return 1
    if getitem_arr_tup(key_arrs, ahna__xvzi) < getitem_arr_tup(key_arrs, lo):
        ahna__xvzi += 1
        while ahna__xvzi < hi and getitem_arr_tup(key_arrs, ahna__xvzi
            ) < getitem_arr_tup(key_arrs, ahna__xvzi - 1):
            ahna__xvzi += 1
        reverseRange(key_arrs, lo, ahna__xvzi, data)
    else:
        ahna__xvzi += 1
        while ahna__xvzi < hi and getitem_arr_tup(key_arrs, ahna__xvzi
            ) >= getitem_arr_tup(key_arrs, ahna__xvzi - 1):
            ahna__xvzi += 1
    return ahna__xvzi - lo


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
    bjf__rutii = 0
    while n >= MIN_MERGE:
        bjf__rutii |= n & 1
        n >>= 1
    return n + bjf__rutii


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    huisw__hovyf = len(key_arrs[0])
    tmpLength = (huisw__hovyf >> 1 if huisw__hovyf < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    rez__uqi = (5 if huisw__hovyf < 120 else 10 if huisw__hovyf < 1542 else
        19 if huisw__hovyf < 119151 else 40)
    runBase = np.empty(rez__uqi, np.int64)
    runLen = np.empty(rez__uqi, np.int64)
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
    gouxd__even = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert gouxd__even >= 0
    base1 += gouxd__even
    len1 -= gouxd__even
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
    pczzm__iyeif = 0
    gpvk__fsny = 1
    if key > getitem_arr_tup(arr, base + hint):
        wxw__yddek = _len - hint
        while gpvk__fsny < wxw__yddek and key > getitem_arr_tup(arr, base +
            hint + gpvk__fsny):
            pczzm__iyeif = gpvk__fsny
            gpvk__fsny = (gpvk__fsny << 1) + 1
            if gpvk__fsny <= 0:
                gpvk__fsny = wxw__yddek
        if gpvk__fsny > wxw__yddek:
            gpvk__fsny = wxw__yddek
        pczzm__iyeif += hint
        gpvk__fsny += hint
    else:
        wxw__yddek = hint + 1
        while gpvk__fsny < wxw__yddek and key <= getitem_arr_tup(arr, base +
            hint - gpvk__fsny):
            pczzm__iyeif = gpvk__fsny
            gpvk__fsny = (gpvk__fsny << 1) + 1
            if gpvk__fsny <= 0:
                gpvk__fsny = wxw__yddek
        if gpvk__fsny > wxw__yddek:
            gpvk__fsny = wxw__yddek
        tmp = pczzm__iyeif
        pczzm__iyeif = hint - gpvk__fsny
        gpvk__fsny = hint - tmp
    assert -1 <= pczzm__iyeif and pczzm__iyeif < gpvk__fsny and gpvk__fsny <= _len
    pczzm__iyeif += 1
    while pczzm__iyeif < gpvk__fsny:
        xdut__rpfm = pczzm__iyeif + (gpvk__fsny - pczzm__iyeif >> 1)
        if key > getitem_arr_tup(arr, base + xdut__rpfm):
            pczzm__iyeif = xdut__rpfm + 1
        else:
            gpvk__fsny = xdut__rpfm
    assert pczzm__iyeif == gpvk__fsny
    return gpvk__fsny


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    gpvk__fsny = 1
    pczzm__iyeif = 0
    if key < getitem_arr_tup(arr, base + hint):
        wxw__yddek = hint + 1
        while gpvk__fsny < wxw__yddek and key < getitem_arr_tup(arr, base +
            hint - gpvk__fsny):
            pczzm__iyeif = gpvk__fsny
            gpvk__fsny = (gpvk__fsny << 1) + 1
            if gpvk__fsny <= 0:
                gpvk__fsny = wxw__yddek
        if gpvk__fsny > wxw__yddek:
            gpvk__fsny = wxw__yddek
        tmp = pczzm__iyeif
        pczzm__iyeif = hint - gpvk__fsny
        gpvk__fsny = hint - tmp
    else:
        wxw__yddek = _len - hint
        while gpvk__fsny < wxw__yddek and key >= getitem_arr_tup(arr, base +
            hint + gpvk__fsny):
            pczzm__iyeif = gpvk__fsny
            gpvk__fsny = (gpvk__fsny << 1) + 1
            if gpvk__fsny <= 0:
                gpvk__fsny = wxw__yddek
        if gpvk__fsny > wxw__yddek:
            gpvk__fsny = wxw__yddek
        pczzm__iyeif += hint
        gpvk__fsny += hint
    assert -1 <= pczzm__iyeif and pczzm__iyeif < gpvk__fsny and gpvk__fsny <= _len
    pczzm__iyeif += 1
    while pczzm__iyeif < gpvk__fsny:
        xdut__rpfm = pczzm__iyeif + (gpvk__fsny - pczzm__iyeif >> 1)
        if key < getitem_arr_tup(arr, base + xdut__rpfm):
            gpvk__fsny = xdut__rpfm
        else:
            pczzm__iyeif = xdut__rpfm + 1
    assert pczzm__iyeif == gpvk__fsny
    return gpvk__fsny


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
        bng__xjalv = 0
        sfrj__tag = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                sfrj__tag += 1
                bng__xjalv = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                bng__xjalv += 1
                sfrj__tag = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not bng__xjalv | sfrj__tag < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            bng__xjalv = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if bng__xjalv != 0:
                copyRange_tup(tmp, cursor1, arr, dest, bng__xjalv)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, bng__xjalv)
                dest += bng__xjalv
                cursor1 += bng__xjalv
                len1 -= bng__xjalv
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            sfrj__tag = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if sfrj__tag != 0:
                copyRange_tup(arr, cursor2, arr, dest, sfrj__tag)
                copyRange_tup(arr_data, cursor2, arr_data, dest, sfrj__tag)
                dest += sfrj__tag
                cursor2 += sfrj__tag
                len2 -= sfrj__tag
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
            if not bng__xjalv >= MIN_GALLOP | sfrj__tag >= MIN_GALLOP:
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
        bng__xjalv = 0
        sfrj__tag = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                bng__xjalv += 1
                sfrj__tag = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                sfrj__tag += 1
                bng__xjalv = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not bng__xjalv | sfrj__tag < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            bng__xjalv = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if bng__xjalv != 0:
                dest -= bng__xjalv
                cursor1 -= bng__xjalv
                len1 -= bng__xjalv
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, bng__xjalv)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    bng__xjalv)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            sfrj__tag = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if sfrj__tag != 0:
                dest -= sfrj__tag
                cursor2 -= sfrj__tag
                len2 -= sfrj__tag
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, sfrj__tag)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    sfrj__tag)
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
            if not bng__xjalv >= MIN_GALLOP | sfrj__tag >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    udj__lmslz = len(key_arrs[0])
    if tmpLength < minCapacity:
        ajss__rggf = minCapacity
        ajss__rggf |= ajss__rggf >> 1
        ajss__rggf |= ajss__rggf >> 2
        ajss__rggf |= ajss__rggf >> 4
        ajss__rggf |= ajss__rggf >> 8
        ajss__rggf |= ajss__rggf >> 16
        ajss__rggf += 1
        if ajss__rggf < 0:
            ajss__rggf = minCapacity
        else:
            ajss__rggf = min(ajss__rggf, udj__lmslz >> 1)
        tmp = alloc_arr_tup(ajss__rggf, key_arrs)
        tmp_data = alloc_arr_tup(ajss__rggf, data)
        tmpLength = ajss__rggf
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        ggqem__njww = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = ggqem__njww


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    xep__hkivp = arr_tup.count
    dlmr__oxgvp = 'def f(arr_tup, lo, hi):\n'
    for i in range(xep__hkivp):
        dlmr__oxgvp += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        dlmr__oxgvp += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        dlmr__oxgvp += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    dlmr__oxgvp += '  return\n'
    bxum__fns = {}
    exec(dlmr__oxgvp, {}, bxum__fns)
    yyh__fkzuh = bxum__fns['f']
    return yyh__fkzuh


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    xep__hkivp = src_arr_tup.count
    assert xep__hkivp == dst_arr_tup.count
    dlmr__oxgvp = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(xep__hkivp):
        dlmr__oxgvp += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    dlmr__oxgvp += '  return\n'
    bxum__fns = {}
    exec(dlmr__oxgvp, {'copyRange': copyRange}, bxum__fns)
    upnxc__hfgo = bxum__fns['f']
    return upnxc__hfgo


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    xep__hkivp = src_arr_tup.count
    assert xep__hkivp == dst_arr_tup.count
    dlmr__oxgvp = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(xep__hkivp):
        dlmr__oxgvp += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    dlmr__oxgvp += '  return\n'
    bxum__fns = {}
    exec(dlmr__oxgvp, {'copyElement': copyElement}, bxum__fns)
    upnxc__hfgo = bxum__fns['f']
    return upnxc__hfgo


def getitem_arr_tup(arr_tup, ind):
    xayq__vcra = [arr[ind] for arr in arr_tup]
    return tuple(xayq__vcra)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    xep__hkivp = arr_tup.count
    dlmr__oxgvp = 'def f(arr_tup, ind):\n'
    dlmr__oxgvp += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(xep__hkivp)]), ',' if xep__hkivp == 1 else '')
    bxum__fns = {}
    exec(dlmr__oxgvp, {}, bxum__fns)
    mqv__zjmp = bxum__fns['f']
    return mqv__zjmp


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, kulxt__ydsva in zip(arr_tup, val_tup):
        arr[ind] = kulxt__ydsva


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    xep__hkivp = arr_tup.count
    dlmr__oxgvp = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(xep__hkivp):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            dlmr__oxgvp += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            dlmr__oxgvp += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    dlmr__oxgvp += '  return\n'
    bxum__fns = {}
    exec(dlmr__oxgvp, {}, bxum__fns)
    mqv__zjmp = bxum__fns['f']
    return mqv__zjmp


def test():
    import time
    qglfw__qvm = time.time()
    cngs__widgb = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((cngs__widgb,), 0, 3, data)
    print('compile time', time.time() - qglfw__qvm)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    ayy__gdeos = np.random.ranf(n)
    dki__tyte = pd.DataFrame({'A': ayy__gdeos, 'B': data[0], 'C': data[1]})
    qglfw__qvm = time.time()
    kafy__poehh = dki__tyte.sort_values('A', inplace=False)
    kjc__mvcvi = time.time()
    sort((ayy__gdeos,), 0, n, data)
    print('Bodo', time.time() - kjc__mvcvi, 'Numpy', kjc__mvcvi - qglfw__qvm)
    np.testing.assert_almost_equal(data[0], kafy__poehh.B.values)
    np.testing.assert_almost_equal(data[1], kafy__poehh.C.values)


if __name__ == '__main__':
    test()
