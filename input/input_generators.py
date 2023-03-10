"""Generators for input sequences to use with simulations!
   They almost always yield InputSignals of various kinds.
"""
from typing import Generator, List, Optional
from .input_signal import InputSignal


def btn_1_ordered_sequence_generator(
    max_t: float, step_time: float, direction: str = "asc"
) -> Generator[InputSignal, Optional[List], None]:
    """A generator that yields elements from all one button press sequences in
    an order.
    Args:
        max_t (float): the maximum time to generate out to
        step_time (float): time between each sample
        direction (str): order of the input
            asc -> all 0s to all 1s
            dsc -> all 1s to all 0s
    Returns:
        Generator[InputSignal, Optional[List], None]: returns a generator
        that yields a new input signal. We move on to the next signal by
        sending back how far the previous input got us, so the generator knows
        how far to jump and ignore parts of the input signal that aren't relevant yet
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
            keep_digits = yield InputSignal(bin_list, sample_times)
            if keep_digits:
                # convert as far as the sim got to a number
                sim_progress = int(
                    f"0b{''.join([str(digit) for digit in keep_digits])}", 2
                )
                # add one to it
                next_sim_num = sim_progress + 1
                # back to a binary string
                # n_samples + 2 to keep the 0b header so we can
                # go back to an int
                next_sim_str = \
                    f"{next_sim_num:0{len(keep_digits) - 1}b}".ljust(
                        n_samples + 2, "0"
                    )
                i = int(next_sim_str, 2)
            else:
                # we didn't get back anything to skip, so we should just move
                # to the next input
                i += 1
    elif direction == "dsc":
        i = 2**n_samples - 1
        while i > 0:  # maybe never tests all 0's?
            bin_list = int_to_bin_list(i, n_samples)
            keep_digits = yield InputSignal(bin_list, sample_times)
            if keep_digits:
                # convert as far as the sim got to a number
                sim_progress = int(
                    f"0b{''.join([str(digit) for digit in keep_digits])}", 2
                )
                # subtract one from it
                next_sim_num = sim_progress - 1
                # back to a binary string
                # n_samples + 2 to keep the 0b header so we can
                # go back to an int
                next_sim_str = \
                    f"{next_sim_num:0{len(keep_digits) - 1}b}".ljust(
                        n_samples + 2, "1"
                    )
                i = int(next_sim_str, 2)
            else:
                # we didn't get back anything to skip, so we should just move
                # to the next input
                i -= 1
        # NOTE: we need to return the min value here, the loop will never
        # actually get to it
    return None


def time_sequence(input_samples, step_time) -> InputSignal:
    """if we already have a sequence and a step time, allocate samples to
    times, return a signal
    """
    return InputSignal(
        input_samples, [step_time * i for i in range(len(input_samples))]
    )


def int_to_bin_list(num, width) -> List[int]:
    """Convert a number to a binary list representation of that number
       num=4, width=4 -> 0, 1, 0, 0
       num=4, width=2 -> 1, 0, 0
       num=4, width=5 -> 0, 0, 1, 0, 0
       num=3, width=4 -> 0, 0, 1, 1
       etc.
    Args:
        num (int): integer number to convert
        width (int): size of the eventual list
    Returns:
        List[int]: a list as described above
    """
    binary_string = bin(num)[2:]  # cut out the leading 0
    padded_bin_string = str(binary_string).zfill(width)
    return [int(digit) for digit in padded_bin_string]