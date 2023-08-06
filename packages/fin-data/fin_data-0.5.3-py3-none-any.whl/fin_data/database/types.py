from typing import TypeVar

# To be used as a type annotation on columns that should be used to create a hypertable partition.
HypertablePartition = TypeVar("HypertablePartition")

# To be used as a type annotation on the columns that should not be used in the generation of row data IDs.
DataIDIgnore = TypeVar("DataIDIgnore")
