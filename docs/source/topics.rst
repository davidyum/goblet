======
Topics
======

Routing
^^^^^^^^

The Goblet.route() method is used to construct which routes you want to create for your API. 
The concept is the same mechanism used by Flask. You decorate a function with @app.route(...), 
and whenever a user requests that URL, the function you’ve decorated is called. For example, 
suppose you deployed this app:

.. code:: python 

    from goblet import Goblet

    app = Goblet(function_name='helloworld')

    @app.route('/')
    def index():
        return {'view': 'index'}

    @app.route('/a')
    def a():
        return {'view': 'a'}

    @app.route('/b')
    def b():
        return {'view': 'b'}

If you go to https://endpoint/, the index() function would be called. If you went to https://endpoint/a and https://endpoint/b, then the a() and b() function would be called, respectively.

You can also create a route that captures part of the URL. This captured value will then be passed in as arguments to your view function:

.. code:: python 

    @app.route('/users/{name}')
    def users(name):
        return {'name': name}

If you then go to https://endpoint/users/james, then the view function will be called as: users('james'). 
The parameters are passed as keyword parameters based on the name as they appear in the URL. 
The argument names for the view function must match the name of the captured argument:

.. code:: python 

    @app.route('/a/{first}/b/{second}')
    def users(first, second):
        return {'first': first, 'second': second}


Config
^^^^^^

You can provide custom configurations for your cloudfunctions and goblet deployment by using the config.json file which should be 
located in the .goblet folder. If one doesn't exist then you should add one. 

To provide custom values for the cloudfunction configuration pass in your desired overrides in the ``cloudfunction`` key. See below for example.

Example fields include 

- environmentVariables
- labels
- availableMemoryMb
- timeout

Example config.json: 

.. code:: json

    {
        "cloudfunction":{
            "environmentVariables": {"env1":"var1"},
            "labels": {"label1":"val1"},
            "availableMemoryMb": 256,
            "timeout": "30s"
        }
    }

see the `cloudfunction`_ docs for more details on the fields.

.. _CLOUDFUNCTION: https://cloud.google.com/functions/docs/reference/rest/v1/projects.locations.functions#CloudFunction

By default goblet includes all python files located in the directory. To include other files use the ``customFiles`` key
which takes in a list of python `glob`_ formatted strings.

Example config.json: 

.. code:: json

    {
        "customFiles": ["*.yaml"]
    }   

.. _GLOB: https://docs.python.org/3/library/glob.html


You can customize the configs for an Api Gateway using the `apiConfig` key in `config.json`. Allowed fields can be found 
`here <https://cloud.google.com/api-gateway/docs/reference/rest/v1/projects.locations.apis.configs#ApiConfig>`_ and include 

* gatewayServiceAccount
* labels 
* displayName

.. code:: json

    {
        "apiConfig": {
            "gatewayServiceAccount": "projects/-/serviceAccounts/ServiceAccount@PROJECT",
            "labels": {
                "label1" : "value1"
            }
        }
    }  

Iam Bindings
^^^^^^^^^^^^

You can add Iam bindings to your cloudfunctions by adding a `binding` section to your `congig.json` file.
The bindings should be in the `GCP Policy format <https://cloud.google.com/functions/docs/reference/rest/v1/Policy>`_

For example to allow unauthenticated (public) access to your cloudfunctions you would add the `roles/cloudfunctions.invoker` to
member `allUsers`

.. code:: json

    {
        "bindings": [
            {
                "role": "roles/cloudfunctions.invoker",
                "members": [
                    "allUsers"
                ]
            }
        ]
    }

To remove bindings once they are deploy you should update your `bindings` in `config.json` and change the `members` to be an empty list

.. code:: json

    {
        "bindings": [
            {
                "role": "roles/cloudfunctions.invoker",
                "members": []
            }
        ]
    }


Run Locally
^^^^^^^^^^^

Running your functions locally for testing and debugging is easy to do with the goblet command `goblet local`. 
You can hit your functions endpoint at ``localhost:8080``.

You can have a custom local name by seting the local param in the goblet class

.. code:: python

    from goblet import Goblet

    app = Goblet(function_name="goblet_example", local='test')


Then run ``goblet local test``

Note: If you have both `http()` and `route("/")` in order to test the route locally make sure to add the header ``X-Envoy-Original-Path``. Otherwise the route will default to ``@http()``

.. code:: sh 

    curl localhost:8080/endpoint

To test a scheduled job locally you will need to include two headers in your request. One ``X-Goblet-Type:schedule`` and 
``X-Goblet-Name:FUNCTION_NAME`` which is the name of your function.

.. code:: sh 

    curl -H X-Goblet-Type:schedule -H X-Goblet-Name:FUNCTION_NAME localhost:8080


Debugging with VScode
^^^^^^^^^^^^^^^^^^^^^

To debug your functions locally with Vscode you can use the following configuration. Replace LOCAL_NAME with the name you 
passed into ``goblet(NAME, local=LOCAL_NAME)``. Make sure that there are no naming collisions with any function names used in your app.

.. code:: json 

    {
        "configurations": [
            {
                "name": "Python: Module",
                "type": "python",
                "request": "launch",
                "module": "functions_framework",
                "args": [
                    "--target",
                    "LOCAL_NAME",
                    "--debug"
                ]
            }
        ]
    }


Authentication
^^^^^^^^^^^^^^
API gateway supports several authentication options including, `jwt`_, `firebase`_, `auth0`_, `Okta`_, `google_id`_, 

.. _JWT: https://cloud.google.com/api-gateway/docs/authenticating-users-jwt
.. _firebase: https://cloud.google.com/api-gateway/docs/authenticating-users-firebase
.. _auth0: https://cloud.google.com/api-gateway/docs/authenticating-users-auth0
.. _Okta: https://cloud.google.com/api-gateway/docs/authenticating-users-okta
.. _google_id: https://cloud.google.com/api-gateway/docs/authenticating-users-googleid

To configure authentication with goblet simply add the desired configuration in the ``securityDefinitions`` option in config.json. See the 
API gateway docs linked above for more details on how to set up the configuration. 

An api using JWT authentication would require the following in ``config.json``

.. code:: json

    {
        "securityDefinitions":{
            "your_custom_auth_id":{
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-issuer": "issuer of the token",
                "x-google-jwks_uri": "url to the public key"
            }
        }
    }

This generates a `security section <https://swagger.io/docs/specification/2-0/authentication/>`_ in the openapi 
spec with empty scopes. If you would like to customize the security section and add custom scopes use the `security` 
section in `config.json`


.. code:: json

    {
        "security":[
            {
                "OAuth2": ["read", "write"]
            }
        ]
    }


If you would like to apply security at the method level then you can add security policy in the route decorator.

.. code:: python 

    @app.route('/method_security', security=[{"your_custom_auth_id": []}])


Another common use case is to authenticate via a service account, which requires the follow secuirty definition. You can specify
multiple service accounts by adding additional entries to the `securityDefinitions` dictionary.

.. code:: json 

    {
        "securityDefinitions": {
            "SERVICE_ACCOUNT_NAME": {
                "authorizationUrl": "",
                "flow": "implicit",
                "type": "oauth2",
                "x-google-audiences": "SERVICE_ACCOUNT_EMAIL",
                "x-google-issuer": "SERVICE_ACCOUNT_EMAIL",
                "x-google-jwks_uri": "https://www.googleapis.com/service_accounts/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL"
            }
        }
    }

Now to access your api endpoint you can use the following python script to generate a jwt token and add it as a bearer token to your request.


.. code:: python 

    import time
    import json 
    import urllib.parse
    import requests
    from oauth2client.client import GoogleCredentials
    from googleapiclient import discovery

    def generate_jwt_payload(service_account_email):
        """Generates jwt payload"""
        now = int(time.time())
        payload = {
            'iat': now,
            "exp": now + 3600,
            'iss': service_account_email,
            'aud':  service_account_email,
            'sub': service_account_email,
            'email': service_account_email
        }
        return payload

    def get_jwt(service_account_email):
        """Generate a signed JSON Web Token using a Google API Service Account."""

        credentials = GoogleCredentials.get_application_default()
        service = discovery.build('iamcredentials', 'v1', credentials=credentials)
        body = {
            "payload": json.dumps(generate_jwt_payload(service_account_email))
        }
        encoded_sa = urllib.parse.quote_plus(service_account_email)
        resp = service.projects().serviceAccounts().signJwt(name=f"projects/-/serviceAccounts/{encoded_sa}", body=body).execute()
        return resp["signedJwt"]


    def make_jwt_request(service_account_email, url):
        """Makes an authorized request to the endpoint"""
        signed_jwt = get_jwt(service_account_email)
        headers = {
            'Authorization': 'Bearer {}'.format(signed_jwt),
            'content-type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        return response


    if __name__ == '__main__':
        print(make_jwt_request(SERVICE_ACCOUNT_EMAIL,GATEWAY_URL).text)


Request
^^^^^^^
 
The route path can only contain [a-zA-Z0-9._-] chars and curly braces for parts of the URL you want to capture. 
To access other parts of the request including headers, query strings, and post data you can use ``app.current_request`` to get
the request object. To see all fields see `request <https://tedboy.github.io/flask/generated/generated/werkzeug.Request.html>`__
Note, that this also means you cannot control the routing based on query strings or headers. 
Here’s an example for accessing query string data in a view function:

.. code:: python 

    @app.route('/users/{name}')
    def users(name):
        result = {'name': name}
        if app.current_request.args.get('include-greeting') == 'true':
            result['greeting'] = 'Hello, %s' % name
        return result

Here’s an example for accessing post data in a view function:

.. code:: python 

    @app.route('/users}', methods=["POST"])
    def users():
        json_data = app.current_request.json
        return json_data

To see the full list of available fields see `request <https://tedboy.github.io/flask/generated/generated/werkzeug.Request.html>`__

Response
^^^^^^^^
Goblet http function response should be of the form a flask `response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Response>`__. See more at the `cloudfunctions`_ documentation

To see the full list of available fields see `response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Response>`__

.. _CLOUDFUNCTIONS: https://cloud.google.com/functions/docs/writing/http


You can use goblet's ``Response`` class to make it easier to pass in custom headers and response codes.

.. code:: python 

    from goblet import Response

    @app.route('/response')
    def response():
        return Response({"failed": 400}, headers={"Content-Type": "application/json"}, status_code=400)


Another option is goblet's ``jsonify``, which is a helper to create response objects.

.. code:: python 

    from goblet import jsonify

    jsonify(*args, **kwargs)



This function wraps dumps() to add a few enhancements that make life easier. It turns the JSON output into a Response 
object with the application/json mimetype. For convenience, it also converts multiple arguments into an array or 
multiple keyword arguments into a dict. This means that both jsonify(1,2,3) and jsonify([1,2,3]) serialize to [1,2,3].

For clarity, the JSON serialization behavior has the following differences from dumps():

Single argument: Passed straight through to dumps().

Multiple arguments: Converted to an array before being passed to dumps().

Multiple keyword arguments: Converted to a dict before being passed to dumps().

Both args and kwargs: Behavior undefined and will throw an exception.

Example usage:

.. code:: python 

    @app.route('/get_current_user')
    def get_current_user():
        return jsonify(username=g.user.username,
                    email=g.user.email,
                    id=g.user.id)

This will send a JSON response like this to the browser:

.. code:: json 

    {
        "username": "admin",
        "email": "admin@localhost",
        "id": 42
    }

OpenApi Spec
^^^^^^^^^^^^

Goblet generates an `OpenApi`_ spec from your route endpoints in order to create the api gateway. The open api spec is written to the 
``.goblet`` folder and can be used for other tools. To generate just the open api spec you can run the command ``goblet openapi FUNCTION_NAME``.
Note that gcp `gateway`_ only supports openapi spec 2.0. 


By default the param types will be created in the spec as strings and a base 200 response. 
You can specify custom param and response types using python typing and pass in openapi requestType and responses to the route.

If you use a custom schema type you should create a schema class that inherits from marshmallow Schema. 

.. code:: python 

    from typing import List
    from marshmallow import Schema, fields

    # Typed Path Param
    @app.route('/home/{name}/{id}', methods=["GET"])
    def namer(name: str, id: int):
        return f"{name}: {id}"

    class Point(Schema):
        lat = fields.Int()
        lng = fields.Int()

    # custom schema types
    @app.route('/points')
    def points() -> List[Point]:
        point = Point().load({"lat":0, "lng":0})
        return [point]

    # custom responses and request_types
    # Request body must be schema defition valid with openapi spec 2
    @app.route('/custom', request_body={'schema': {"type": "array", "items": {'type': 'string'}}}, responses={'400': {'description': '400'}})
    def custom():
        request = app.current_request
        assert request.data ["string1", "string2"]
        return

.. _OPENAPI: https://swagger.io/specification/
.. _GATEWAY: https://cloud.google.com/api-gateway/docs/openapi-overview

Multiple Files
^^^^^^^^^^^^^^

It is common to split out your api routes into different sub folders. You can do this by creating seperate goblet instances and combining
them in the main.py folder under your main app. You can do this with simple addition notation or with the ``Goblet.combine`` function

other.py 

.. code:: python

    from goblet import Goblet

    otherapp = Goblet()

    @otherapp.route('/other')
    def other():
        return 'other'

combine all routes in main.py

.. code:: python

    from goblet import Goblet
    from other import otherapp

    app = Goblet('main_function')
    
    app.combine(otherapp)
    # can also do
    # app + otherapp

    @app.route('/home')
    def home():
        return 'home'


Stages
^^^^^^^

You can create different deployments of your api (for example dev and prod) using stages. You can create a new stage from the cli using ``goblet stage create STAGE`` or by 
manually adding an entry in config.json under stages. A stage will require a unique function_name which is used to create resources in gcp. Any fields in your stage will 
override those in the general config file. 

For example the dev deployment will override the environment variable ``env`` with ``dev`` and the prod deployment will yield ``prod``

.. code:: json 

    {
        "cloudfunction": {
            "environmentVariables": {
                "env": "main"
            }
        },
        "stages": {
            "dev": {
                "function_name": "goblet-dev",
                "cloudfunction": {
                    "environmentVariables": {
                        "key": "dev"
                    }
                }
            },
            "prod": {
                "function_name": "goblet-prod",
                "cloudfunction": {
                    "environmentVariables": {
                        "key": "prod"
                    }
                }
            }
        }
    }

You can view your current stages using ``goblet stage list``. To deploy or destroy a specific stage use the ``--stage`` or ``-s`` flag with the stage. You can also use the 
environment variable ``STAGE``. For example ``goblet deploy -s dev``.


API Gateway Backends
^^^^^^^^^^^^^^^^^^^^

Api Gateway supports all available backend services including app engine, GKE, GCE, cloudrun, and cloudfunctions. To add an endpoint to a backend service other than the deployed
cloudfunction, specify the endpoint in the `backend` argment in `route`. Note that the function will not be invoked since the request will be routed to a different backend.

.. code:: python 

    @app.route('/custom_backend', backend="https://www.CLOUDRUN_URL.com/home")
    def home():
        return 

Cors
^^^^

Cors can be set on the route level or on the Goblet application level. Setting `cors=True` uses the default cors setting 

.. code:: json 

    {
        "headers" : {
            "Access-Control-Allow-Headers" : ["Content-Type", "Authorization"],
            "Access-Control-Allow-Origin": "*"
        }
    }

.. code:: python 

    @app.route('/custom_backend', cors=True)
    def home():
        return "cors headers"

Use the `CORSConfig` class to set customized cors headers from the `goblet.resources.routes` class. 

.. code:: python 

    from goblet.resources.routes import CORSConfig

    @app.route('/custom_cors', cors=CORSConfig(allow_origin='localhost'))
    def custom_cors():
        return jsonify('localhost is allowed')

Multiple Cloudfunctions
^^^^^^^^^^^^^^^^^^^^^^^

Using the field `main_file` in `config.json` allows you to set any file as the entrypoint `main.py` file, which is required by cloudfunctions. 
This allows for multiple functions to be deploying using similar code bases.

For example with the following files which each contain a function and share code in `shared.py`

`func1.py`
`func2.py`

Could have the goblet `.config`

.. code: json 
    {
        "stages": {
            "func1": {
                "function_name": "func1",
                "main_file" : "func1"

            },
            "func2": {
                "function_name": "func2",
                "main_file" : "func2"
        }
    }

To test each function locally you can simply run `goblet local -s func1` and to deploy `goblet local -s func1 -p Project -l Region`

Note: This may cause some imports to break if something is importing directly from the func1.py or func2.py since they will be renamed to `main.py` 
in the packaged zipfile.

Note: There is a bug when uploading a different `main_file`, while also having `main.py` in your code, so if you decide to use `main_file` remove `main.py`. The bug 
shows the previos main.py in the gcp console, however the local zipfile and uploaded zipfile in gcs both contain the correct `main.py` 