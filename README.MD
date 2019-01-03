# Bushelper
> Django webapp to manage local bus courses

## Table of contents
* [Overview](#overview)
 * [Requirements](#setup)
* [Features](#features)

## Overview
There are many apps which manage bus courses but most of them are including only courses provided by "Big players". The bushelper is designed for small carriers who are not included in big apps.
Moreover this app is personal field to try myself in Django web app development.

The bushelper takes bus courses from database and returns best way of taking a bus from given location(explicit or by current geolocation).Thanks to the Django Rest Framework, data are ready to use with AJAX requests on client side. Bushelper takes care of representing these informations by communication with Openroute Service Directions API.


## Requirements
* Python 3.4+
* Django 2.1+
* [Django Rest Framework][rest-framework]
* [Openroute Service][openroute] API Key

[rest-framework]:<https://github.com/encode/django-rest-framework>
[openroute]: <https://openrouteservice.org/>


![](https://imgur.com/UnJtOME.jpg)
![](https://imgur.com/UFsz4RT.jpg)
