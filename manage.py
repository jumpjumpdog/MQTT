#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libfreeiot import app
from libfreeiot.adapters.mqtt import MQTTAdapter
from libfreeiot.adapters.file import FileAdapter

if __name__ == '__main__':
    app.run(adapters = [ MQTTAdapter(), FileAdapter() ])
    # app.run()