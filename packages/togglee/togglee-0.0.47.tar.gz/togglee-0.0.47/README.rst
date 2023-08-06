|LogoMakr_4ojFPZ|
=================

**Motivation**
==============

Simple library to separate deployment of features from release time. It uses network accesible files without the need of a server to provide feature toggles.

**Installation**
================

add it to your project using `pip install togglee`

**Usage**
=========

.. code:: python

   from togglee import Togglee

   url = "https://gist.githubusercontent.com/kanekotic/c469f99bef5a5c0634b4a94a4acd6546/raw/b67985d8e3a5112c9be2da47bdadf2cf17edbe44/toggles"
   refresh_rate_seconds = 5
   default_values = [
        {
            "name": "prop",
            "type": "release",
            "value": True
        }
    ]
   subject = Togglee(url, refresh_rate_seconds, default_values)
   if subject.is_enabled("prop"):
       print("do stuff")
   else:
       print("dont do stuff")

**Type of toggles**
===================

**Release**

Simple true/false logical path definition.

.. code-block:: JSON

    {
        "type": "release",
        "value": true,
    }

**Context**

Allows complex logic to decide the outcome of the logical path (example traffic, users, resources available). 

.. code-block:: JSON

    {
        "type": "context",
        "conditions": [
            {
                "field": "username",
                "value": "user1",
                "operation": "eq"
            }
        ]
    }

available operations are:

- 'eq': equal (===)
- 'ne': not equal (!==)
- 'gt': greater than (>)
- 'ge': greater equal (>=)
- 'lt': lesser than (<)
- 'le': lesser qqual (<=)

.. |LogoMakr_4ojFPZ| image:: https://user-images.githubusercontent.com/3071208/90978825-2b93de00-e540-11ea-8e0d-60267e95fec8.png