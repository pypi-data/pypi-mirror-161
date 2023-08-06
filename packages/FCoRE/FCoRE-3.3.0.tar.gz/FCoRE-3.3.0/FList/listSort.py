

SORT_BY_DICT_KEY = lambda listObj, dictKey: sorted(listObj, key=lambda k: k.get(f"{dictKey}"), reverse=True)


