class VRoute():
    def __init__(self, request, *args):
        self.data = {}
        self.matched = False
        if len(request.pathlist) != len(args):
            return

        for i, elm in enumerate(request.pathlist):
            try:
                exp = args[i]
            except IndexError:
                break

            if exp.startswith("$"):
                kl = exp.lstrip("$").split(":")
                if len(kl) == 2:
                    func = {
                        "int": int,
                        "str": str,
                        "float": float,
                        "bool": bool
                    }.get(kl[1], str)
                else:
                    func = str
                try:
                    self.data[kl[0]] = func(elm)
                except ValueError:
                    break
                continue

            if exp != elm:
                break
        else:
            self.matched = True
            return

    def __bool__(self):
        return self.matched

    def __getitem__(self, key):
        return self.data.get(key, None)
