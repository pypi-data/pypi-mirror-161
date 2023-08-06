from typing import Type, Dict, List, Any, TypeVar, Generic
from uuid import UUID

from pymongo import ReturnDocument

from deci_common.abstractions.base_model import DBSchema
from deci_common.data_connection.mongo_db_connector import MongoDBConfiguration, MongoDBConnector
from deci_common.abstractions.abstract_logger import ILogger


T = TypeVar("T", bound=DBSchema)


class DBInterface(Generic[T], ILogger):
    def __init__(self, element_type: Type[T], mongo_db_configuration: Type[MongoDBConfiguration]):
        super().__init__()
        self._element_type = element_type
        self._db_connector = MongoDBConnector(mongo_db_configuration)

    def insert(self, element: T) -> T:
        """
        Insert an element to the DB and return it
        @param element: The element to insert
        @return: T
        """
        with self._db_connector as db:
            db._insert_document(element.dict())
        return element

    def find(self, search_filter: Dict[str, Any] = {}) -> List[T]:
        """
        Find all elements from DB with a specified search filter
        @param search_filter: Filter for the search
        @return: List[T]
        """
        with self._db_connector as db:
            elements = db._get_documents(search_filter=search_filter)

        return [self._element_type(**element) for element in elements]

    def update(self, element: T) -> T:
        """
        Updates an element in the DB using its id
        @param element: The element to update to (id is used to find the element to update)
        @return: T
        """
        with self._db_connector as db:
            updated_element = db._update_and_return_document(
                search_filter={"id": element.id}, updated_document=element.dict(), return_document=ReturnDocument.AFTER
            )
        return self._element_type(**updated_element)

    def update_many(self, updated_document: Dict[str, Any], search_filter: Dict[str, Any] = {}) -> List[T]:
        """
        Updates multiple elements in the DB using the specified search filter
        :param updated_document: the new values to set for the documents
        :param search_filter: documents to update values for
        :return: List[T]
        """
        with self._db_connector as db:
            elements = db._update_many_and_return_documents(
                search_filter=search_filter, updated_document=updated_document
            )
        return [self._element_type(**element) for element in elements]

    def delete(self, id: UUID, force: bool = False) -> bool:
        """
        Deletes an element from the DB
        @param id: The ID of the element to delete
        @param force: if True, permanently delete the element from the DB, otherwise - just mark it as deleted
        @return: True on success, False otherwise
        """
        with self._db_connector as db:
            if force:
                delete_result = db._delete_document(search_filter={"id": id})
                return delete_result.deleted_count == 1
            updated_element = db._update_and_return_document(
                search_filter={"id": id}, updated_document={"deleted": True}, return_document=ReturnDocument.AFTER
            )
            return updated_element["deleted"]
