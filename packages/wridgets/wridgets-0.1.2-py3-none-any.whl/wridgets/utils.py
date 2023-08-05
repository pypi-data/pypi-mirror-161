import numpy as np
from ipywidgets import VBox, HBox 


def wrap(item):
    if not isinstance(item, list) and not isinstance(item, tuple):
        item = [item]
    return item


def unwrap(item):
    if isinstance(item, list) or isinstance(item, tuple):
        if len(item) == 1:
            return item[0]
    return item


def GridBox2(items:list, dims:tuple=(3, -1)):
    """
    Displays multiple widgets in rows and columns.
    
    :param items: (list) widgets to display
    :param dims: (tuple) n_rows, n_cols
    
    :returns: VBox with widgets
    """
    n_items = len(items)
    n_rows, n_cols = dims
    assert (n_rows > 0) or (n_cols > 0), 'At least one dim must be > 0'
    assert (n_rows != 0) and (n_cols != 0), 'dims cant contain 0'
    n_rows = int(np.ceil(n_items / n_cols)) if n_rows < 0 else n_rows
    n_cols = int(np.ceil(n_items / n_rows)) if n_cols < 0 else n_cols
    assert n_rows * n_cols >= n_items, f"Specified dims: {n_rows, n_cols} won't fit all {n_items} items"

    HBoxs = []
    for r in range(n_rows):
        HBoxs.append(
            HBox(
                *[items[slice(n_cols*r, n_cols*(r+1))]]
            )
        )
    return VBox([*HBoxs])


def init_trait(cls, trait):
    def getter_lda(self): return self._config.get(trait)
    setattr(cls, trait, property(getter_lda))
    def setter_lda(self, value): return self._config.update({trait: value})
    setattr(cls, trait, getattr(cls, trait).setter(setter_lda))


def init_store(cls, store):
    def getter_lda(self): return self._stores.get(store)
    setattr(cls, store, property(getter_lda))
    def setter_lda(self, value): return self._stores.update({store: value})
    setattr(cls, store, getattr(cls, store).setter(setter_lda))