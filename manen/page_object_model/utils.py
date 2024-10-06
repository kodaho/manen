from typing import get_args


def resolve_args(annotation, meta=None):
    args = get_args(annotation)
    if len(args) == 0:
        return (annotation, *(meta or tuple()))
    return resolve_args(args[0], args[1:] + (meta or tuple()))
