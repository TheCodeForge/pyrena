import time
import webbrowser

def lazy(f):

    def wrapper(self):

        if f.__name__ in self._cache:
            return self._cache[f.__name__]
        else:

            return_value = f(self)
            self._cache[f.__name__]=return_value
            return return_value

    wrapper.__name__=f.__name__
    return wrapper



OBJ_CACHE={}

class Object():

    def __new__(cls, guid=None, **kwargs):

        cache_key = f"{cls.__name__};{guid}"

        if not kwargs:
            obj=OBJ_CACHE.get(cache_key)
            if obj:
                return obj

        obj = super(Object, cls).__new__(cls)

        return obj

    def __init__(self, guid=None, **kwargs):

        """
        Use one of the following:

        guid - object ID to fetch from Arena

        or

        **kwargs - Dictionary of properties to set on a blank object instance that does not yet exist in Arena. Call `create()` once all desired properties are set.
        """

        #skip if cached
        cache_key = f"{self.__class__.__name__};{guid}"

        if guid and not kwargs:
            if cache_key in OBJ_CACHE:
                return

            self.endpoint=getattr(self.__class__, 'endpoint')
            if not self.endpoint:
                raise ValueError(f"{self.__class__.__name__} objects cannot be directly obtained by GUID.")

            if not isinstance(self.endpoint, property):
                self.endpoint=self.endpoint.format(guid=guid)
            
            data = self._client._get(self.endpoint)

            self.__dict__.update(data)

        elif kwargs:
            self.guid=guid
            self.__dict__.update(kwargs)
            if not isinstance(self.__class__.__dict__.get('endpoint'), property):
                if "endpoint" in dir(self.__class__):
                    self.endpoint=getattr(self.__class__, 'endpoint').format(guid=self.guid)

        else:
            raise AttributeError("Must specify either `guid` or `**kwargs`")

        self._cache={}

        OBJ_CACHE[cache_key]=self

    def __repr__(self):

        if self._client._debug:

            return f"<{self.__class__.__name__}(id={self.guid})>"

        else:
            if "number" in self.__dict__:
                return f"<{self.__class__.__name__}(number={self.number})>"
            elif "name" in self.__dict__:
                return f"<{self.__class__.__name__}(name={self.name})>"
            else:
                return f"<{self.__class__.__name__}(id={self.guid})>"

    def __str__(self):
        if "name" in self.__dict__:
            return f"<{self.__class__.__name__}(name={self.name})>"
        else:
            return self.__repr__

    def __eq__(self, other):
        return self.__repr__==other.__repr__

    def __getattr__(self, name):

        # "2018-06-01T06:59:59Z"
        if name.endswith("_utc"):
            target_name=f"{name.split('_utc')[0]}DateTime"
            if target_name in self.__dict__:
                target_time=self.__dict__[target_name]
                return int(time.mktime(time.strptime(self.__dict__[target_name], "%Y-%m-%dT%H:%M:%SZ")))
            else:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        elif name in self.__dict__:
            return self.__dict__[name]
        elif name in dir(self):
            return getattr(self.__class__, name).fget(self)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def refresh(self, value=None):
        """
        Dumps cache for lazily loaded object properties. Dumped properties will be reloaded from Arena at next access.

        Optional arguments:

        value - A specific property to dump. If None, all of the object's lazy-loaded properties will be dumped.
        """

        if value:
            val = self._cache.pop(value, None)
            if val and isinstance(val, Object):
                self._client.clear_cache(val)
        else:
            for entry in self._cache:
                val = self._cache[entry]
                if val and isinstance(val, Object):
                    self._client.clear_cache(val)
            self._cache={}

    def create(self):
        """
        Creates a new object in Arena based on object attributes. Not available for objects retrieved from Arena.
        """

        if self.__dict__.get("guid"):
            raise ValueError(f"This {self.__class__.__name__} has already been created")

        strip_endpoints = [
            "endpoint",
            "guid",
            "listing_endpoint",
        ]
        data = {x: self.__dict__[x] for x in self.__dict__ if (x not in strip_endpoints and not x.startswith('_'))}

        response= self._client._post(self.__class__.listing_endpoint, data=data)

        self.__dict__.update(response)

        if "endpoint" in dir(self.__class__):
            self.endpoint=getattr(self.__class__, 'endpoint').format(guid=self.guid)

    def update(self, **data):
        """
        Updates the object properties in Arena based on attributes passed in.

        Required arguments:

        - **data - Object properties to update. Use attribute GUIDs to update custom attributes.
        """

        response = self._client._put(self.endpoint, data)

        self.__dict__.update(response)

    def delete(self):
        """
        Deletes the object in Arena.
        """
        self._client._delete(self.endpoint)

    def reload(self):
        """
        Hard reloads the object from Arena. Useful when object is first obtained via a Listing search, which does not include all desired information.
        """

        data = self._client._get(self.endpoint)
        self.__dict__.update(data)

    @property
    def cache_key(self):
        return f"{self.__class__.__name__};{self.guid}"

    @property
    @lazy
    def user(self):
        return self._client.User(self.creator['guid'])
    
class openable_mixin():


    def open(self):
        """
        Open the object in the browser. Requires also being logged into Arena in the default web browser.
        """

        webbrowser.open(f"{self._client.browser_url}{self.guid}")