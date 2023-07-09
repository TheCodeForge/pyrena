import requests
import sys
import time
import mistletoe
from collections import deque
import webbrowser
import inspect
import warnings
import urllib3
import ssl
from pprint import pprint
import os
import json

import pyrena.classes as classes

class ArenaHTTPError(Exception):
    pass

class Arena():

    def __init__(self, username=None, password=None, env=None, ssl_verify=True, user_agent="Python Pyrena", verbose=False, arenagov=False):

        """
        Creates the Arena client

        Optional arguments:
        - arenagov      - Set to True for accessing workspaces located on app.arenagov.com. Defaults to False for workspaces located on app.bom.com.
        - ssl_verify    - Use strict SSL verification in requests. May need to be set to False when accessing Arena from a corporate-controlled network.
        - user_agent    - Set a User-Agent header.
        - verbose       - Verbosely output API requests to console
        """

        #set properties
        self.base_url = "https://api.arenagov.com/v1/v1" if arenagov else "https://api.arenasolutions.com/v1"
        self.browser_url = "https://app.arenagov.com/" if arenagov else "https://app.bom.com/"
        self.ssl_verify = ssl_verify


        #if ssl_verify is false, disable insecure http warnings
        if not ssl_verify:
            warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

        self.user_agent = user_agent

        self._debug=verbose
 
        self.__dict__['_username']=username
        self.__dict__['_password']=password
        self.__dict__['_env']=env

        self.headers={
            "User-Agent": self.user_agent,
            "Content-Type": "application/json"
        }

        self._reqs_remaining=123456789 #arbitrary high - depends on your deal with Arena

        #login
        try:
            self.login()
        except ArenaHTTPError:
            print("Unable to log in. Call `login(username, password + optional env)` on this client to authenticate with Arena.")
        except ssl.SSLCertVerificationError:
            print("Unable to establish a secure connection to Arena. Use a different internet connection or use `ssl_verify=False` to allow insecure requests.")

        #initialize cache
        self._cache={}

    def __getattr__(self, name):

        if name in ['username', '_username', 'password', '_password']:
            raise AttributeError

        obj = getattr(classes, name, None)

        if not obj and name in self.__dict__:
            return self.__dict__[name]
        elif not obj:
            raise AttributeError

        if obj and not isinstance(obj, type):
            raise AttributeError
        elif not obj:
            raise AttributeError

        obj._client=self

        return obj

    def __repr__(self):
        if self.__dict__['_env']:
            return f"<Arena(user={self.__dict__['_username']}) in env={self.__dict__['_env']}>"
        else:
            return f"<Arena(user={self.__dict__['_username']}) in default env>"

    def login(self, username=None, password=None, env=None):

        """
        Log into Arena

        Optional arguments:
        - username    - Username. Defaults to username given at client creation if not specified.
        - password    - Password. Defaults to password given at client creation if not specified.
        """

        self.__dict__["_username"] = username or self.__dict__["_username"]
        self.__dict__["_password"] = password or self.__dict__["_password"]
        self.__dict__["_env"] = env or self.__dict__["_env"]

        if env: #e.g to switch between several workspaces or sandboxes
            login_data = self._post(
                "/login",
                data={
                    "email":self.__dict__["_username"],
                    "password":self.__dict__["_password"],
                    "workspaceId":self.__dict__["_env"]
                    }
                )
        else: # if no env specified, logs into to default env
            login_data = self._post(
                "/login",
                data={
                    "email":self.__dict__["_username"],
                    "password":self.__dict__["_password"],
                    }
                )

        #set auth token
        self.headers["arena_session_id"]=login_data["arenaSessionId"]
        #set time to re-auth, 1 min before expiry
        self.reauth_utc = int(time.time())+60*80 # to customize

    def logout(self):

        """
        Log out of Arena.
        """
        self._put("/logout", expect_json = False)
        self.__dict__["_username"]=None
        self.__dict__["_password"]=None
        self.__dict__["me"]=None
        self.__dict__["env"]=None
        self.headers["arena_session_id"]=None
        self.reauth_utc=0

    def _fetch(self, method, endpoint, params={}, data={}, files={}, headers={}, expect_json=True, **kwargs):

        if not self._reqs_remaining:
            raise ArenaHTTPError("Request limit reached.") 

        #reauth 1 min before expiry
        if endpoint != "/login" and int(time.time())> self.reauth_utc:
            self.login()

        url = f"{self.base_url}{'' if endpoint.startswith('/') else '/'}{endpoint}"

        req_headers=self.headers
        for header in headers:
            req_headers[header]=headers[header]

        try:
            resp = getattr(requests, method.lower())(
                url, 
                headers=req_headers, 
                params=params,
                json=data, 
                files=files,
                verify=self.ssl_verify,
                )
        except requests.exceptions.SSLError:
            raise requests.exceptions.SSLError("Unable to establish a secure connection to Arena. Use a different internet connection or use `ssl_verify=False` to allow insecure requests.")

        if self._debug:
            print("===PAYLOAD===")
            print(f"{method.upper()} {endpoint}")
            pprint(data)
            print("===RESPONSE===")
            print(f"status {resp.status_code}")
            pprint(resp.json())

        if resp.status_code >=400:
            data=resp.json()
            raise ArenaHTTPError(f"HTTP Error {resp.status_code} - {data['errors'][0]['message']} (Arena Error Code {data['errors'][0]['code']})")

        resp.raise_for_status()


        #update reqs remaining
        # getting the header that mentions how many calls remain
        #exact name of the HTTP header hidden for more privacy:
        for k in resp.headers:
            #debug print
            #print("test my iterate thru headers loop: ", k)
            if 'Remain' in k:
                self._reqs_remaining = int(resp.headers.get(k, self._reqs_remaining))

        # print reqs remaining at login/logout:
        if endpoint == "/login" or endpoint == "/logout":
            print(f"Number of remaining requests: {self._reqs_remaining}")
        if self._reqs_remaining < 1000 and self._debug:
            print(f"Caution: {self._reqs_remaining} requests remaining")

        if method.lower()=="delete":
            return
        elif expect_json==False:
            return resp.content
        else:
            return resp.json()

    def _get(self, endpoint, params={}, **kwargs):
        return self._fetch("get", endpoint, params=params, **kwargs)

    #@disable
    def _post(self, endpoint, data={}, files={}, **kwargs):
        return self._fetch("post", endpoint, data=data, files=files, **kwargs)

    #@disable
    def _put(self, endpoint, data={}, **kwargs):
        return self._fetch("put", endpoint, data=data, **kwargs)

    #@disable
    def _delete(self, endpoint, data={}, **kwargs):
        self._fetch("delete", endpoint, data=data, **kwargs)

    def Listing(self, obj, endpoint=None, limit=400, offset=0, **kwargs):

        '''
        Obtains a listing of objects using Arena's search feature.

        Required arguments:
        - obj       - Object class to aquire. For example, client.QualityProcess

        Optional arguments:
        - endpoint  - The endpoint to use. Defaults to obj.listing_endpoint property
        - limit     - The maximum number to fetch. Defaults to 400, the maximum number of objects that may be returned by one Arena API call.
        - offset    - Offset for result returns. Defaults to 0 (no offset). Mainly used in recursive pagination calls.
        - **kwargs  - Property arguments for search parameters.

        Returns: List of objects
        '''

        if isinstance(obj, str):
            obj=getattr(classes, obj)

        endpoint = endpoint or obj.__dict__.get("listing_endpoint")
        if not endpoint:
            raise AttributeError(f"Object type `{obj.__name__}` cannot be globally listed")

        #assemble search params if needed
        params={}
        for entry in kwargs:
            if isinstance(kwargs[entry], classes.Object):
                params[f"{entry}.guid"] = kwargs[entry].guid
            elif isinstance(entry, str):
                params[entry]=kwargs[entry]
            else:
                params[entry.guid]=kwargs[entry]

        if getattr(obj, "_can_paginate", True):

            params["limit"]=min(limit, 400) if limit else 400
            params["offset"]=offset

        #process percent/plus needed in object numbers
        if "number" in params:
            params["number"]=params["number"].replace('%', '%25')
            params["number"]=params["number"].replace('+', '%2b')

        data=self._get(endpoint, params=params)

        listing=[obj(**dictionary) for dictionary in data["results"]]

        if not listing:
            return []

        for item in listing:
            item._client=self


        if not limit or len(listing)==limit:
            listing+=self.Listing(
                    obj, 
                    endpoint, 
                    limit=400 if limit else None,
                    offset=offset+400,
                    **kwargs
                    )
        
        return listing



    def Stream(self, obj, endpoint=None, limit=400, offset=0, delay=60, **kwargs):

        """
        Similar to Listing, but works as a generator that yields live results without end. Does not yield pre-existing content.

        Required arguments:
        - obj       - Object class to aquire. For example, client.QualityProcess

        Optional arguments:
        - endpoint  - The endpoint to use. Defaults to obj.listing_endpoint property
        - limit     - The maximum number to fetch. Defaults to 400, the maximum number of objects that may be returned by one Arena API call.
        - offset    - Offset for result returns. Defaults to 0 (no offset). Mainly used in recursive pagination calls.
        - delay     - Time to sleep (in seconds) between API calls.

        Yields objects
        """

        initial = self.Listing(obj, endpoint, limit, offset, **kwargs)

        already_seen=deque([], 1000)
        for item in initial:
            already_seen.append(item.__repr__())

        while True:

            time.sleep(delay)

            for entry in self.Listing(*args, **kwargs):

                if entry.__repr__ in already_seen:
                    continue

                already_seen.append(entry.__repr__())
                yield entry

    def find(self, obj_type, **kwargs):

        """
        Searches for a single instance of an object and raises an error if 0 or 2+ are found

        Required arguments:
        - obj       - Object class to aquire. For example, client.QualityProcess

        Optional arguments:
        - **kwargs  - Property arguments for search parameters. Should be sufficiently narrow to define a single object.
        """

        results=self.Listing(obj_type, **kwargs)

        if len(results) != 1:
            raise RuntimeError(f"{len(results)} instances of {obj_type.__class__.__name__} found: {results}")

        return results[0]

    def clear_cache(self, item=None):

        """
        Dumps cached versions of an item, causing it to be reloaded from Arena on next access.

        Optional arguments:

        - item    - Any object corresponding to any Arena record. If None, dumps the entire cache.
        """

        if item and isinstance(item, classes.Object):
            item=item.cache_key

        if item:
            classes.OBJ_CACHE.pop(item, None)

        else:
            classes.OBJ_CACHE={}

        return True


    @property
    def me(self):

        """
        Returns the currently authenticated User
        """

        if self.__dict__.get("me"):
            return self.__dict__['me']
        else:
            self.__dict__['me']=self.Listing(self.User, email=self.__dict__['_username'])[0]
            return self.__dict__['me']

   
def docs():

    """
    Generate and display this documentation page.
    """

    classlist = {name:cls for name, cls in list(classes.__dict__.items()) if isinstance(cls, type) and name not in ["Object"] and "_mixin" not in name}
    classlist["Arena"]=Arena

    #page header
    md = "# `Pyrena Docs`\n\n"

    #Iterate through classes (including the Arena client class)
    for class_name in sorted(classlist.keys()):
        class_obj = classlist[class_name]

        methods=[x for x in sorted(dir(class_obj)) if callable(getattr(class_obj, x)) and not x.startswith('_')]

        params=inspect.signature(class_obj.__init__).parameters
        class_args=[f"{'*' if params[x].name=='args' else ''}{'**' if params[x].name=='kwargs' else ''}{params[x].name}{f'={params[x].default.__repr__()}' if params[x].default != params[x].empty else ''}" for x in params]

        md+= f"## `{class_name}({', '.join(class_args)})`\n\n{f'{class_obj.__init__.__doc__}' if class_obj.__init__.__doc__ else ''}\n\n"

        #iterate through callable methods of that class
        for method in methods:

            params=inspect.signature(getattr(class_obj, method)).parameters

            args = [f"{'*' if params[x].name=='args' else ''}{'**' if params[x].name=='kwargs' else ''}{params[x].name}{f'={params[x].default.__repr__()}' if params[x].default != params[x].empty else ''}" for x in params if params[x].name!='self']

            doc = getattr(class_obj, method).__doc__.format(name=class_obj.__name__)

            md+= f"### `{method}({', '.join(args)})`\n\n{doc}\n\n"

    with open("pyrena.html", "w+") as file:
        file.write(mistletoe.markdown(md))
        file.truncate()

    webbrowser.open("pyrena.html")