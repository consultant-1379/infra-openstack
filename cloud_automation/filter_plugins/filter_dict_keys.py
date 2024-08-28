
def remove_keys(dict_to_filter, keys_to_remove):
    """
    Remove keys from a dictionary.

    Args:
      dict_to_filter:
        The dictionary from which the keys will be removed.
      keys_to_remove:
        A list of keys to remove.

    Returns:
      A dictionary containing the same items as dict_to_filter but with the 
      items specified in keys_to_remove removed
    """
    return {k: v for k, v in dict_to_filter.items() if k not in keys_to_remove}


def remove_all_keys_except(dict_to_filter, keys_to_keep):
    """
    Remove all keys from a dictionary except those specified.

    Args:
      dict_to_filter:
        The dictionary from which the keys will be removed.
      keys_to_keep:
        A list of keys to keep.

    Returns:
      A dictionary containing the same items as dict_to_filter but with only
      the items specified in keys_to_keep retained.
    """
    return {k: v for k, v in dict_to_filter.items() if k in keys_to_keep}

class FilterModule(object):
    dict_filters = {
        'remove_keys': remove_keys,
        'remove_all_keys_except': remove_all_keys_except
    }

    def filters(self):
        return self.dict_filters
