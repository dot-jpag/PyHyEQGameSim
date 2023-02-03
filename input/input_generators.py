""" Generators for input sequences to use with simulations! They almost always yield
    InputSignals of various kinds.
"""
from typing import Generator, List,  Optional
from .input_signal import InputSignal

def btn_1_ordered_sequence_generator(max_t, step_time, direction:str="asc") -> Generator[InputSignal, Optional[List], None]:
    """A generator that yields elements from all one button sequences in an order
       ascending (asc) goes from never pressed (all 0s) to always pressed (all 1s)
       descending (dsc) goes from always pressed (all 1s) to never pressed (all 0s)
    """
    # assume an equal distance, sample n+1 happens at t+step_time
    sample_times = []
    running_timer = 0.0
    while running_timer < max_t:
        sample_times.append(running_timer)
        running_timer += step_time

    # rad, ok, we have times
    n_samples = len(sample_times)
    print(f"Number of input samples: {n_samples}")
    print(f"Number of unique sequences over input {2**n_samples}")
    if direction == "asc":
        i = 0
        while i < 2**n_samples:
            bin_list = int_to_bin_list(i, n_samples)
            keep_digits = (yield InputSignal(bin_list, sample_times))
            # kinda wonky (FIXME): what we get back is the digits to keep.
            # flip the last 0 to a 1, fill the remainder out with 0s
            # convert that back to decimal and set i to it
            # ex 000 --> 00100
            # ex 001 --> 01100
            # ex 0010 --> 00110
            if keep_digits:
                # convert as far as the sim got to a number
                sim_progress = int(f"0b{''.join([str(digit) for digit in keep_digits])}", 2)
                # add one to it
                next_sim_num = sim_progress + 1
                # back to a binary string, left justify with 1s
                # n_samples +2 to keep the 0b header so we can go back to an int
                next_sim_str = f"{next_sim_num:0{len(keep_digits) - 1}b}".ljust(n_samples + 2, '0')
                i = int(next_sim_str, 2)
            else:
                # we didn't get back anything to skip, so we should just move to the next input
                i += 1
        # NOTE: we need to return the min value here, the loop will never actually get to it
        
        # NOTE: we need to return the max value here, the loop will never actually get to it
    elif direction == "dsc":
        i = 2**n_samples - 1
        while i > 0: # maybe never tests all 0's?
            bin_list = int_to_bin_list(i, n_samples)
            keep_digits = (yield InputSignal(bin_list, sample_times))
            # kinda wonky (FIXME): what we get back is the digits to keep.
            # flip the last 1 to a 0, fill the remainder out with 1s
            # convert that back to decimal and set i to it
            # ex 111 --> 11011
            # ex 110 --> 10011
            # ex 1101 --> 11001
            if keep_digits:
                # convert as far as the sim got to a number
                sim_progress = int(f"0b{''.join([str(digit) for digit in keep_digits])}", 2)
                # subtract one from it
                next_sim_num = sim_progress - 1
                # back to a binary string, left justify with 1s
                # nsamples +2 to keep the 0b header so we can go back to an int
                next_sim_str = f"{next_sim_num:0{len(keep_digits) - 1}b}".ljust(n_samples + 2, '1')
                i = int(next_sim_str, 2)
            else:
                # we didn't get back anything to skip, so we should just move to the next input
                i -= 1
        # NOTE: we need to return the min value here, the loop will never actually get to it
    return None

def time_sequence(input_samples, step_time) -> InputSignal:
    """ if we already have a sequence and a step time, allocate samples to times, return a signal
    """
    return InputSignal(input_samples, [step_time * i for i in range(len(input_samples))])

def int_to_bin_list(num, width) -> List[int]:
    """Convert a number to a binary list representation of that number
       num=4, width=4 -> 0, 1, 0, 0
       num=4, width=2 -> 1, 0, 0
       num=4, width=5 -> 0, 0, 1, 0, 0
       num=3, width=4 -> 0, 0, 1, 1
       etc.
    """
    binary_string = bin(num)[2:] #cut out the leading 0
    padded_bin_string = str(binary_string).zfill(width)
    return [int(digit) for digit in padded_bin_string]

def jump_to(keep_digits, flip_digit, fill_digit, size) -> int:
    """ Given keep digits, find the right most relevant flip digit,
        flip it, then right fill with fill digit is until we get size digits
        convert back to an int
    """
    # find the flip idx given the flip digit
    flip_idx = len(keep_digits) - keep_digits[-1::-1].index(flip_digit) - 1 # FIXME: this makes a copy, but eeeeeh. Other options are worse.
    # flip it
    keep_digits[flip_idx] = (-flip_digit) + 1
    # concatinate down as str
    keep_digits_as_str = "".join([str(d) for d in keep_digits])
    # fill with the fill digit
    skip_until = f"0b{keep_digits_as_str.ljust(size, str(fill_digit))}"
    # convert back to int
    return int(skip_until, 2)