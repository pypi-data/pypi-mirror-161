class UnexpectedCypherQueryTypeException(Exception):
    """
    Raised when the query type (node, path or edge) is not the expected one
    """


class InvalidEdgeIdException(Exception):
    """
    Raised for invalid edge id formats
    """


class InvalidRelationshipsDirectionsException(Exception):
    """
    Raised when fetching for relationships using invalid inbound/outbound directions
    """
