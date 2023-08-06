"""Declares :class:`MessagePublished`."""
import pydantic

from .pubsubmessage import PubsubMessage

SUBSCRIPTION_NAME = pydantic.constr(
    regex='^projects/[\-a-z0-9]{6,30}/subscriptions/.*$'
)

class MessagePublished(pydantic.BaseModel):
    """A datastructure containing a message that was published to a Google Pub/Sub
    topic and received by the server through a subscription.
    """
    subscription: SUBSCRIPTION_NAME = pydantic.Field(
        default=...,
        title="Subscription",
        description=(
            "The subscription through which the message was delivered to the "
            "endpoint."
        ),
        example="projects/myproject/subscriptions/mysub"
    )

    message: PubsubMessage
