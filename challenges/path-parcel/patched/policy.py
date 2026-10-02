def locate(public, name):
    path = (public / name).resolve()
    if not path.is_relative_to(public.resolve()):
        raise PermissionError('outside public')
    return path
