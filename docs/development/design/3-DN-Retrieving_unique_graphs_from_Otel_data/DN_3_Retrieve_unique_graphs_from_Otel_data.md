# Design Note 3: Retrieving unique graphs from OTel data

## Problem

Currently, OpenTelemetry (OTel) data is processed and stored in a SQLite database. The current method for evaluating and comparing graph structures derived from this data has limitations:

1. Relations between data points are formed and evaluated within the SQLite database.
2. Graph structures are compared by sorting them into alphanumerical order before equating them.
3. This approach is not 100% accurate, potentially leading to misidentification of unique graph structures.

The current implementation's inaccuracy may result in:

- False positives: Different graph structures being identified as the same
- False negatives: Identical graph structures being treated as different

## Solution

### Overview

An investigation into various methods for storing and analysing OTel data to find unique graphs was conducted, considering both graph and relational databases. The investigation found that SQLite, a relational serverless database, was significantly faster and more efficient in identifying unique graphs than Memgraph, a graph database.

### Proposed Approach

SQLite will be the primary database for storing and analysing OTel data in conjunction with SQLAlchemy. A detailed schema will be provided for the structure of the data, and an `IngestData` class will be used to load data into the SQLite database.

The proposed process for determining unique graphs involves the following steps:

- Initialisation: Initialise the SQLite database.
- Data Ingestion: Load OTel data into the SQLite database using the `IngestData` class.
- Identify Distinct Trace IDs: Identify distinct trace_ids.
- Batch Processing: Load batches of graphs based on trace_ids into memory.
- Hash Calculation: Calculate a unique graph hash for each graph and store the results in the database against their trace_id.
- Result Compilation: Once all batches are complete, identify unique graph hashes along with their corresponding trace_id.

### Classes and Functions

The following classes are required

```python
class OTelEvent(NamedTuple):
    """Named tuple for OTel Event"""
    job_name: str
    job_id: str
    event_type: str
    event_id: str
    start_timestamp: str
    end_timestamp: str
    application_name: str
    parent_event_id: Optional[str, None]
    child_event_ids: Optional[list[str], None]

class OTELDataSource(ABC):
    """Abstract class for returning a OTelEvent object from a data source."""
    
    def __iter__(self) -> Self:
        """Returns the iterator object.

        :return: The iterator object
        :rtype: `self`
        """
        pass

    @abstractmethod
    def __next__(self) -> OTelEvent:
        """Returns the next item in the sequence.
        
        :return: The next OTelEvent in the sequence
        :rtype: :class: `OTelEvent`
        """


class JSONDataSource(OTELDataSource):
    """A class to handle OTel Data in JSON format"""

    def __init__(self) -> None:
        """Constructor method."""
        super().__init__()
        self.current_file_index: int
        self.current_parser: Iterator[OTelEvent] | None
        self.dirpath : str
        self.filepath: str
        self.file_list: list[str]

    def __next__(self) -> OTelEvent:
        """Returns the next item in the sequence.
        
        :return: The next OTelEvent in the sequence
        :rtype: :class: `OTelEvent`
        """
    
    def parse_json_stream(self, filepath: str) -> Iterator[OTelEvent]:
        """Function that parses a json file, maps the json to the application
        structure through the config specified in the config.yaml file.
        ijson iteratively parses the json file so that large files can be
        processed.

        :param filepath: The path to the JSON file to parse
        :return: An iterator of tuples containing OTelEvent and header
        :rtype: `Iterator`[:class:`OTelEvent`]
        """
        pass

    def create_otel_object(self, record: dict[str, Any]) -> OTelEvent:
        """Creates an OTelEvent object from a JSON record.

        :return: OTelEvent object
        :rtype: :class:`OTelEvent`
        """
        pass

    def set_dirpath(self) -> str | None:
        """Set the directory path.

        :return: The directory path
        :rtype: `str`
        """
        pass

    def set_filepath(self) -> str | None:
        """Set the filepath.

        :return: The filepath
        :rtype: `str`
        """
        pass

    def get_file_list(self) -> list[str]:
        """Get a list of filepaths to process.

        :return: A list of filepaths.
        :rtype: `list`[`str`]
        """
        pass

    def process_record(self, record: dict[str, Any]) -> Iterator[OTelEvent]:
        """Process a single record and yield OTelEvent objects.

        :param record: The record to process
        :type record: `dict`[`str`,`Any`]
        :return: An iterator of tuples containing OTelEvent and header
        :rtype: `Iterator`[:class: `OTelEvent`]
        """

class DataHolder(ABC):
    """An abstract class to handle saving processed OTel data."""
    
    @abstractmethod
    def save_data(self, otel_event: OTelEvent) -> None:
        """Method for batching and saving OTel data.
        
        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass

    @abstractmethod
    def clean_up(self) -> None:
        """Abstract method for any clean up tasks."""

        pass
    
class SQLDataHolder(DataHolder):
    """A class to handle saving data in SQL databases using SQLAlchemy."""

    def __init__(self, config: SQLDataHolderConfig) -> None:
        """Constructor method.

        :param config: Configuration parameters.
        :type config: :class: `SQLDataHolderConfig`
        """
        self.node_models_to_save: list[NodeModel]
        self.node_relationships_to_save: list[dict[str, str]]
        self.batch_size: int
        self.engine: Engine
        self.session: Session
        self.base: Base
        self.create_db_tables()


    def create_db_tables(self) -> None:
        """Method to create the database tables based on the defined models."""
        pass
    
    def save_data(self, otel_event: OTelEvent) -> None:
        """Method for batching and saving OTel data to SQL database.
        
        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass

    def commit_batched_data_to_database(self) -> None:
        """Method to commit batched node models, and their relationships to
        a SQL database.
        """
        pass

    def batch_insert_node_models(self) -> None:
        """Method to batch insert NodeModel objects into database."""
        pass

    def batch_insert_node_associations(self) -> None:
        """Method to batch insert node associations into database."""
        pass

    def add_node_relations(self, otel_event: OTelEvent) -> None:
        """Method to add parent-child node relations.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        """
        pass

    def convert_otel_event_to_node_model(
        self, otel_event: OTelEvent
    ) -> NodeModel:
        """Method to convert an OTelEvent object to a NodeModel object.

        :param otel_event: An OTelEvent object
        :type otel_event: :class: `OTelEvent`
        :return: A NodeModel object
        :rtype: :class:`NodeModel`
        """
        pass

    def clean_up(self) -> None:
        """Method to save commit remaining items within the batch to the
        database.
        """

class NodeModel(Base):
    """SQLAlchemy model to represent a node in the database."""
    pass


class IngestData():
    def __init__(self, otel_data_source: OTELDataSource, data_holder: DataHolder) -> None:
        """Initialise IngestData class.

        :param otel_data_source: The class that returns an OTelEvent object
        "type otel_data_source: :class: `OTELDataSource`
        :param data_holder: The class that handles data source operations
        :type data_holder: `DataHolder`
        """
        pass

    def load_to_data_holder(self) -> None:
        """Sends data to DataHolder object"""
        pass
```
The following functions are required in the find_unique_graphs module:

```python
def get_time_window(time_buffer: int, sql_data_holder: SQLDataHolder) -> tuple[datetime.datetime, datetime.datetime]:
    """Queries the database for min and max datetime, returns a min and max datetime with time buffer added.
    
    :param time_buffer: The time buffer in minutes
    :type time_buffer: `int`
    :param sql_data_holder: The SQLDataHolder object
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: A tuple consisting of the min and max datetime adjusted by time_buffer minutes
    :rtype: `tuple`[`datetime.datetime`,`datetime.datetime`]
    """
    pass

def create_db_view_root_nodes_in_time_window(time_window: tuple[datetime.datetime, datetime.datetime], sql_data_holder: SQLDataHolder) -> None:
    """Creates a view within the database that holds root nodes that have a start_timestamp within the time window.
    
    ":param time_window: The time window in which to create the view for root nodes
    :type time_window: `tuple`[:class:`datetime.datetime`, :class:`datetime.datetime`]
    :param sql_data_holder: The SQLDataHolder object
    :type sql_data_holder: :class:`SQLDataHolder`
    """
    pass

def find_unique_graphs_sql(batch_size: int, sql_data_holder: SQLDataHolder) -> dict[str, set[str]]:
    """Main function to return unique graphs sorted by job_name within the database.
    
    :param batch_size: The number of items to query from the database at once
    :type batch_size: `int`
    :param sql_data_holder: The SQLDataHolder object
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: A dictionary mapping job_name to set of job_id representing unique graphs
    :rtype: `dict`[`str`,`set`[`str`]]
    """
    pass

def get_root_nodes(start_row: int, batch_size: int, sql_data_holder: SQLDataHolder) -> list[NodeModel]:
    """Function to return batch of root nodes from the database.
    
    :param start_row: The row in the database to get the first value from
    :type start_row: `int`
    :param batch_size: The number of rows to return from the database
    :type batch_size: `int`
    :param sql_data_holder: The SQLDataHolder object
    :type sql_data_holder: :class:`SQLDataHolder`
    :return: A batch of root nodes
    :rtype: `list`[:class: `NodeModel`]
    """
    pass

def compute_graph_hashes_for_batch(root_nodes: list[NodeModel]) -> None:
    """Function to calculate graph hashes for a batch of root nodes, commiting the results to the database.
    
    :param root_nodes: The batch of root node objects to calculate graph hashes for
    :type root_nodes: :class: `NodeModel`
    """
    pass

def get_batch_nodes(job_ids: set[str]) -> list[NodeModel]:
    """Function to return all nodes within the database that have a job_id within job_ids
    
    :param job_ids: A set of job_id to perform the database query against
    :type job_ids: `set`[`str`]
    :return: A list of NodeModel objects from the query result
    :rtype: `list`[:class:`NodeModel`]    
    """
    pass

def create_event_id_to_child_nodes_map(
    nodes: list[NodeModel],
) -> DefaultDict[str, list[NodeModel]]:
    """Create a mapping of node event IDs to their child NodeModels

    :param nodes: List of NodeModel objects to process
    :type nodes: `list`[:class:`NodeModel`]
    :return: Mapping of node span IDs to their children
    :rtype: `DefaultDict`[`str`, `list`[:class:`NodeModel`]]
    """
    pass

def compute_graph_hash_recursive(root_node: NodeModel, event_id_to_child_node_map: DefaultDict[str, list[NodeModel]]) -> str:
    """Recursive function to calculate the unique hash of a graph based on each node's event_type attribute.
    
    :param root_node: The root node of the graph that the calculation is performed against
    :type root_node: :class: `NodeModel`
    :param event_id_to_child_node_map: A dictionary mapping event_id to their child nodes
    :type event_id_to_child_node_map: `DefaultDict`[`str`, `list`[:class:`NodeModel`]]
    :return: The graph hash
    :rtype: `str`
    """
    pass
```
A yaml config file will be provided:
```yaml
data_sources:
  json:
    type: JSONDataSource
    dirpath: /path/to/your/json/directory

data_holders:
  sql:
    type: SQLDataHolder
    db_uri: sqlite:///graph_database.db
    batch_size: 100
    time_buffer: 15 # minutes

ingest_data:
  data_source: json
  data_holder: sql
```