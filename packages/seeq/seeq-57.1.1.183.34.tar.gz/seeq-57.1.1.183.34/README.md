
The **seeq** Python module is used to interface with Seeq Server ([http://www.seeq.com](http://www.seeq.com)).

**IMPORTANT:**

This module does **NOT** follow semantic versioning.

The **Seeq** Python module's version number is of the form `a.b.c.F.G`. For example, `0.46.0.178.00`.

**For Seeq Python versions before 178**, the minor version _G_ is not used. For example, `0.46.0.118`

**For Seeq Server version R22**, the Seeq Server version is of the form `R22.a.bb.cc`. 
For example, `R22.0.47.02`. 

**For Seeq Server versions R50 and later**, the Seeq Server version is of the form `Raa.b.c`.
For example `R51.2.0`.

You must use particular PIP commands to install a version of the **seeq** Python module that is compatible
with the version of Seeq Server you are using.

Here are some examples.

| Seeq Server Version | PIP Install Command |
|---------------------|-------------------------------|
| R22.0.46.00 | `pip install -U seeq~=0.46.0` |
| R22.0.47.02 | `pip install -U seeq~=0.47.2` |
| R50.0.0 | `pip install -U seeq~=50.0` |
| R51.2.1 | `pip install -U seeq~=51.2` |

**Note how the commands for R50 and later only utilize the `a` and `b` part of the Seeq Server version,
while R22 commands must utilize `a`, `b` and `c`.**

The last part of the version of this `seeq` module (the _F.G_ of a.b.c.F.G) is referred to as the
_functional version_ and refers to the level of functionality (and bug fixes) present in the package
for the SPy module (with _F_ and _G_ being the major and minor SPy versions, respectively).
For example,`0.47.0.178.01` and `50.2.1.178.01` have the same level of SPy functionality
but are built for the respective versions of Seeq Server (R22.0.47.00 and R50.2.1).

In order to keep the SPy testing and compatibility matrix manageable, the latest functional versions (v183+) are
published only for Seeq Server R55 and higher. 

# seeq.spy

The Seeq **SPy** module is a friendly set of functions that are optimized for use with
[Jupyter](https://jupyter.org), [Pandas](https://pandas.pydata.org/) and [NumPy](https://www.numpy.org/).

The SPy module is the best choice if you're trying to do any of the following:

- Search for signals, conditions, scalars, assets
- Pull data out of Seeq
- Import data in a programmatic way (when Seeq Workbench's *CSV Import* capability won't cut it)
- Calculate new data in Python and push it into Seeq
- Create an asset model

**Use of the SPy module requires Python 3.7 or later.**

To start exploring the SPy module, execute the following lines of code in Jupyter:

```
from seeq import spy
spy.docs.copy()
```

Your Jupyter folder will now contain a `SPy Documentation` folder that has a *Tutorial* and *Command Reference*
notebook that will walk you through common activities.

For more advanced tasks, you may need to use the SDK module described below.

# seeq.sdk

The Seeq **SDK** module is a set of Python bindings for the Seeq Server REST API. You can experiment with the
REST API by selecting the *API Reference* menu item in the upper-right "hamburger" menu of Seeq Workbench.

**The SDK module supports both Python 2.x and Python 3.x, but it is strongly recommended that you use Python 3.x
(or later) as Python 2.x is end-of-life.**

Login is accomplished with the following pattern:

```
import seeq
import getpass

api_client = seeq.sdk.ApiClient('http://localhost:34216/api')

# Change this to False if you're getting errors related to SSL
seeq.sdk.Configuration().verify_ssl = True

auth_api = seeq.sdk.AuthApi(api_client)
auth_input = seeq.sdk.AuthInputV1()

# Use raw_input() instead of input() if you're using Python 2
auth_input.username = input('Username:').rstrip().lower()
auth_input.password = getpass.getpass()
auth_input.auth_provider_class = "Auth"
auth_input.auth_provider_id = "Seeq"
auth_api.login(body=auth_input)
```

The `api_client` object is then used as the argument to construct any API object you need, such as
`seeq.sdk.ItemsApi`. Each of the root endpoints that you see in the *API Reference* webpage corresponds
to a `seeq.sdk.XxxxxApi` class.

# Upgrade Considerations

## DataFrame Metadata

In **SPy v183** and later, the DataFrame metadata that is described in the *Properties stored in the output DataFrame*
section of the **spy.search.ipynb** documentation notebook has been moved into a top-level `spy` namespace on the
DataFrame (as opposed to each variable being at the top level). For example, in order to access the function name that
was used to produce the DataFrame, you would use `search_df.spy.func` instead of just `search_df.func`. This change was
made to avoid collisions with native DataFrame properties and functions.

## spy.assets

In **SPy v183** and later, `spy.assets.build()` conducts the build process in two passes instead of one. This generally
has no repercussions for your Asset- or Mixin-derived classes, but you will notice that
`@Asset.Component`-decorated functions are called twice per asset. In the first pass, the framework is expecting the
component asset classes to be instantiated, and in the second pass it is expecting all attributes to be evaluated and
built. This new behavior generally does not require you to make any changes to your classes, with one exception: If you
were using `@Asset.Component` as a means by which you could generate multiple signals/conditions/scalars/metrics from a
single function, you should instead use `@Asset.Attribute` to achieve that.

## spy.workbooks

In **Seeq Server R22.0.49.00**, the ability to schedule the update of an Organizer Topic was added. As
a result, much of the internals of how Organizer Topic embedded content and date ranges are represented
changed.

If you have used `spy.workbooks.save()` in R22.0.48.XX and earlier to save a set of Organizer Topic
workbooks to disk, you will not be able to use those files in R22.0.49.00 and later.

Live Docs must now be specified by a `schedule` on the `TopicDocument` object. The `@Asset.DateRange`
decorator no longer honors the `Auto Refresh Rate` property. To specify a Live Doc, you must specify a
`schedule` dict for a TopicDocument by setting `document.schedule['Background'] = False` and then
specifying a Cron expression like `schedule['Cron Schedule'] = ['*/30 * * * * *']` (every thirty seconds).
Alternatively, you can specify a Scheduled Doc by setting `document.schedule['Background'] = True`.

----------

In case you are looking for the Gencove package, it is available here: https://pypi.org/project/gencove/