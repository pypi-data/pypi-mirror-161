import pickle as pkl


def export(in_path, out_path, include_dominant_pools=False, include_per_pool_cls=False):
    with open(in_path, 'rb') as file:
        pkl.load(file).export(out_path, include_dominant_pools=include_dominant_pools, include_per_pool_cls=include_per_pool_cls)
