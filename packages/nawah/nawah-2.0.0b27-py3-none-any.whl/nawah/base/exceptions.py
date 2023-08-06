"""Provides Exception classes for Base Functions"""

# START: Shared exceptions
class UtilityModuleDataCallException(Exception):
    """Raised if a data call was made for a Utility Module"""

    status = 400

    def __init__(self, *, module_name, func_name):
        super().__init__(
            f"Nawah Function '{func_name}' can't be called on Nawah Utility module "
            f"'{module_name}'"
        )


class DuplicateUniqueException(Exception):
    """Raised if 'create', 'update' call has at least one 'unique_attr' value in 'doc'
    that matches another doc"""

    status = 400

    def __init__(self, *, unique_attrs):
        super().__init__(
            f"A doc matching at least one of '{unique_attrs}' already exists"
        )


class InvalidDocException(Exception):
    """Raised if 'delete_file', 'retrieve_file' call 'query' does not return any doc"""

    status = 400

    def __init__(self, *, doc_id):
        super().__init__(f"Query for doc with '_id' '{doc_id}' returned no results")


# END: Shared exceptions

# START: create exceptions
class NoDocCreatedException(Exception):
    """Raised if 'create' call creates no doc"""

    status = 400

    def __init__(self, *, module_name):
        super().__init__(f"No documents were created for module '{module_name}'")


# END: create exceptions

# START: delete exceptions
class NoDocDeletedException(Exception):
    """Raised if 'delete' call deletes no doc"""

    status = 400

    def __init__(self, *, module_name):
        super().__init__(f"No documents were deleted for module '{module_name}'")


# END: delete exceptions

# START: read exceptions
class NoDocFoundException(Exception):
    """Raised if 'read' call founds no doc"""

    status = 400

    def __init__(self, *, module_name):
        super().__init__(f"No documents were found for module '{module_name}'")


# END: read exceptions

# START: delete_file exceptions
class InvalidDeleteFileDocAttrException(Exception):
    """Raised if 'delete_file' call 'query' returns doc with attr not valid for operation"""

    status = 400

    def __init__(self, *, doc_id, attr_name):
        super().__init__(
            f"Query for doc with '_id' '{doc_id}' returned doc with invalid value for attr "
            f"'{attr_name}'"
        )


class InvalidDeleteFileIndexException(Exception):
    """Raised if 'delete_file' call 'query' returns doc with index for call not valid for
    operation"""

    status = 400

    def __init__(self, *, doc_id, attr_name, index):
        super().__init__(
            f"Index '{index}' for attr '{attr_name}' for doc with '_id' '{doc_id}' is invalid"
        )


class InvalidDeleteFileIndexValueException(Exception):
    """Raised if 'delete_file' call 'query' returns doc with index value for call not valid for
    operation"""

    status = 400

    def __init__(self, *, doc_id, attr_name, index, index_val_type):
        super().__init__(
            f"Index '{index}' for attr '{attr_name}' for doc with '_id' '{doc_id}' is of invalid "
            f"type '{index_val_type}'"
        )


class InvalidDeleteFileMismatchNameException(Exception):
    """Raised if 'delete_file' call 'query' returns doc with index value file name not matching
    'query'"""

    status = 400

    def __init__(self, *, doc_id, attr_name, index, query_file_name, index_file_name):
        super().__init__(
            f"Index '{index}' for attr '{attr_name}' for doc with '_id' '{doc_id}' is for file "
            f"'{index_file_name}', not '{query_file_name}'"
        )


# END: delete_file exceptions

# START: obtain_lock exceptions
class FailedObtainLockException(Exception):
    """Raised if 'obtain_lock' call failed to obtain lock"""

    status = 400

    def __init__(self, *, module_name):
        super().__init__(f"Failed to obtain lock for '{module_name}'")


# END: obtain_lock exceptions

# START: delete_lock exceptions
class FailedDeleteLockException(Exception):
    """Raised if 'obtain_lock','delete_lock' call failed to deleted obtaiend lock"""

    status = 500

    def __init__(self, *, module_name, lock_id):
        super().__init__(
            f"Failed to delete lock '{lock_id}' for '{module_name}'. Delete manually now"
        )


# END: delete_lock exceptions

# START: update exceptions
class UpdateMultiUniqueException(Exception):
    """Raised if 'update' call is attempted on multiple docs
    where at least one 'unique_attr' is present in 'update_doc'"""

    status = 400

    def __init__(self):
        super().__init__(
            "Update call query has more than one doc as results. This would result in"
            "duplication"
        )


class EmptyUpdateDocException(Exception):
    """Raised if 'update' call has empty \'doc\'"""

    status = 400

    def __init__(self, *, module_name):
        super().__init__(f"Update 'doc' is empty for module '{module_name}'")


class NoDocUpdatedException(Exception):
    """Raised if 'update' call updates no doc"""

    status = 400

    def __init__(self, *, module_name):
        super().__init__(f"No documents were updated for module '{module_name}'")


# END: update exceptions

# START: retrieve_file exceptions
class FileNotFoundException(Exception):
    """Raised by 'retrieve_file' if failed to locate attr, or attr does not match requested file
    name"""

    status = 400

    def __init__(self, *, doc_id, attr_name, file_name):
        super().__init__(
            f"Failed to find file for doc '_id' '{doc_id}', attr '{attr_name}', file '{file_name}'"
        )


class FileNotImageException(Exception):
    """Raised by 'retrieve_file' if attemtped to generate thumbnail of non-image file"""

    status = 400

    def __init__(self, *, doc_id, attr_name, file_name, file_type):
        super().__init__(
            f"Can't generate thumbnail for file for doc '_id' '{doc_id}', attr '{attr_name}', file "
            f"'{file_name}', of type '{file_type}'"
        )


# END: retrieve_file exceptions
