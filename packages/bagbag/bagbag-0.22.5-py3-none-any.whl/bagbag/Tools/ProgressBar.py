import tqdm

def ProgressBar(iterable_obj, startfrom=0, total=None, title=None, leave=False):
    """
    It creates a progress bar for iterable objects.
    
    :param iterable_obj: The iterable object you want to iterate over
    :param startfrom: The position of the progress bar, defaults to 0 (optional)
    :param total: The number of expected iterations. If unspecified, len(iterable) is used if possible
    :param title: Title of the progress bar
    :param leave: If True, tqdm will leave the progress bar on the screen after completion, defaults to
    False (optional)
    :return: A progress bar object.
    """
    return tqdm.tqdm(iterable_obj, dynamic_ncols=True, total=total, leave=leave, position=startfrom, desc=title)

if __name__ == "__main__":
    import time
    for i in ProgressBar(range(10), title="test sleep"):
        print(i)
        time.sleep(1)