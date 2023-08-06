import uuid
from typing import Optional


class GantryException(Exception):
    """
    Base class for Gantry exceptions.
    """

    pass


class GantryLoggingException(GantryException):
    """
    Raised when logging invalid data.
    """

    pass


class GantryLoggingDataTypeError(GantryLoggingException):
    """
    Raised when Gantry cannot process datatype
    """

    pass


class ConfigurationMissing(GantryException):
    """
    There is some configuration missing
    """

    def __init__(self, message=""):
        if len(message) == 0:
            message = "Gantry is missing some configuration"
        else:
            message = "Gantry is missing some configuration: {}".format(message)

        super(ConfigurationMissing, self).__init__(message)


class InvalidConfigError(GantryException):
    """
    Invalid configuration passed in
    """

    pass


class ClientNotInitialized(GantryException):
    """
    Gantry client not initialized
    """

    def __init__(self):
        message = "Gantry client is not initialized. Did you call `gantry.init()`?"
        super(ClientNotInitialized, self).__init__(message)


class DatabaseAccessError(GantryException):
    """
    Gantry client not initialized
    """

    def __init__(self, message=""):
        if len(message) == 0:
            message = "Unable to access database, check the configuration"
        super(DatabaseAccessError, self).__init__(message)


class FeedbackEventMissingPrediction(GantryException):
    """
    Feedback event cannot be processed right now because we cannot find the
    corresponding predictions. Could be raised because the prediction has not
    been ingested or processed by the system.
    """

    def __init__(self, fe_id):
        message = "Feedback event (id={}) is missing prediction.".format(fe_id)
        super(FeedbackEventMissingPrediction, self).__init__(message)


class MissingDependencyError(GantryException):
    """
    Raised when a dependency needed for a feature is not installed.
    """

    pass


class FeatureTypeInvalid(GantryException):
    def __init__(self, msg):
        super(FeatureTypeInvalid, self).__init__(msg)


class InvalidAttributeError(GantryException):
    """
    Raised when the attribute requested is invalid for a sketch.
    """

    def __init__(self, msg):
        super(InvalidAttributeError, self).__init__(msg)


class GantryAPIException(GantryException):
    """
    Base class for exceptions in the API
    """

    status_code = 400

    # Based on:
    # https://flask.palletsprojects.com/en/2.0.x/errorhandling/#returning-api-errors-as-json
    def __init__(self, msg, status_code: Optional[int] = None):
        """Optional status_code can be passed and it will be used
        by flask as HTTP response status code.
        """
        super().__init__(msg)
        if status_code is not None:
            self.status_code = status_code


class MissingQueryError(GantryAPIException):
    """
    Raised when a query is missing
    """

    pass


class QueryError(GantryAPIException):
    """
    Raised when a query doesn't have a result
    """

    pass


class InvalidVersionError(GantryAPIException):
    """
    Raised when the function version in the request is invalid
    """

    pass


class AuthenticationError(GantryAPIException):
    """
    Raised when the request does not have valid authentication
    """

    status_code = 401


class AccessDenied(GantryAPIException):
    """
    Raised when the user does not have access to the requested resource
    """

    status_code = 404


class GantryFilterException(GantryException):
    """
    Raised by the sdk when there is an exception to a filter
    """

    pass


class GantryDockerException(GantryException):
    """
    Raised by the Gantry Docker command when docker or docker-compose is not found
    """

    pass


class GantryDatabaseConnectionError(GantryException):
    """
    Raised when Gantry cannot connect to the database
    """

    pass


class ApplicationNotFoundException(GantryException):
    """Raised when an application is not found"""

    def __init__(
        self,
        application_node_id: Optional[uuid.UUID] = None,
        func_name: Optional[str] = None,
        version: Optional[int] = None,
    ):
        if application_node_id:
            message = "Could not find an application with application id: {}".format(
                application_node_id
            )
        elif func_name and version:
            message = (
                "Could not find an application with application name: {} and version: {}".format(
                    func_name, version
                )
            )
        else:
            message = "Unable to find that application"

        super(GantryException, self).__init__(message)


class ApplicationDisabledException(GantryException):
    """Raised when an application is disabled and the action cannot be performed"""

    pass


class GantryBatchCreationException(GantryException):
    """Raised when gantry failed to create batch"""

    pass
