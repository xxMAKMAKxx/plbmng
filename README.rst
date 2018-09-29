======
plbmng
======

Description
-----------
``plbmng`` is a tool created for usage within PlanetLab network. Main purpose of this tool is to manage and monitor your PlanetLab nodes. 

For this purpose there are several tools within this project:
        - to get all the servers and gather all available information about them
        - to create a map with location of the servers
        - to set-up a cron job which gets infromation about latency and/or ssh availability for the selected servers

Dependencies
------------
        - Python 3.6.5 (Python scripts have been tested on this version but they will probably work with other versions too.)
        - Python modules (all modules are available from pip):
                - geocoder
                - folium
                - numpy
                - vincent
                - pandas
        - For Fedora-like distros:
                .. code-block:: bash
                 
                 $ sudo dnf install -y dialog pssh fping

Instalation
-----------
Make sure you have installed all dependencies!
To install the plbmng module, type:

.. code-block:: bash

         $ pip install plbmng

Locate plbmng folder and run:

.. code-block:: bash
        
          $ ./plbmng.sh

Basic usage
-----------
When you run plbmng for the first time, you will be asked to add your credentials to Planetlab network. If you don't want to add your credentials right away, you can skip it and add it in the settings later or edit the config file located in the bin folder.

Once you added your credentials, use ``Monitor now`` option in the Measure menu. It downloads all servers from your slice and exports it as ``default.node`` file. This step is important because other functions will not work without it.

``Main menu``

``Search nodes``: If you are looking for some specific node or set of nodes, use ``Search nodes`` option. In the next screen you can choose from three filters: search by DNS, IP or location. If you choose search by DNS or IP you will be prompted to type a string, which indicates the domain you are looking for. If you want to search by location, you will be asked to choose a continent and a country. Then you will see all available nodes from this selected country and you can choose one of them to see more detailes about this particular node. At the bottom of the information screen you can choose from three options. 

``Measure menu``: In this menu you can set-up a cron job for monitoring your slice. 
                 -  ``Set monitoring period``, here you can specify how often you wish to run the monitoring. 
                 -  ``Set monitored elements``, supported elements are ping and SSH.
                 -  ``Monitor now`` will immediately run a test which you have chosen in the ``Set monitored elements``.

``Map menu``:
             ``Generate map``, will create a map with all nodes from ``planetlab.node`` file. You can choose what shall be displayed on the map in ``Select map elements``, select what do display on map. You can choose from ICMP responses and SSH time.
``Settings menu``:
                  In the settings menu you can change your username, password, slice name and path to your private key. Another option how to change these parameters is to edit plbmng.conf file located in the bin folder.

Authors
-------

- `Ivan Andrasov`_ - Creator of the project
- `Filip Suba`_ - Improvements to the project and creator of planetlab_list_creator
- `Dan Komosny`_ - Maintainer and supervisor of the project

.. _`Ivan Andrasov`: https://github.com/Andrasov
.. _`Filip Suba`: https://github.com/fsuba
.. _`Dan Komosny`: https://www.vutbr.cz/en/people/dan-komosny-3065
