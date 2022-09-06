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

import pyrena.classes as classes

class ArenaHTTPError(Exception):
    pass

class Arena():

    def __init__(self, username=None, password=None, ssl_verify=True, user_agent="Python Pyrena", verbose=False, arenagov=False):

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


        self.headers={
            "User-Agent": self.user_agent,
            "Content-Type": "application/json"
        }

        self._reqs_remaining=25000

        #login
        try:
            self.login()
        except ArenaHTTPError:
            print("Unable to log in. Call `login(username, password)` on this client to authenticate with Arena.")
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
        return f"<Arena(user={self.__dict__['_username']})>"

    def login(self, username=None, password=None):

        """
        Log into Arena

        Optional arguments:
        - username    - Username. Defaults to username given at client creation if not specified.
        - password    - Password. Defaults to password given at client creation if not specified.
        """

        self.__dict__["_username"] = username or self.__dict__["_username"]
        self.__dict__["_password"] = password or self.__dict__["_password"]

        login_data = self._post(
            "/login",
            data={
                "email":self.__dict__["_username"],
                "password":self.__dict__["_password"]
                }
            )


        #set auth token
        self.headers["arena_session_id"]=login_data["arenaSessionId"]

        #set workspace id and name
        self._workspace_id=login_data["workspaceId"]
        self._workspace_name=login_data["workspaceName"]

        #set time to re-auth, 1 min before expiry
        self.reauth_utc = int(time.time())+60*60*80

    def logout(self):

        """
        Log out of Arena.
        """

        self._put("/logout")
        self.__dict__["_username"]=None
        self.__dict__["_password"]=None
        self.__dict__["me"]=None
        self._workspace_id=None
        self._workspace_name=NOne
        self.headers["arena_session_id"]=None
        self.reauth_utc=0

    def _fetch(self, method, endpoint, params={}, data={}, files={}, headers={}, expect_json=True, **kwargs):

        if not self._reqs_remaining:
            raise ArenaHTTPError("Request limit of 25000/day reached.")

        #reauth 1 min before expiry
        if endpoint != "/login" and int(time.time())> self.reauth_utc:
            self.login()

        url = f"{self.base_url}{'' if endpoint.startswith('/') else '/'}{endpoint}"

        req_headers=self.headers
        for header in headers:
            req_headers[header]=headers[header]

        try:
            req = getattr(requests, method.lower())(
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
            print(f"status {req.status_code}")
            pprint(req.json())

        if req.status_code >=400:
            data=req.json()
            raise ArenaHTTPError(f"HTTP Error {req.status_code} - {data['errors'][0]['message']} (Arena Error Code {data['errors'][0]['code']})")

        req.raise_for_status()


        #update reqs remaining
        self._reqs_remaining = req.headers.get("X-Arena-Requests-Remaining", self._reqs_remaining)

        if method.lower()=="delete":
            return
        elif expect_json=False:
            return req.content
        else:
            return req.json()

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


        if len(listing)==limit:
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

    def archive(self, folder_name="", exclude=[]):

        """
        WIP feature

        Downloads all available data from the current Arena instance and saves it in JSON format.
        Intended to be used as a rapid bulk export for local backup.

        This may take some time, will verbosely output data, and may consume a large portion of the daily API limit.

        Optional arguments:

        - folder    - Path to existing archive folder, if one already exists
        - exclude   - list of Arena classes to exclude from the backup.
        """

        d= time.strftime("%d_%B_%Y")

        folder_name = folder_name or f"Arena_archive_{d}"

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        #Files
        if self.File not in exclude:
            files=self.Listing(self.File, limit=None)

            with open(f"{folder_name}/files_{time.strftime('%d_%B_%Y')}.txt", "w+"):
                file.write(json.dumps([x.json for x in files], indent=2))
                file.truncate()

            if not os.path.exists(f"{folder_name}/file_vault"):
                os.mkdir(f"{folder_name}/file_vault")

            for file in files:
                with open(f"{folder_name}/file_vault/[{file.number}] {file.title}.{file.format}", "w+") as f:


        #Item
        if self.Item not in exclude:
            items = self.Listing(self.Item, limit=None)
            for item in items:
                item.__dict__["files"]=[x.json for x in item.file_associations]
                item.__dict__["revisions"]=[x.json for x in item.revisions]

            with open(f"{folder_name}/items_{time.strftime('%d_%B_%Y')}.txt", "w+") as f:
                f.write(json.dumps([x.json for x in items], indent=2))
                f.truncate()

        #Quality
        if self.QualityProcess not in exclude:
            qps = self.Listing(self.QualityProcess, limit=None)
            for qp in qps:
                for step in qp.steps:
                    step.__dict__['affected']=[x.json for x in step.affected]
                qp.__dict__["steps"]=[x.json for x in qp.steps]

            with open(f"{folder_name}/quality_{time.strftime('%d_%B_%Y')}.txt", "w+") as f:
                f.write(json.dumps([x.json for x in qps], indent=2))
                f.truncate()

        #Training
        if self.TrainingPlan not in exclude:
            tps = self.Listing(self.TrainingPlan, limit=None)
            for tp in tps:
                tp.__dict__["records"]=[x.json for x in tp.records]
                tp.__dict__["items"]=[x.json for x in tp.item_associations]
                tp.__dict__["users"]=[x.json for x in tp.user_associations]

            with open(f"{folder_name}/training_{time.strftime('%d_%B_%Y')}.txt", "w+") as f:
                f.write(json.dumps([x.json for x in tps], indent=2))
                f.truncate()

def docs():

    """
    Generate and display this documentation page.
    """

    classlist = {name:cls for name, cls in list(classes.__dict__.items()) if isinstance(cls, type) and name!="Object"}
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