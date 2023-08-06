import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    oeq__tnekx = hi - lo
    if oeq__tnekx < 2:
        return
    if oeq__tnekx < MIN_MERGE:
        ctx__snj = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + ctx__snj, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    pgsf__bsuvm = minRunLength(oeq__tnekx)
    while True:
        cfgfe__vfudw = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if cfgfe__vfudw < pgsf__bsuvm:
            zwhe__gkk = (oeq__tnekx if oeq__tnekx <= pgsf__bsuvm else
                pgsf__bsuvm)
            binarySort(key_arrs, lo, lo + zwhe__gkk, lo + cfgfe__vfudw, data)
            cfgfe__vfudw = zwhe__gkk
        stackSize = pushRun(stackSize, runBase, runLen, lo, cfgfe__vfudw)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += cfgfe__vfudw
        oeq__tnekx -= cfgfe__vfudw
        if oeq__tnekx == 0:
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
        ewoql__gguy = getitem_arr_tup(key_arrs, start)
        yvse__wifmn = getitem_arr_tup(data, start)
        squdd__rbz = lo
        chk__dtypu = start
        assert squdd__rbz <= chk__dtypu
        while squdd__rbz < chk__dtypu:
            lojko__hscv = squdd__rbz + chk__dtypu >> 1
            if ewoql__gguy < getitem_arr_tup(key_arrs, lojko__hscv):
                chk__dtypu = lojko__hscv
            else:
                squdd__rbz = lojko__hscv + 1
        assert squdd__rbz == chk__dtypu
        n = start - squdd__rbz
        copyRange_tup(key_arrs, squdd__rbz, key_arrs, squdd__rbz + 1, n)
        copyRange_tup(data, squdd__rbz, data, squdd__rbz + 1, n)
        setitem_arr_tup(key_arrs, squdd__rbz, ewoql__gguy)
        setitem_arr_tup(data, squdd__rbz, yvse__wifmn)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    idz__jbmls = lo + 1
    if idz__jbmls == hi:
        return 1
    if getitem_arr_tup(key_arrs, idz__jbmls) < getitem_arr_tup(key_arrs, lo):
        idz__jbmls += 1
        while idz__jbmls < hi and getitem_arr_tup(key_arrs, idz__jbmls
            ) < getitem_arr_tup(key_arrs, idz__jbmls - 1):
            idz__jbmls += 1
        reverseRange(key_arrs, lo, idz__jbmls, data)
    else:
        idz__jbmls += 1
        while idz__jbmls < hi and getitem_arr_tup(key_arrs, idz__jbmls
            ) >= getitem_arr_tup(key_arrs, idz__jbmls - 1):
            idz__jbmls += 1
    return idz__jbmls - lo


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
    ybbg__lpp = 0
    while n >= MIN_MERGE:
        ybbg__lpp |= n & 1
        n >>= 1
    return n + ybbg__lpp


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    rjku__xqxle = len(key_arrs[0])
    tmpLength = (rjku__xqxle >> 1 if rjku__xqxle < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    jupx__qhsm = (5 if rjku__xqxle < 120 else 10 if rjku__xqxle < 1542 else
        19 if rjku__xqxle < 119151 else 40)
    runBase = np.empty(jupx__qhsm, np.int64)
    runLen = np.empty(jupx__qhsm, np.int64)
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
    wfh__sulr = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert wfh__sulr >= 0
    base1 += wfh__sulr
    len1 -= wfh__sulr
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
    tvvl__hgy = 0
    lhdnp__elra = 1
    if key > getitem_arr_tup(arr, base + hint):
        nhvgd__bkw = _len - hint
        while lhdnp__elra < nhvgd__bkw and key > getitem_arr_tup(arr, base +
            hint + lhdnp__elra):
            tvvl__hgy = lhdnp__elra
            lhdnp__elra = (lhdnp__elra << 1) + 1
            if lhdnp__elra <= 0:
                lhdnp__elra = nhvgd__bkw
        if lhdnp__elra > nhvgd__bkw:
            lhdnp__elra = nhvgd__bkw
        tvvl__hgy += hint
        lhdnp__elra += hint
    else:
        nhvgd__bkw = hint + 1
        while lhdnp__elra < nhvgd__bkw and key <= getitem_arr_tup(arr, base +
            hint - lhdnp__elra):
            tvvl__hgy = lhdnp__elra
            lhdnp__elra = (lhdnp__elra << 1) + 1
            if lhdnp__elra <= 0:
                lhdnp__elra = nhvgd__bkw
        if lhdnp__elra > nhvgd__bkw:
            lhdnp__elra = nhvgd__bkw
        tmp = tvvl__hgy
        tvvl__hgy = hint - lhdnp__elra
        lhdnp__elra = hint - tmp
    assert -1 <= tvvl__hgy and tvvl__hgy < lhdnp__elra and lhdnp__elra <= _len
    tvvl__hgy += 1
    while tvvl__hgy < lhdnp__elra:
        cxebt__siif = tvvl__hgy + (lhdnp__elra - tvvl__hgy >> 1)
        if key > getitem_arr_tup(arr, base + cxebt__siif):
            tvvl__hgy = cxebt__siif + 1
        else:
            lhdnp__elra = cxebt__siif
    assert tvvl__hgy == lhdnp__elra
    return lhdnp__elra


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    lhdnp__elra = 1
    tvvl__hgy = 0
    if key < getitem_arr_tup(arr, base + hint):
        nhvgd__bkw = hint + 1
        while lhdnp__elra < nhvgd__bkw and key < getitem_arr_tup(arr, base +
            hint - lhdnp__elra):
            tvvl__hgy = lhdnp__elra
            lhdnp__elra = (lhdnp__elra << 1) + 1
            if lhdnp__elra <= 0:
                lhdnp__elra = nhvgd__bkw
        if lhdnp__elra > nhvgd__bkw:
            lhdnp__elra = nhvgd__bkw
        tmp = tvvl__hgy
        tvvl__hgy = hint - lhdnp__elra
        lhdnp__elra = hint - tmp
    else:
        nhvgd__bkw = _len - hint
        while lhdnp__elra < nhvgd__bkw and key >= getitem_arr_tup(arr, base +
            hint + lhdnp__elra):
            tvvl__hgy = lhdnp__elra
            lhdnp__elra = (lhdnp__elra << 1) + 1
            if lhdnp__elra <= 0:
                lhdnp__elra = nhvgd__bkw
        if lhdnp__elra > nhvgd__bkw:
            lhdnp__elra = nhvgd__bkw
        tvvl__hgy += hint
        lhdnp__elra += hint
    assert -1 <= tvvl__hgy and tvvl__hgy < lhdnp__elra and lhdnp__elra <= _len
    tvvl__hgy += 1
    while tvvl__hgy < lhdnp__elra:
        cxebt__siif = tvvl__hgy + (lhdnp__elra - tvvl__hgy >> 1)
        if key < getitem_arr_tup(arr, base + cxebt__siif):
            lhdnp__elra = cxebt__siif
        else:
            tvvl__hgy = cxebt__siif + 1
    assert tvvl__hgy == lhdnp__elra
    return lhdnp__elra


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
        buld__uqtv = 0
        wyzg__oqd = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                wyzg__oqd += 1
                buld__uqtv = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                buld__uqtv += 1
                wyzg__oqd = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not buld__uqtv | wyzg__oqd < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            buld__uqtv = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if buld__uqtv != 0:
                copyRange_tup(tmp, cursor1, arr, dest, buld__uqtv)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, buld__uqtv)
                dest += buld__uqtv
                cursor1 += buld__uqtv
                len1 -= buld__uqtv
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            wyzg__oqd = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if wyzg__oqd != 0:
                copyRange_tup(arr, cursor2, arr, dest, wyzg__oqd)
                copyRange_tup(arr_data, cursor2, arr_data, dest, wyzg__oqd)
                dest += wyzg__oqd
                cursor2 += wyzg__oqd
                len2 -= wyzg__oqd
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
            if not buld__uqtv >= MIN_GALLOP | wyzg__oqd >= MIN_GALLOP:
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
        buld__uqtv = 0
        wyzg__oqd = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                buld__uqtv += 1
                wyzg__oqd = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                wyzg__oqd += 1
                buld__uqtv = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not buld__uqtv | wyzg__oqd < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            buld__uqtv = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if buld__uqtv != 0:
                dest -= buld__uqtv
                cursor1 -= buld__uqtv
                len1 -= buld__uqtv
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, buld__uqtv)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    buld__uqtv)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            wyzg__oqd = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if wyzg__oqd != 0:
                dest -= wyzg__oqd
                cursor2 -= wyzg__oqd
                len2 -= wyzg__oqd
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, wyzg__oqd)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    wyzg__oqd)
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
            if not buld__uqtv >= MIN_GALLOP | wyzg__oqd >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    sibw__sshh = len(key_arrs[0])
    if tmpLength < minCapacity:
        iguyq__hslpm = minCapacity
        iguyq__hslpm |= iguyq__hslpm >> 1
        iguyq__hslpm |= iguyq__hslpm >> 2
        iguyq__hslpm |= iguyq__hslpm >> 4
        iguyq__hslpm |= iguyq__hslpm >> 8
        iguyq__hslpm |= iguyq__hslpm >> 16
        iguyq__hslpm += 1
        if iguyq__hslpm < 0:
            iguyq__hslpm = minCapacity
        else:
            iguyq__hslpm = min(iguyq__hslpm, sibw__sshh >> 1)
        tmp = alloc_arr_tup(iguyq__hslpm, key_arrs)
        tmp_data = alloc_arr_tup(iguyq__hslpm, data)
        tmpLength = iguyq__hslpm
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        tijhf__mwwt = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = tijhf__mwwt


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    wown__mjvfl = arr_tup.count
    thne__rdyh = 'def f(arr_tup, lo, hi):\n'
    for i in range(wown__mjvfl):
        thne__rdyh += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        thne__rdyh += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        thne__rdyh += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    thne__rdyh += '  return\n'
    keo__ztedx = {}
    exec(thne__rdyh, {}, keo__ztedx)
    vwyv__gri = keo__ztedx['f']
    return vwyv__gri


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    wown__mjvfl = src_arr_tup.count
    assert wown__mjvfl == dst_arr_tup.count
    thne__rdyh = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(wown__mjvfl):
        thne__rdyh += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    thne__rdyh += '  return\n'
    keo__ztedx = {}
    exec(thne__rdyh, {'copyRange': copyRange}, keo__ztedx)
    pms__nzocb = keo__ztedx['f']
    return pms__nzocb


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    wown__mjvfl = src_arr_tup.count
    assert wown__mjvfl == dst_arr_tup.count
    thne__rdyh = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(wown__mjvfl):
        thne__rdyh += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    thne__rdyh += '  return\n'
    keo__ztedx = {}
    exec(thne__rdyh, {'copyElement': copyElement}, keo__ztedx)
    pms__nzocb = keo__ztedx['f']
    return pms__nzocb


def getitem_arr_tup(arr_tup, ind):
    xgcdq__enko = [arr[ind] for arr in arr_tup]
    return tuple(xgcdq__enko)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    wown__mjvfl = arr_tup.count
    thne__rdyh = 'def f(arr_tup, ind):\n'
    thne__rdyh += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(wown__mjvfl)]), ',' if wown__mjvfl == 1 else
        '')
    keo__ztedx = {}
    exec(thne__rdyh, {}, keo__ztedx)
    uskc__budnk = keo__ztedx['f']
    return uskc__budnk


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, tww__lpb in zip(arr_tup, val_tup):
        arr[ind] = tww__lpb


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    wown__mjvfl = arr_tup.count
    thne__rdyh = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(wown__mjvfl):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            thne__rdyh += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            thne__rdyh += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    thne__rdyh += '  return\n'
    keo__ztedx = {}
    exec(thne__rdyh, {}, keo__ztedx)
    uskc__budnk = keo__ztedx['f']
    return uskc__budnk


def test():
    import time
    gaulq__xcpqt = time.time()
    yzmk__zqd = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((yzmk__zqd,), 0, 3, data)
    print('compile time', time.time() - gaulq__xcpqt)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    xzrva__lbd = np.random.ranf(n)
    blnry__weu = pd.DataFrame({'A': xzrva__lbd, 'B': data[0], 'C': data[1]})
    gaulq__xcpqt = time.time()
    mli__lls = blnry__weu.sort_values('A', inplace=False)
    nsb__skyvx = time.time()
    sort((xzrva__lbd,), 0, n, data)
    print('Bodo', time.time() - nsb__skyvx, 'Numpy', nsb__skyvx - gaulq__xcpqt)
    np.testing.assert_almost_equal(data[0], mli__lls.B.values)
    np.testing.assert_almost_equal(data[1], mli__lls.C.values)


if __name__ == '__main__':
    test()
