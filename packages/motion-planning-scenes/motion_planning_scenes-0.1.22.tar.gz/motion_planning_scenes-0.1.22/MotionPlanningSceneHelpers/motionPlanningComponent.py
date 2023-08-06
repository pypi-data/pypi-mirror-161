from abc import ABC, abstractmethod
import yaml


class ComponentIncompleteError(Exception):
    pass


class DimensionNotSuitableForEnv(Exception):
    pass


class MotionPlanningComponent(ABC):

    def __init__(self, **kwargs):
        if 'contentDict' in kwargs and 'name' in kwargs:
            self._content_dict = kwargs.get('contentDict')
            self._name = kwargs.get('name')
        elif 'fileName' in kwargs:
            with open(kwargs.get('fileName'), 'r') as stream:
                self._content_dict = yaml.safe_load(stream)
            self._name = self._content_dict['name']
            del self._content_dict['name']

    def checkCompleteness(self):
        incomplete = False
        missingKeys = ""
        for key in self._required_keys:
            if key not in self._content_dict.keys():
                incomplete = True
                missingKeys += key + ", "
        if incomplete:
            raise ComponentIncompleteError("Missing keys: %s" % missingKeys[:-2])

    def name(self):
        return self._name

    @abstractmethod
    def toDict(self):
        pass
