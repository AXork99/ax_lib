from collections import defaultdict
from typing import Callable
from ..std.extras import Proxy

def listen(default = "__all__", *tags : str):
    def wrapper(f):
        for tag in tags + (default,):
            setattr(f, "_tag", tag)
        return f
    return wrapper

class Observer:
    def __init__(self, *observables : "Observable"):
        self.observables = {
            "__all__" : self.on_update,
            "__property__" : self.on_property
        }
        
        for method in dir(self):
            method = getattr(self, method)
            if isinstance(method, Callable) and hasattr(method, "_tag"):
                self.observables[getattr(method, "_tag")] = method
        
        for observable in observables:
            observable.register_observers(self)
        
    def _update(self, what, *args, **kwargs):
        return self.observables[what](*args, **kwargs)
    
    def on_update(self, what, *args, **kwargs):
        pass
    
    def on_property(self, which : "ObservableProperty", whose):
        pass
    
class Observable:
    def __init__(self, *observers : Observer):
        self.observers = defaultdict(list[Observer])
        self.register_observers(*observers)
    
    def register_observers(self, *observers : Observer):
        # print("adding:", observers)
        for observer in observers:
            for observable in observer.observables.keys():
                self.observers[observable].append(observer)
    
    def notify(self, what : list[str] | str = "__all__", *args, **kwargs):
        if not isinstance(what, list):
            what = [what]
        
        observers_list = ((o, key) for key in what for o in self.observers[key])
        for observer, what in observers_list:
            observer._update(what, self.vget() if what != "__property__" else self, *args, **kwargs)

def notify(observers : list[str] | str = "__all__"):
    def wrapp(f):
        def fun(self : Observable, *args, **kwargs):
            f(self, *args, **kwargs)
            self.notify(observers)
        return fun
    return wrapp

class ObservableProperty(Observable, Proxy):
    def __init__(self, name, val = None):
        super().__init__()
        self._val = val
        self.name = name
    def __str__(self):
        return str(self.name)

class observable:
    def __set_name__(self, _, name):
        self._name = name 
    
    def __get__(self, instance, _) -> ObservableProperty:
        _id = f"_val_{id(self)}"
        if not hasattr(instance, _id):
            setattr(instance, _id, ObservableProperty(self._name, self._default))
        return getattr(instance, _id)

    def __set__(self, instance, val):
        obs : ObservableProperty = getattr(instance, f"_val_{id(self)}")
        obs._val = val
        obs.notify(["__property__", obs.name], instance)
    
    def __init__(self, val = None):
        self._default = val

def get_observables(obj):
    def safe_get(obj, name):
        try:
            return getattr(obj, name)
        except:
            return None 
    return (attr for name in dir(obj) if isinstance(attr := safe_get(obj, name), ObservableProperty) and name != str(attr))           

if __name__ == "__main__":
    class A(Observable):
        x = observable(3)
        y = observable(2)

        @notify("poop")
        def poop(self):
            pass
    
    class BabyObserver(Observer):
        def on_update(self, who : ObservableProperty, whose):
            print(f"baby got _update from {who} in {whose}!", who.val)
    
    class PoopObserver(Observer):
        @listen("poop")
        def when_poop(self, who):
            print(f"{who} pooped!")
            
        def on_update(self, *args, **kwargs):
            print("Poop unrelated thing happen:", args, kwargs)
    
    class SexObserver(Observer):
        def on_update(self, *args, **kwargs):
            print("I had sex just now")
    
    obj = A()
    print(obj.x)
    obj.register_observers(PoopObserver())
    obj.x.register_observers(PoopObserver(), BabyObserver())
    obj.y.register_observers(SexObserver())
    obj.x = 12
    print(obj.x.val)
    obj.poop()
    obj.y = 69
    print(obj.y.val)