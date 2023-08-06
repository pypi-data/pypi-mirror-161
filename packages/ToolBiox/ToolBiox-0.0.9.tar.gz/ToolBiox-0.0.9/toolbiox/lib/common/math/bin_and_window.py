from math import ceil
import re


# windows

def cover_windows_index(pos, step, window, start=1):
    """
    For a known windows set for a sequence (given step length, windows length, and start site).
    Now when I am on a position(pos), which windows covered me ?=
    :param pos: Pos site I am
    :param step: step for windows
    :param window: window length for windows
    :param start: where is start for first window
    :return: windows index (begin for 0) for windows which covered me
    """
    if pos < start:
        raise ValueError("Pos: %d is small than start %d" % (pos, start))
    else:
        pos = pos - start + 1
        for i in range(ceil((pos - window) / step), int((pos - 1) / step) + 1):
            if i >= 0:
                yield i


def windows_index_to_range(index, step, window, start=1):
    """
    For a known windows set for a sequence (given step length, windows length, and start site).
    Now I give a index (begin for 0), give me the detail for this window
    :param pos: index I have
    :param step: step for windows
    :param window: window length for windows
    :param start: where is start for first window
    :return: windows start and end
    """
    start = index * step + start
    end = start + window - 1
    return start, end


def total_windows(end, step, window, start=1):
    """
    return how many windows can be get for a given sequence and given windows parameter
    :param end: sequence length or end for window split
    :param step: step for windows
    :param window: windows length
    :param start: where is the start for the first window, default: 1
    :return: windows number
    """

    # seq_len = end - start + 1
    seq_len = end - start
    win_num = ceil((seq_len - window + 1) / step) + 1
    return win_num


def split_sequence_to_windows(end, step, window, start=1):
    """
    make a windows split for a sequence
    :param end: sequence length or end for window split
    :param step: step for windows
    :param window: windows length
    :param start: where is the start for the first window, default 1
    :return: generator for windows index, start and end
    """

    for i in range(0, total_windows(end, step, window, start)):
        start_tmp, end_tmp = windows_index_to_range(i, step, window, start)
        start_tmp, end_tmp = round(start_tmp), round(end_tmp)
        if start_tmp == end:
            yield i, start_tmp, end
            continue
        elif start_tmp > end:
            continue
        #     raise ValueError("start_tmp %d > end %d, it should not happen" % (start_tmp, end))
        elif end_tmp > end:
            yield i, start_tmp, end
        else:
            yield i, start_tmp, end_tmp


# bin (means windows without overlap)

def cover_bin_index(pos, bin_length, start=1):
    """
    For a known bins set for a sequence (given bin length and start site).
    Now when I am on a position(pos), which bin covered me ?
    :param pos: Pos site I am
    :param bin_length: length for a bin
    :param start: where is the start for the first bin
    :return: bin index (begin for 0) for windows which covered me
    """
    return list(cover_windows_index(pos, bin_length, bin_length, start))[0]


def bin_index_to_range(index, bin_length, start=1):
    """
    For a known bins set for a sequence (given bin_length, and start site).
    Now I give a index (begin for 0), give me the detail for this bin
    :param index: index I have
    :param bin_length: length of each bin
    :param start: where is start for first bin
    :return: bin start and end
    """
    return windows_index_to_range(index, bin_length, bin_length, start)


def total_bins(end, bin_length, start=1):
    """
    return how many bin can be get for a given bin_length
    :param end: sequence length or end for bin split
    :param bin_length: length of each bin
    :param start: where is the start for the first bin, default: 1
    :return: bins number
    """
    return total_windows(end, bin_length, bin_length, start)


def split_sequence_to_bins(end, bin_length, start=1):
    """
    make a windows split for a sequence
    :param end: sequence length or end for window split
    :param step: step for windows
    :param window: windows length
    :param start: where is the start for the first window, default 1
    :return: generator for windows index, start and end
    """
    return split_sequence_to_windows(end, bin_length, bin_length, start)
