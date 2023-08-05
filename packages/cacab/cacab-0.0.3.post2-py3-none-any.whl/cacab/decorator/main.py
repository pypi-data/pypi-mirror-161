import os
import pickle
import functools


def cache_at_location(file_location, save_per_arguments=False, rerun=False):
    # Ensure that the file_location ends in .pkl
    if len(file_location) <= 4 or file_location[-4:] != '.pkl':
        file_location = file_location + '.pkl'

    # Ensure that a cacheconfig file exists if cache is supposed to be saved per argument.
    config_location = file_location.split(".pkl")[0] + '_cacheconfig.pkl'
    arg_save_fmt = file_location.split(".pkl")[0] + '_{}.pkl'
    if save_per_arguments:
        configs = dict()
        if not os.path.exists(config_location):
            with open(config_location, 'wb') as bs:
                pickle.dump(configs, bs)  # Instantiate empty dict.
        else:
            with open(config_location, 'rb') as bs:
                configs = pickle.load(bs)

    def decorator(func):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            def get_file_loc(key=None) -> tuple[str, bool]:
                if not save_per_arguments:
                    return file_location, os.path.exists(file_location)
                else:
                    if key in configs:
                        return configs[key], True
                    else:
                        return "determined_later...", False

            config_key = str(args) + str(kwargs)
            file_loc, exists = get_file_loc(config_key)

            if exists and not rerun:
                with open(file_loc, 'rb') as o:
                    result = pickle.load(o)
            else:
                result = func(*args, **kwargs)

            if save_per_arguments:
                # Read configs again, to allow for this function to be used recursively
                # (Now if func writes to the configs file, it will be taken into account)
                with open(config_location, 'rb') as bs:
                    configs_instance = pickle.load(bs)
                file_loc = arg_save_fmt.format(str(len(configs_instance)).zfill(6))
                configs_instance[config_key] = file_loc
                with open(file_loc, 'wb') as o:
                    pickle.dump(result, o)
                with open(config_location, 'wb') as o:
                    pickle.dump(configs_instance, o)
            else:
                with open(file_loc, 'wb') as o:
                    pickle.dump(result, o)

            return result

        return wrapper_func

    return decorator
