# clean_params.py
import boakboak.src.settings as sts


def cleaner(params, *args, **kwargs):
    for k, vs in params.copy().items():
        cleaned = {}
        for parName, pars in vs.items():
            if type(pars) == str:
                if (("\\" in pars) or ("/" in pars)) and not parName == "executable":
                    pars = sts.prep_path(pars)
                    if pars == False:
                        print(f"clean_params.cleaner: {parName}: {pars}")
                        exit()
            cleaned[parName] = pars
        params[k] = cleaned
    return params
