from django.db.models import Count
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response

from .models import Server
from .schema import server_list_docs
from .serializer import ServerSerializer


class ServerListViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling server-related API endpoints that provides flexible filtering
    and listing capabilities for Server objects.

    This ViewSet implements a single 'list' endpoint that supports multiple filtering options
    through query parameters, allowing for versatile server querying without requiring
    separate endpoints for each filtering scenario.

    Attributes:
        queryset: Base queryset containing all Server objects.

    Supported Query Parameters:
        category (str, optional):
            Filter servers by category name.
            Example: ?category=gaming

        qty (int, optional):
            Limit the number of returned servers.
            Example: ?qty=10

        by_user (bool, optional):
            If "true", returns only servers where the authenticated user is a member.
            Requires authentication.
            Example: ?by_user=true

        by_serverid (int, optional):
            Filter by a specific server ID.
            Example: ?by_serverid=123

        with_num_members (bool, optional):
            If "true", includes a count of members for each server in the response.
            Example: ?with_num_members=true

    Returns:
        REST framework Response containing serialized server data.
        The response format will be a list of server objects with their respective fields.

    Raises:
        AuthenticationFailed:
            When by_user=true is specified but the user is not authenticated.
        ValidationError:
            When by_serverid is specified but the server doesn't exist or the ID is invalid.

    Example Usage:
        # Get all servers in the 'gaming' category with member counts
        GET /api/servers/?category=gaming&with_num_members=true

        # Get first 5 servers that the authenticated user is a member of
        GET /api/servers/?by_user=true&qty=5

    Notes:
        - Multiple query parameters can be combined to create complex filters
        - The endpoint is optimized to handle multiple filtering scenarios efficiently
        - All filters are applied sequentially to the base queryset
        - The serializer handles the final formatting of the response data
    """

    queryset = Server.objects.all()

    @server_list_docs
    def list(self, request):
        """
        Handle GET requests for server listings with optional filtering.

        Args:
            request (Request): Django REST framework request object containing query parameters
                             for filtering and customizing the response.

        Returns:
            Response: Serialized server data based on applied filters
                     Format: [
                         {
                             "id": int,
                             "name": str,
                             "category": str,
                             "num_members": int (optional),
                             ...additional server fields
                         },
                         ...
                     ]

        Raises:
            AuthenticationFailed: If by_user=true and user is not authenticated
            ValidationError: If by_serverid is invalid or server doesn't exist
        """
        # Extract query parameters from the request
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        # Authentication check for user-specific queries
        # if by_user and not request.user.is_authenticated:
        # raise AuthenticationFailed()

        # Apply category filter if specified
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        # Filter by user membership if requested
        if by_user:
            if by_user and request.user.is_authenticated:
                # utilizing default session authentication setup in settings.py^^^
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()

        # Add member count annotation if requested
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        # Apply quantity limit if specified
        if qty:
            self.queryset = self.queryset[: int(qty)]

        # Filter by specific server ID if requested
        if by_serverid:
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                # Raise validation error if server doesn't exist
                if not self.queryset.exists():
                    raise ValidationError(
                        detail=f"Server with ID {by_serverid} does not exist"
                    )
            except ValueError:
                # Handle case where by_serverid is not a valid integer
                raise ValidationError(
                    detail=f"Server with ID {by_serverid} does not exist"
                )

        # Serialize the filtered queryset
        serializer = ServerSerializer(
            self.queryset, many=True, context={"num_members": with_num_members}
        )

        return Response(serializer.data)
