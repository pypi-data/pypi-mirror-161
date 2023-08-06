Purpose of the Package
======================

Convert intents and entities defined in the Watson Assistant skill
object to rasa nlu.yml file.

Given how rasa works, there is no way to translate dialog flows defined
in WA into rasa stories. So this converter don’t intends to take care of
dialog flows.

Installation
============

You can use pip:

.. code:: bash

   $ pip3 install wa2rasa

*Rasa* and *wa2rasa* use common libraries, to avoid conflicts please
install *wa2rasa* in a separate virtual environment.

Usage
=====

Just run the following command:

.. code:: bash

   $ wa2rasa convert <path_to_your_wa_object>/ <directory_to_store_rasa_nlu_file>/

Here a gif for you:

.. figure:: https://media.giphy.com/media/zQxXPs9HhNJHZBI1Iy/giphy.gif
   :alt: how to use the wa2rasa

Author
======

`Cloves Paiva <https://www.linkedin.com/in/cloves-paiva-02b449124/>`__.
