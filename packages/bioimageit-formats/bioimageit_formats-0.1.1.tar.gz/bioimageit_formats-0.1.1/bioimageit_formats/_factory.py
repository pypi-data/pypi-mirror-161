# -*- coding: utf-8 -*-
"""BioImageIT formats reader service provider.

This module implement the runner service provider

Classes
-------
RunnerServiceProvider

"""
from ._plugins._csv import (TableCSVServiceBuilder, ArrayCSVServiceBuilder, NumberCSVServiceBuilder)
from ._plugins._imagetiff import ImagetiffServiceBuilder
from ._plugins._imagezarr import ImagezarrServiceBuilder
from ._plugins._movietxt import MovietxtServiceBuilder
from ._plugins._trackmate import TrackmateModelServiceBuilder


class ObjectFactory:
    """Agnostic factory

    Implements the factory design pattern

    """
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        """Add a new service builder to the factory"""
        self._builders[key] = builder

    def create(self, key, **kwargs):
        """Create a new service builder"""
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


class FormatsReaderServiceProvider(ObjectFactory):
    """Service provider for the formats readers"""
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


formatsServices = FormatsReaderServiceProvider()
formatsServices.register_builder('imagetiff', ImagetiffServiceBuilder())
formatsServices.register_builder('imagezarr', ImagezarrServiceBuilder())
formatsServices.register_builder('movietxt', MovietxtServiceBuilder())
formatsServices.register_builder('tablecsv', TableCSVServiceBuilder())
formatsServices.register_builder('arraycsv', ArrayCSVServiceBuilder())
formatsServices.register_builder('numbercsv', NumberCSVServiceBuilder())
formatsServices.register_builder('trackmatemodel', TrackmateModelServiceBuilder())
