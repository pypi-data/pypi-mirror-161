import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    zopbd__neae = hi - lo
    if zopbd__neae < 2:
        return
    if zopbd__neae < MIN_MERGE:
        qzavs__puvw = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + qzavs__puvw, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    csx__wyxj = minRunLength(zopbd__neae)
    while True:
        cvzr__cflw = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if cvzr__cflw < csx__wyxj:
            cnlp__uzex = zopbd__neae if zopbd__neae <= csx__wyxj else csx__wyxj
            binarySort(key_arrs, lo, lo + cnlp__uzex, lo + cvzr__cflw, data)
            cvzr__cflw = cnlp__uzex
        stackSize = pushRun(stackSize, runBase, runLen, lo, cvzr__cflw)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += cvzr__cflw
        zopbd__neae -= cvzr__cflw
        if zopbd__neae == 0:
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
        ayaa__shfz = getitem_arr_tup(key_arrs, start)
        lgmnn__miy = getitem_arr_tup(data, start)
        hmwg__axez = lo
        rqsla__ukclk = start
        assert hmwg__axez <= rqsla__ukclk
        while hmwg__axez < rqsla__ukclk:
            oga__gnozv = hmwg__axez + rqsla__ukclk >> 1
            if ayaa__shfz < getitem_arr_tup(key_arrs, oga__gnozv):
                rqsla__ukclk = oga__gnozv
            else:
                hmwg__axez = oga__gnozv + 1
        assert hmwg__axez == rqsla__ukclk
        n = start - hmwg__axez
        copyRange_tup(key_arrs, hmwg__axez, key_arrs, hmwg__axez + 1, n)
        copyRange_tup(data, hmwg__axez, data, hmwg__axez + 1, n)
        setitem_arr_tup(key_arrs, hmwg__axez, ayaa__shfz)
        setitem_arr_tup(data, hmwg__axez, lgmnn__miy)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    aeoc__blobb = lo + 1
    if aeoc__blobb == hi:
        return 1
    if getitem_arr_tup(key_arrs, aeoc__blobb) < getitem_arr_tup(key_arrs, lo):
        aeoc__blobb += 1
        while aeoc__blobb < hi and getitem_arr_tup(key_arrs, aeoc__blobb
            ) < getitem_arr_tup(key_arrs, aeoc__blobb - 1):
            aeoc__blobb += 1
        reverseRange(key_arrs, lo, aeoc__blobb, data)
    else:
        aeoc__blobb += 1
        while aeoc__blobb < hi and getitem_arr_tup(key_arrs, aeoc__blobb
            ) >= getitem_arr_tup(key_arrs, aeoc__blobb - 1):
            aeoc__blobb += 1
    return aeoc__blobb - lo


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
    xaz__lqyyv = 0
    while n >= MIN_MERGE:
        xaz__lqyyv |= n & 1
        n >>= 1
    return n + xaz__lqyyv


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    prl__wswu = len(key_arrs[0])
    tmpLength = (prl__wswu >> 1 if prl__wswu < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    zutb__rwqae = (5 if prl__wswu < 120 else 10 if prl__wswu < 1542 else 19 if
        prl__wswu < 119151 else 40)
    runBase = np.empty(zutb__rwqae, np.int64)
    runLen = np.empty(zutb__rwqae, np.int64)
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
    fmg__vooa = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert fmg__vooa >= 0
    base1 += fmg__vooa
    len1 -= fmg__vooa
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
    ryvy__apt = 0
    lecd__vpc = 1
    if key > getitem_arr_tup(arr, base + hint):
        ijuw__wuks = _len - hint
        while lecd__vpc < ijuw__wuks and key > getitem_arr_tup(arr, base +
            hint + lecd__vpc):
            ryvy__apt = lecd__vpc
            lecd__vpc = (lecd__vpc << 1) + 1
            if lecd__vpc <= 0:
                lecd__vpc = ijuw__wuks
        if lecd__vpc > ijuw__wuks:
            lecd__vpc = ijuw__wuks
        ryvy__apt += hint
        lecd__vpc += hint
    else:
        ijuw__wuks = hint + 1
        while lecd__vpc < ijuw__wuks and key <= getitem_arr_tup(arr, base +
            hint - lecd__vpc):
            ryvy__apt = lecd__vpc
            lecd__vpc = (lecd__vpc << 1) + 1
            if lecd__vpc <= 0:
                lecd__vpc = ijuw__wuks
        if lecd__vpc > ijuw__wuks:
            lecd__vpc = ijuw__wuks
        tmp = ryvy__apt
        ryvy__apt = hint - lecd__vpc
        lecd__vpc = hint - tmp
    assert -1 <= ryvy__apt and ryvy__apt < lecd__vpc and lecd__vpc <= _len
    ryvy__apt += 1
    while ryvy__apt < lecd__vpc:
        kzdc__jfgkw = ryvy__apt + (lecd__vpc - ryvy__apt >> 1)
        if key > getitem_arr_tup(arr, base + kzdc__jfgkw):
            ryvy__apt = kzdc__jfgkw + 1
        else:
            lecd__vpc = kzdc__jfgkw
    assert ryvy__apt == lecd__vpc
    return lecd__vpc


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    lecd__vpc = 1
    ryvy__apt = 0
    if key < getitem_arr_tup(arr, base + hint):
        ijuw__wuks = hint + 1
        while lecd__vpc < ijuw__wuks and key < getitem_arr_tup(arr, base +
            hint - lecd__vpc):
            ryvy__apt = lecd__vpc
            lecd__vpc = (lecd__vpc << 1) + 1
            if lecd__vpc <= 0:
                lecd__vpc = ijuw__wuks
        if lecd__vpc > ijuw__wuks:
            lecd__vpc = ijuw__wuks
        tmp = ryvy__apt
        ryvy__apt = hint - lecd__vpc
        lecd__vpc = hint - tmp
    else:
        ijuw__wuks = _len - hint
        while lecd__vpc < ijuw__wuks and key >= getitem_arr_tup(arr, base +
            hint + lecd__vpc):
            ryvy__apt = lecd__vpc
            lecd__vpc = (lecd__vpc << 1) + 1
            if lecd__vpc <= 0:
                lecd__vpc = ijuw__wuks
        if lecd__vpc > ijuw__wuks:
            lecd__vpc = ijuw__wuks
        ryvy__apt += hint
        lecd__vpc += hint
    assert -1 <= ryvy__apt and ryvy__apt < lecd__vpc and lecd__vpc <= _len
    ryvy__apt += 1
    while ryvy__apt < lecd__vpc:
        kzdc__jfgkw = ryvy__apt + (lecd__vpc - ryvy__apt >> 1)
        if key < getitem_arr_tup(arr, base + kzdc__jfgkw):
            lecd__vpc = kzdc__jfgkw
        else:
            ryvy__apt = kzdc__jfgkw + 1
    assert ryvy__apt == lecd__vpc
    return lecd__vpc


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
        myjaz__obuxi = 0
        awo__gtr = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                awo__gtr += 1
                myjaz__obuxi = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                myjaz__obuxi += 1
                awo__gtr = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not myjaz__obuxi | awo__gtr < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            myjaz__obuxi = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if myjaz__obuxi != 0:
                copyRange_tup(tmp, cursor1, arr, dest, myjaz__obuxi)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, myjaz__obuxi)
                dest += myjaz__obuxi
                cursor1 += myjaz__obuxi
                len1 -= myjaz__obuxi
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            awo__gtr = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if awo__gtr != 0:
                copyRange_tup(arr, cursor2, arr, dest, awo__gtr)
                copyRange_tup(arr_data, cursor2, arr_data, dest, awo__gtr)
                dest += awo__gtr
                cursor2 += awo__gtr
                len2 -= awo__gtr
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
            if not myjaz__obuxi >= MIN_GALLOP | awo__gtr >= MIN_GALLOP:
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
        myjaz__obuxi = 0
        awo__gtr = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                myjaz__obuxi += 1
                awo__gtr = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                awo__gtr += 1
                myjaz__obuxi = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not myjaz__obuxi | awo__gtr < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            myjaz__obuxi = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if myjaz__obuxi != 0:
                dest -= myjaz__obuxi
                cursor1 -= myjaz__obuxi
                len1 -= myjaz__obuxi
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, myjaz__obuxi)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    myjaz__obuxi)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            awo__gtr = len2 - gallopLeft(getitem_arr_tup(arr, cursor1), tmp,
                0, len2, len2 - 1)
            if awo__gtr != 0:
                dest -= awo__gtr
                cursor2 -= awo__gtr
                len2 -= awo__gtr
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, awo__gtr)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    awo__gtr)
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
            if not myjaz__obuxi >= MIN_GALLOP | awo__gtr >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    iku__gks = len(key_arrs[0])
    if tmpLength < minCapacity:
        eghgt__dgcti = minCapacity
        eghgt__dgcti |= eghgt__dgcti >> 1
        eghgt__dgcti |= eghgt__dgcti >> 2
        eghgt__dgcti |= eghgt__dgcti >> 4
        eghgt__dgcti |= eghgt__dgcti >> 8
        eghgt__dgcti |= eghgt__dgcti >> 16
        eghgt__dgcti += 1
        if eghgt__dgcti < 0:
            eghgt__dgcti = minCapacity
        else:
            eghgt__dgcti = min(eghgt__dgcti, iku__gks >> 1)
        tmp = alloc_arr_tup(eghgt__dgcti, key_arrs)
        tmp_data = alloc_arr_tup(eghgt__dgcti, data)
        tmpLength = eghgt__dgcti
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        powa__ntzc = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = powa__ntzc


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    lcu__fykv = arr_tup.count
    oqd__xso = 'def f(arr_tup, lo, hi):\n'
    for i in range(lcu__fykv):
        oqd__xso += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        oqd__xso += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        oqd__xso += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    oqd__xso += '  return\n'
    ixrwy__zul = {}
    exec(oqd__xso, {}, ixrwy__zul)
    ntmdf__rydh = ixrwy__zul['f']
    return ntmdf__rydh


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    lcu__fykv = src_arr_tup.count
    assert lcu__fykv == dst_arr_tup.count
    oqd__xso = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(lcu__fykv):
        oqd__xso += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    oqd__xso += '  return\n'
    ixrwy__zul = {}
    exec(oqd__xso, {'copyRange': copyRange}, ixrwy__zul)
    rcpvo__tompk = ixrwy__zul['f']
    return rcpvo__tompk


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    lcu__fykv = src_arr_tup.count
    assert lcu__fykv == dst_arr_tup.count
    oqd__xso = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(lcu__fykv):
        oqd__xso += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    oqd__xso += '  return\n'
    ixrwy__zul = {}
    exec(oqd__xso, {'copyElement': copyElement}, ixrwy__zul)
    rcpvo__tompk = ixrwy__zul['f']
    return rcpvo__tompk


def getitem_arr_tup(arr_tup, ind):
    qut__mjjql = [arr[ind] for arr in arr_tup]
    return tuple(qut__mjjql)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    lcu__fykv = arr_tup.count
    oqd__xso = 'def f(arr_tup, ind):\n'
    oqd__xso += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(lcu__fykv)]), ',' if lcu__fykv == 1 else '')
    ixrwy__zul = {}
    exec(oqd__xso, {}, ixrwy__zul)
    mygln__keg = ixrwy__zul['f']
    return mygln__keg


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, gqqy__lzfu in zip(arr_tup, val_tup):
        arr[ind] = gqqy__lzfu


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    lcu__fykv = arr_tup.count
    oqd__xso = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(lcu__fykv):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            oqd__xso += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            oqd__xso += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    oqd__xso += '  return\n'
    ixrwy__zul = {}
    exec(oqd__xso, {}, ixrwy__zul)
    mygln__keg = ixrwy__zul['f']
    return mygln__keg


def test():
    import time
    dfosz__uznlg = time.time()
    oap__ygf = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((oap__ygf,), 0, 3, data)
    print('compile time', time.time() - dfosz__uznlg)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    pnk__kdfrl = np.random.ranf(n)
    sxnja__lllo = pd.DataFrame({'A': pnk__kdfrl, 'B': data[0], 'C': data[1]})
    dfosz__uznlg = time.time()
    hgje__qaeah = sxnja__lllo.sort_values('A', inplace=False)
    hvt__uhyu = time.time()
    sort((pnk__kdfrl,), 0, n, data)
    print('Bodo', time.time() - hvt__uhyu, 'Numpy', hvt__uhyu - dfosz__uznlg)
    np.testing.assert_almost_equal(data[0], hgje__qaeah.B.values)
    np.testing.assert_almost_equal(data[1], hgje__qaeah.C.values)


if __name__ == '__main__':
    test()
