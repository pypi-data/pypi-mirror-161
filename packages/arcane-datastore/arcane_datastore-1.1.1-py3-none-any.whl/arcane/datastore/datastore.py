from typing import Union, List, Dict, Any

import backoff

from google.cloud.datastore import Client as GoogleDatastoreClient, Entity, Key
from google.cloud import exceptions

from arcane.core.exceptions import GOOGLE_EXCEPTIONS_TO_RETRY

BATCH_MAX_NUMBER = 500


class Client(GoogleDatastoreClient):
    def __init__(self, project=None, credentials=None, _http=None):
        super().__init__(project=project, credentials=credentials, _http=_http)

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def get_entity(self, kind: str, entity_id: Union[int, str]) -> Union[Entity, None]:
        return self.get(self.key(kind, entity_id))

    def batch_allocate_keys(self, base_key: Key, nb_required_ids: int) -> List[Key]:
        """ key creation by slicing entities required ids by BATCH_MAX_NUMBER """
        all_keys = []
        for number_of_indexes in range(0, nb_required_ids, BATCH_MAX_NUMBER):
            all_keys.extend(self.allocate_ids(base_key,
                                              min(BATCH_MAX_NUMBER,
                                                  nb_required_ids - number_of_indexes)))
        return all_keys

    def batch_put(self, entities: List[Entity]) -> None:
        """
        performs datastore put by slicing entities list by BATCH_MAX_NUMBER
        """
        if not entities:
            return
        for entity_index in range(0, len(entities), BATCH_MAX_NUMBER):
            self.put_multi((entities[entity_index: min(entity_index + BATCH_MAX_NUMBER, len(entities))]))

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def put(self, entity: Entity) -> None:
        super().put(entity)

    def batch_delete(self, keys: List[Key]) -> None:
        """ performs datastore delete by slicing entities list by BATCH_MAX_NUMBER  """
        if not keys:
            return
        for entity_index in range(0, len(keys), BATCH_MAX_NUMBER):
            self.delete_multi(keys[entity_index: min(entity_index + BATCH_MAX_NUMBER, len(keys))])

    def clear_kind(self, kind: str) -> int:
        """ deletes all entities with the appropriate kind and reports on the number of deletion """
        query = self.query()
        query.kind = kind
        query.keys_only()
        keys = [entity.key for entity in query.fetch()]
        deletion_number = len(keys)
        self.batch_delete(keys)
        return deletion_number

    @staticmethod
    def convert_entity_to_dict(input_data: Union[Entity, List, Any]) -> Union[Dict[str, Any], List, Any]:
        """ Convert recursively a datastore entity to dict """
        if isinstance(input_data, Entity) or isinstance(input_data, dict):
            return {index: Client.convert_entity_to_dict(value) for index, value in input_data.items()}
        elif isinstance(input_data, list) or isinstance(input_data, tuple):
            return [Client.convert_entity_to_dict(elem) for elem in input_data]
        else:
            return input_data

    @staticmethod
    def convert_input_to_excluded_entity(input_data: Union[Dict, List, Any]) -> Union[Entity, List, Any]:
        """ Convert recursively a dict to an excluded entity"""
        if isinstance(input_data, Dict) or isinstance(input_data, dict):
            entity = Entity(exclude_from_indexes=tuple(input_data.keys()))
            entity.update({index: Client.convert_input_to_excluded_entity(value) for index, value in input_data.items()})
            return entity
        elif isinstance(input_data, list) or isinstance(input_data, tuple):
            return [Client.convert_input_to_excluded_entity(elem) for elem in input_data]
        else:
            return input_data

    @staticmethod
    def update_entity(entity_to_update: Entity, input_data: Union[Dict, Entity], read_only_attributes: List[str] = []) -> Entity:
        """ Update an entity preserving the read only attributes """
        for field in read_only_attributes:
            input_data.pop(field, None)
        entity_to_update.update(input_data)
        return entity_to_update

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def save_entity_with_transactions(self, entity_id: Union[int, str], updated_properties: Dict, kind: str) -> None:
        """Update an entity while ensuring atomicity"""
        for _ in range(5):
            try:
                with self.transaction():
                    entity_to_update = self.get(self.key(kind, entity_id))
                    if entity_to_update is not None:
                        entity_to_update.update(updated_properties)
                        self.put(entity_to_update)
                        break
            except exceptions.Conflict:
                continue

        else:
            print(f"Transaction failed for entity {entity_id}")

    def update_entity_execution_info(self, kind: str, entity: Entity, status: str, errors=[]):
        """Update an entity execution info status and errors. Usefull for SmartFeeds components."""
        entity_id = entity['id']
        updated_properties = {
            'execution_info': entity.get('execution_info', {})}

        updated_properties['execution_info']['errors'] = errors
        updated_properties['execution_info']['status'] = status
        updated_properties['execution_info'] = self.convert_input_to_excluded_entity(
            updated_properties['execution_info'])

        self.save_entity_with_transactions(
            entity_id, updated_properties, kind)
