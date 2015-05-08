from abc import ABCMeta, abstractmethod, abstractproperty
import hashlib


class AbstractHexDigest:

    __metaclass__ = ABCMeta

    @abstractproperty
    def hexdigest(self):
        "A checksum of the object"


class AbstractHasYamlRepr:

    "Objects that have a YAML representation"

    __metaclass__ = ABCMeta

    @abstractmethod
    def to_yaml(self):
        "Return YAML representation of the object"

    def from_yaml(cls, yamlrepr):
        "Create an object from the yaml representation"
        # not sure how create @abstractclassmethod from abc
        raise NotImplementedError


class AbstractHasJsonRepr:

    "Objects that have a JSON representation"

    __metaclass__ = ABCMeta

    @abstractmethod
    def to_json(self):
        "Return a JSON representation of the object"

    def from_json(cls, jsonrepr):
        "Create an object from the json representation"
        # not sure how to create @abstractclassmethod from abc
        raise NotImplementedError


class File(AbstractHexDigest, AbstractHasYamlRepr, AbstractHasYamlRepr):

    """Represents an entity on the filesystem that may need to be
    transferred.
    """

    def __init__(self, localname, remotename=None, cached=True):
        self._localname = localname
        self._remotename = remotename
        self._cached = cache

    @property
    def localname(self):
        "The name of the file on the local node"
        return self._localname

    @property
    def remotename(self):
        "The name of the file on the remote node"
        return self._remotename

    @property
    def cached(self):
        "Should this file be cached?"
        return self._cached

    @property
    def hexdigest(self):
        if self._checksum is None:
            hasher = hashlib.sha1()
            with open(self.localname, 'rb') as fd:
                hasher.update(fd.read())
            self._checksum = hasher.hexdigest()

        return self._checksum


class Task(AbstractHexDigest, AbstractHasYamlRepr, AbstractHasJsonRepr):

    """A `Task` is something that can be stored somewhere (database,
    filesystem, etc) and executed on some node.
    """

    @property
    def hexdigest(self):
        "Need to commutatively merge file hashes"
        raise NotImplementedError

    def command(self):
        "The command to run"
        raise NotImplementedError

    def iter_input_files(self):
        "Iterable over input files"
        raise NotImplementedError

    def iter_output_files(self):
        "Iterable over output files"
        raise NotImplementedError

    @property
    def task_id(self):
        "Every task should have a distinct id"
        raise NotImplementedError

    def specify_input_file(self):
        "Add an input file"
        raise NotImplementedError

    def specify_output_file(self):
        "Add an output file"
        raise NotImplementedError

    def add_metadata(self, name, value):
        "Add a metadata to the class"
        raise NotImplementedError

    @property
    def metadata(self):
        "Get the metadata associated with the task"
        raise NotImplementedError


class Status(object):

    """
    Represents the result of querying for the status of a `Task`
    """

    raise NotImplementedError
