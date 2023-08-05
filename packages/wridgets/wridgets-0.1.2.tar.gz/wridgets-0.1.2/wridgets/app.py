import functools
import traceback
from hashlib import md5

from . import wridgets as wr
from .utils import init_trait, init_store, unwrap, wrap


class App:
    trait_names = (
        'name',
        'output',
        'display_output',
        'propagate',
    )

    def set_trait_defaults(self):
        self.name = self.__class__.__name__
        self.output = wr.Output()
        self.display_output = True
        self.propagate = False

    _init_trait = classmethod(init_trait)

    _init_store = classmethod(init_store)

    def display(self):
        wr.display(
            self.app
        )
    
    def with_output(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.output:
                self.output.clear_output()
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    (self.clear_button + \
                    Button(
                        on_interact=self.print_traceback,
                        on_interact_kws=dict(tb=traceback.format_exc()),
                        button_style='info',
                        description='Traceback'
                    )).display()
                    print(e)
        return wrapper
    
    def print_traceback(self, tb):
        with self.output:
            self.output.clear_output()
            self.clear_button.display()
            print(tb)
    
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.app = wr.VBox()
        
        for trait in cls.trait_names:
            cls._init_trait(trait)

        # set stores
        if hasattr(cls, 'store_config'):
            for row in cls.store_config:
                row = wrap(row)
                cls._init_store(store=row[0])
        
        cls.make = cls._build(cls.make)

        return obj
    
    def __init_subclass__(cls):
        # automatically assign output to methods
        base_method_list = [func for func in dir(App) if callable(getattr(App, func))]
        method_list = [func for func in dir(cls) if callable(getattr(cls, func)) and func not in base_method_list]
        for method in method_list:
            setattr(cls, method, cls.with_output(getattr(cls, method)))
    
    def __init__(self, core=None, name=None, output=None, display_output=None, propagate=None, **kwargs):
        self._config = {}
        self._stores = {}
        self._core = None
        self.set_trait_defaults()
        if hasattr(self, 'store_config'):
            for row in self.store_config:
                row = wrap(row)
                if len(row)==2:
                    setattr(self, row[0], row[1])
                else:
                    setattr(self, row[0], None)
        if core is not None:
            self.core = core
        else:
            self._app_layout = []
            self.children = AppGroup()
        if name is not None:
            self.name = name
        if output is not None:
            self.output = output
        if display_output is not None:
            self.display_output = display_output
        if propagate is not None:
            self.propagate = propagate
        
        self.make(**kwargs)
    
    @property
    def core(self):
        return self._core

    @core.setter
    def core(self, core):
        self.app = core.app
        self._app_layout = core._app_layout
        self.children = core.children
        self._core = core

    def make(self, **kwargs):
        pass
    
    @property
    def app_layout(self):
        return self._app_layout
    
    @property
    def config(self):
        return self._config

    @property
    def stores(self):
        return self._stores

    def clear_output(self):
        self.output.clear_output()

    @property
    def clear_button(self):
        return Button(description='Clear', button_style='warning', on_interact=self.clear_output)

    def msg(self, msg:str, with_clear_button=True):
        clear_button = self.clear_button if with_clear_button else None
        with self.output:
            self.clear_output()
            if isinstance(msg, str):
                (Label(text=msg, fontsize=0.5) + 
                clear_button
                ).display()
            else:
                (msg + \
                clear_button).display()
    
    def _build(func):
        @functools.wraps(func)
        def wrapper(self, **kwargs):
            func(self, **kwargs)
            self.build()
        return wrapper
    
    def build(self):
        if self.display_output:
            self.app.children = [wr.HBox(row) for row in self.app_layout] + [self.output]
        else:
            self.app.children = [wr.HBox(row) for row in self.app_layout]
    
    @property
    def model_id(self):
        if not isinstance(self, AppWridget):
            ids = []
            for _, value in self.children:
                model_id = getattr(value, 'model_id', None)
                model_id = value.wridget.widget.model_id if model_id is None else model_id
                ids.append(model_id)
            encoded = ''.join(ids).encode()
            dhash = md5()
            dhash.update(encoded)
            return dhash.hexdigest()
        else:
            return self.wridget.widget.model_id

    def _union(self, other):
        if isinstance(other, App):
            obj = App()
            obj.children = self.children + other.children
            for source in [self, other]:
                if source.propagate:
                    setattr(obj.children, source.name, source)
            return obj
        else:
            raise TypeError(f'Cannot add type {type(self)} to type {type(other)}.')
    
    def _horizontal_app_layout(self, other):
        return [
            [
                self.app, other.app
            ]
        ]
    
    def _vertical_app_layout(self, other):
        return [
            [
                self.app
            ],
            [
                other.app
            ]
        ]
    
    def __radd__(self, other):
        if other is None:
            return self

    def __add__(self, other):
        if other is not None:
            obj = self._union(other)
            obj._app_layout = self._horizontal_app_layout(other)
            obj.build()
            return obj
        else:
            return self

    def __rsub__(self, other):
        if other is None:
            return self
    
    def __sub__(self, other):
        if other is not None:
            obj = self._union(other)
            obj._app_layout = self._vertical_app_layout(other)
            obj.build()
            return obj
        else:
            return self
    
    def __iter__(self):
        yield from self.children.__iter__()
    
    def wridgets(self, include=None, exclude=None):
        wridgets = {}
        for name, value in self.children:
            if isinstance(value, AppWridget):
                wridgets[name] = value
        
        subset = set(wridgets.keys())
        if include is not None:
            subset = set(wridgets.keys()).intersection(wrap(include))
        if exclude is not None:
            subset = set(wridgets.keys()).difference(wrap(exclude))
        return {k: v.wridget for k, v in wridgets.items() if k in subset}

    def get(self, name, include=None, exclude=None):
        if name in self.trait_names:
            return getattr(self, name)
        wridgets = self.wridgets(include=include, exclude=exclude)
        return {wridget_name: wridget.get(name) for wridget_name, wridget in wridgets.items()}

    def get1(self, name, include=None, exclude=None):
        if name in self.trait_names:
            return getattr(self, name)
        d = list(self.get(name=name, include=include, exclude=exclude).values())
        assert len(d) == 1, f'get1 must return one value'
        return unwrap(d)

    def set(self, include=None, exclude=None, **kwargs):
        for name, value in kwargs.items():
            if name in self.trait_names:
                setattr(self, name, value)
                self.build()
            else:
                wridgets = self.wridgets(include=include, exclude=exclude)
                for wridget in wridgets.values():
                    try:
                        wridget.set({name: value})
                    except:
                        pass

class AppGroup:
    def __init__(self, *args, **kwargs):
        for value in args:
            self.__setattr__(value.name, value)
            
        for name, value in kwargs.items():
            self.__setattr__(name, value)
            
    def __setattr__(self, name, value):
        cont = False
        new_model_id = getattr(value, 'model_id', None)
        if new_model_id is not None:
            original = getattr(self, name, None)
            if original is not None:
                original_model_id = getattr(original, 'model_id', None)
                if original_model_id is not None and original_model_id == new_model_id:
                    self.__dict__[name] = value
                else:
                    cont = True
            else:
                cont = True
        else:
            cont = True

        if cont:
            i = 1
            base = name
            while hasattr(self, name):
                i += 1
                name = base
                name += str(i)
            # if getattr(value, 'name', name) != name:
            #     value.set_config(name=name, update=True)
            self.__dict__[name] = value
    
    def __iter__(self):
        yield from self.__dict__.items()
        
    def __add__(self, other):
        if isinstance(other, AppGroup):
            obj = AppGroup()
            for source in [self, other]:
                for name, value in source:
                    setattr(obj, name, value)
            return obj
        else:
            raise TypeError(f'Cannot add type {type(self)} to type {type(other)}.')

    def __repr__(self):
        return str(tuple([a for a, _ in self if not a.startswith('_')]))
        

class AppWridget:
    def _set_wridget(self, wridget_type, **kwargs):
        if hasattr(self, 'allowed_wridget_types'):
            assert wridget_type in self.allowed_wridget_types, f'Allowed types are {self.allowed_wridget_types}'
        try:
            delattr(self.children, self.name)
        except:
            pass
        setattr(self.children, self.name, self)
        self.wridget = getattr(wr, wridget_type)(output=self.output, **kwargs)
        self._app_layout = [
                [
                    self.wridget.widget
                ]
        ]


class Label(App, AppWridget):
    allowed_wridget_types = 'HTML',
    def make(self, wridget_type='HTML', **kwargs):
        kwargs.setdefault('text', '')
        kwargs.setdefault('fontsize', 1)
        kwargs.setdefault('bold', False)
        kwargs['value'] = f"<font size='+{kwargs.get('fontsize')}'>{kwargs.get('text')}</font>"
        if kwargs.get('bold'):
            kwargs['value'] = "<b>" + kwargs['value'] + "</b>"
        self._set_wridget(wridget_type=wridget_type, **kwargs)


class Button(App, AppWridget):
    allowed_wridget_types = 'Button',
    def make(self, wridget_type='Button', **kwargs):
        kwargs.setdefault('value', None)
        kwargs.setdefault('layout', {'width': 'auto'})
        self._set_wridget(wridget_type=wridget_type, **kwargs)


class Field(App, AppWridget):
    allowed_wridget_types = ('Text', 'Textarea', 'IntText', 'FloatText', 'BoundedIntText', 'BoundedFloatText')
    def make(self, wridget_type='Text', **kwargs):
        kwargs.setdefault('continuous_update', False)
        kwargs.setdefault('layout', {'width': 'auto'})
        self._set_wridget(wridget_type=wridget_type, **kwargs)


class SelectButtons(App, AppWridget):
    allowed_wridget_types = 'ToggleButtons', 'RadioButtons'
    def make(self, wridget_type='ToggleButtons', **kwargs):
        kwargs.setdefault('options', ())
        kwargs.setdefault('layout', {'width': 'auto'})
        kwargs.setdefault('style', {'button_width': 'auto'})
        self._set_wridget(wridget_type=wridget_type, **kwargs)


class ToggleButton(App, AppWridget):
    allowed_wridget_types = 'ToggleButton',
    def make(self, wridget_type='ToggleButton', **kwargs):
        kwargs.setdefault('widget_type', 'ToggleButton')
        kwargs.setdefault('layout', {'width': 'auto'})
        self._set_wridget(wridget_type=wridget_type, **kwargs)


class Dropdown(App, AppWridget):
    allowed_wridget_types = 'Dropdown',
    def make(self, wridget_type='Dropdown', **kwargs):
        kwargs.setdefault('layout',  {'width': 'auto'})
        self._set_wridget(wridget_type=wridget_type, **kwargs)


class Link(App, AppWridget):
    allowed_wridget_types = 'HTML'
    def make(self, wridget_type='HTML', link_kws=None, **kwargs):
        link_kws = {} if link_kws is None else link_kws
        link_kws.setdefault('src', '')
        link_kws.setdefault('text', link_kws.get('src'))
        link_kws.setdefault('fontsize', 1)
        link_kws.setdefault('link_color', 'blue')
        link_kws.setdefault('link_background_color', 'transparent')
        link_kws.setdefault('link_text_decoration', 'underline')
        link_kws.setdefault('visited_color', 'purple')
        link_kws.setdefault('visited_background_color', 'transparent')
        link_kws.setdefault('visited_text_decoration', 'underline')
        kwargs['value'] = f"""
            <style>
            a:link {{
            color: {link_kws.get('link_color')};
            background-color: {link_kws.get('link_background_color')};
            text-decoration: {link_kws.get('link_text_decoration')};
            }}

            a:visited {{
            color: {link_kws.get('visited_color')};
            background-color: {link_kws.get('visited_background_color')};
            text-decoration: {link_kws.get('visited_text_decoration')};
            }}
            </style>
            <font size='+{link_kws.get('fontsize')}'>
            <a href={link_kws.get('src')} target='_blank'>{link_kws.get('text')}</a>
            </font>
            """
        self._set_wridget(wridget_type=wridget_type, **kwargs)


class Valid(App, AppWridget):
    allowed_wridget_types = 'Valid'
    def make(self, wridget_type='Valid', **kwargs):
        self._set_wridget(wridget_type=wridget_type, **kwargs)