def _get_nice_list(the_list, max_len=3):
    the_list = [str(item) for item in the_list] # just in case they are not strings
    if len(the_list) == 1:
        return the_list[0]
    elif len(the_list) <= max_len:
        return ", ".join(the_list[:-1])+" and "+the_list[-1]
    else:
        return ", ".join(the_list[:max_len-1])+", ... and "+the_list[-1]