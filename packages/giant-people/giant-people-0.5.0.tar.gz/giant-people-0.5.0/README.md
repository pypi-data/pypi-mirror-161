# Giant People

A re-usable package which can be used in any project that requires a generic `People` app. 

This will include the basic formatting and functionality such as model creation via the admin. The package also includes a cms plugin which allows a client to add a select number of people to a page and order them via a "drag and drop", provided by `django-admin-sortable2`. 

## Installation

To install with the package manager, run:

    $ poetry add giant-people

You should then add `"people", "easy_thumbnails" and "filer"` to the `INSTALLED_APPS` in your settings file. 
The detail pages in this app use plugins which are not contained within this app. It is recommended that you include a set of plugins in your project, or use the `giant-plugins` app.

In order to run `django-admin` commands you will need to set the `DJANGO_SETTINGS_MODULE` by running

    $ export DJANGO_SETTINGS_MODULE=settings

## Configuration

This application exposes the following settings:


- `PEOPLE_ADMIN_LIST_DISPLAY` is the field list for the admin index. This must be a list.
- `PEOPLE_ADMIN_SEARCH_FIELDS` is the fields that can be searched against in the admin. This must be a list.
- `PEOPLE_ADMIN_FIELDSETS` allows the user to define the admin fieldset. This must be a list of two-tuples.
- `PEOPLE_ADMIN_READONLY_FIELDS` allows the user to configure readonly fields in the admin. This must be a list.

## Preparing for release
 
In order to prep the package for a new release on TestPyPi and PyPi there is one key thing that you need to do. You need to update the version number in the `pyproject.toml`.
This is so that the package can be published without running into version number conflicts. The version numbering must also follow the Semantic Version rules which can be found here https://semver.org/.

## Publishing

Publishing a package with poetry is incredibly easy. Once you have checked that the version number has been updated (not the same as a previous version) then you only need to run two commands.

  $ `poetry build` 

will package the project up for you into a way that can be published.

  $ `poetry publish`

will publish the package to PyPi. You will need to enter the username and password for the account which can be found in the company password manager
