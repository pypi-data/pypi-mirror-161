"""Client for basic usage"""

import logging
import os
from typing import AsyncGenerator, Optional, Type, TypeVar, Union, cast

from google.cloud.firestore import AsyncClient
from google.oauth2.service_account import Credentials

from frantic.base import BaseModel


ModelType = TypeVar("ModelType", bound=BaseModel)  # pylint: disable=invalid-name

logger = logging.getLogger(__name__)


def client_factory() -> AsyncClient:
    """Create a default client instance"""
    gappcreds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gappcreds is None:
        raise ValueError("No GOOGLE_APPLICATION_CREDENTIALS env was set")
    credentials = Credentials.from_service_account_file(gappcreds)
    return AsyncClient(credentials=credentials)


class Frantic:
    """Firestore with Pydantic models integration"""

    def __init__(self, *, client: Optional[AsyncClient] = None, prefix: Optional[str] = None):
        self.client = client or client_factory()
        self.prefix = (prefix or "").rstrip("/")

    def _get_path(self, model: Type[ModelType]) -> str:
        """Get collection path for a specified model"""
        colname = model.collection or model.__name__.lower()
        return f"{self.prefix}/{colname}"

    async def get(self, model: Type[ModelType], did: str) -> Optional[ModelType]:
        """Get a single document of a type {model} by its document id {did}

        Returns None if none found
        """
        collection_path = self._get_path(model)
        collection = self.client.collection(collection_path)
        docref = collection.document(document_id=did)
        document = await docref.get()
        if not document.exists:
            return None
        return model(**document.to_dict(), id=document.id)

    # TODO: Pagination
    async def list(self, model: Type[ModelType]) -> AsyncGenerator[ModelType, None]:
        """Iterate through all documents of a type {model}"""
        collection_path = self._get_path(model)
        collection = self.client.collection(collection_path)
        async for docref in collection.list_documents():
            document = await docref.get()
            yield model(**document.to_dict(), id=docref.id)

    async def add(self, instance: ModelType) -> ModelType:
        """Add instance as a document within corresponding collection"""
        collection_path = self._get_path(instance.__class__)
        collection = self.client.collection(collection_path)
        _, docref = await collection.add(instance.dict(exclude={"id"}))
        instance.id = docref.id
        return instance

    async def delete(self, model_or_instance: Union[Type[ModelType], ModelType], did: Optional[str] = None):
        """Delete a document specified by model type and document id {did}"""
        if isinstance(model_or_instance, BaseModel):
            if did:
                logger.warning(
                    "Document ID was provided even though an instance was provided as well. Using ID of the instance."
                )
            did = model_or_instance.id
            model = type(model_or_instance)
        else:
            model = cast(Type[BaseModel], model_or_instance)
        if did is None:
            raise ValueError(f"Cannot delete '{model.__name__}' without an id")
        collection_path = self._get_path(model)
        collection = self.client.collection(collection_path)
        docref = collection.document(did)
        await docref.delete()
