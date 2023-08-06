from typing import Any


class RigelError(Exception):
    """
    The base exception class for all Rigel errors.

    :type base: string
    :var base: The error message.
    :type code: int
    :cvar code: The error code.
    """
    base: str = 'Generic Rigel error.'
    code: int = 1

    def __init__(self, **kwargs: Any):
        Exception.__init__(self, self.base.format(**kwargs))
        self.kwargs = kwargs


class DockerAPIError(RigelError):
    """
    Raised whenever an exception is thrown while making a call to the Docker API.

    :type exception: docker.errors.DockerException
    :ivar exception: The exception thrown by the Docker API.
    """
    base = "An error occured while calling the Docker API: {exception}"
    code = 2


class InvalidDockerClientInstanceError(RigelError):
    """
    Raised whenever an invalid Docker client instance is provided.
    """
    base = "An invalid instance of python_on_whales.docker_client.DockerClient was provided."
    code = 4


class PydanticValidationError(RigelError):
    """
    Raised whenever a ValidationError is thrown
    while creating instances of pydantic.BaseModel.

    :type exception: pydantic.error_wrappers.ValidationError
    :ivar exception: The exception thrown.
    """
    base = "An error occurred while validating Pydantic model: {exception}."
    code = 6


class UndeclaredEnvironmentVariableError(RigelError):
    """
    Raised whenever an attempt is made to use the value of an undeclared environment variable.

    :type env: string
    :ivar env: The undeclared environment variable.
    """
    base = "Environment variable {env} is not declared."
    code = 7


class UndeclaredGlobalVariableError(RigelError):
    """
    Raised whenever an undeclared global variable is referenced.

    :type field: string
    :ivar field: Path for the field referencing the global varialble.
    :type var: string
    :ivar var: Global variable identifier.
    """
    base = "Field '{field}' set to have the value of undeclared global variable '{var}'."
    code = 8
