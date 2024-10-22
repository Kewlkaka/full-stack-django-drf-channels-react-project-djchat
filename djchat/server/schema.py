# To describe different parameters that can be passed into the view, and then this additional information will be used in the frontend/swaggerUI so that we can interact with the view utilizing swaggerUI interface.

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from .serializer import ChannelSerializer, ServerSerializer

# reference to serverlist, a reference to the fact this is to extend in some metadata to describe the parameters that can be passed into this list here.
server_list_docs = extend_schema(
    responses=ServerSerializer(many=True),
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Category of Servers to Retrieve",
        ),
        OpenApiParameter(
            name="qty",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of Servers to Retrieve",
        ),
        OpenApiParameter(
            name="qty",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of Servers to Retrieve",
        ),
        OpenApiParameter(
            name="by_user",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter servers by current authenticated User (True/False)",
        ),
        OpenApiParameter(
            name="with_num_members",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Include number of members for each server in the response",
        ),
        OpenApiParameter(
            name="by_server_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Include server by id",
        ),
    ],
)
