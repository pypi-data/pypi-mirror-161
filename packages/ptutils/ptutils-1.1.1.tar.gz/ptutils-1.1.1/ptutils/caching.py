#!/bin/false
# -*- coding: utf-8 -*-

"""
A collection of functions for working with regular expressions.
"""
# =======================================================================================================================
# imports
# =======================================================================================================================
import datetime
from typing import Any, Callable, Optional, Tuple, Union, Generator
from ptutils.time import now
from ptutils.undefined import UNDEFINED, default_if_undefined, is_defined
from ptutils.typing import MutableMapping


# =======================================================================================================================
# class: CacheEntry
# =======================================================================================================================
class CacheEntry:
    def __init__(
        self,
        value:    Optional[Any] = None,
        created:  Optional[Any] = None,
        modified: Optional[Any] = None
    ):
        NOW = now()
        self.value    = value
        self.created  = NOW          if created  is None else created
        self.modified = self.created if modified is None else modified

    @property
    def age(self) -> datetime.timedelta:
        return now() - self.modified


# =======================================================================================================================
# class: Cache
# =======================================================================================================================
class Cache:
    """
    A mapping-backed key/value cache with TTL and validation control with options for default/creation on cache miss.
    """

    # -------------------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        store:    MutableMapping,
        default:  Optional[ Any ]                                   = UNDEFINED,
        create:   Optional[ Callable[ [], Any ] ]                   = UNDEFINED,
        max_age:  Optional[ Union[float, int, datetime.timedelta] ] = UNDEFINED,
        validate: Optional[ Callable[ [str, Any], bool ] ]          = UNDEFINED
    ):
        """
        Create a new mapping-backed cache.

        Parameters
        ----------
        store : MutableMapping
            The mapping providing key/value storage.
        default : Optional[ Any ], optional
            A default value to use if `name` is not already in the cache, by default `UNDEFINED`.
        create : Optional[ Callable[ [], Any ] ], optional
            A method to create a default value to use if `name` is not already in the cache, by default `UNDEFINED`.
            This method is only called if `default` is `UNDEFINED`.
        max_age : Optional[ Union[float, int, datetime.timedelta] ], optional
            The maximum allowed age of any retrieved value, by default `UNDEFINED`.
        validate : Optional[ Callable[ [str, Any], bool ] ], optional
            A method to validate any cached value, by default `UNDEFINED`. This is a function taking the name
            and stored value and which returns True if the value is considered valid, False if the stored value
            should be discarded.
        """

        self.store    = store
        self.default  = default
        self.create   = create
        self.max_age  = max_age
        self.validate = validate
        if is_defined(max_age):
            if isinstance(max_age, datetime.timedelta):
                self.max_age = max_age
            else:
                self.max_age = datetime.timedelta( seconds = max_age )
        else:
            self.max_age = UNDEFINED

    # -------------------------------------------------------------------------------------------------------------------
    def clear(self) -> None:
        """
        Clear all cache contents.
        """
        self.store.clear()

    # -------------------------------------------------------------------------------------------------------------------
    def get_entry(
        self,
        name:      str,
        default:   Optional[ Any ]                                    = UNDEFINED,
        create:    Optional[ Callable[ [], Any ] ]                    = UNDEFINED,
        max_age:   Optional[ Union[float, int, datetime.timedelta] ]  = UNDEFINED,
        validate:  Optional[ Callable[ [str, Any], bool ] ]           = UNDEFINED
    ) -> CacheEntry:
        """
        Get the named cache entry.

        Parameters
        ----------
        name : str
            The name of the entry.
        default : Optional[ Any ], optional
            A default value to use if `name` is not already in the cache, by default `UNDEFINED`.
        create : Optional[ Callable[ [], Any ] ], optional
            A method to create a default value to use if `name` is not already in the cache, by default `UNDEFINED`.
            This method is only called if `default` is `UNDEFINED`.
        max_age : Optional[ Union[float, int, datetime.timedelta] ], optional
            The maximum allowed age of any retrieved value, by default `UNDEFINED`.
        validate : Optional[ Callable[ [str, Any], bool ] ], optional
            A method to validate any cached value, by default `UNDEFINED`. This is a function taking the name
            and stored value and which returns True if the value is considered valid, False if the stored value
            should be discarded.

        Returns
        -------
        CacheEntry
            The cache entry containing the stored or newly-created value.
        """
        try:
            entry = self.store[ name ]

            # validate entry age (if requested)
            max_age = default_if_undefined(max_age, self.max_age)
            if is_defined(max_age):
                if not isinstance(max_age, datetime.timedelta):
                    max_age = datetime.timedelta( seconds = max_age )
                age = entry.age
                if age > max_age:
                    del self.store[ name ]
                    raise KeyError( name )

            # validate entry age (if requested)
            validate = default_if_undefined(validate, self.validate)
            if is_defined(validate):
                if not validate(name, entry.value):
                    raise KeyError( name )

            return entry

        except KeyError:
            pass

        default = default_if_undefined(default, self.default)
        create  = default_if_undefined(create, self.create)
        if is_defined(default):
            new_value = default

        elif is_defined(create):
            new_value = create()

        else:
            raise KeyError(f"Cache entry '{name}' does not exist, and no default or creation method were provided.")

        entry = CacheEntry( value = new_value )
        self.store[ name ] = entry
        return entry

    # -------------------------------------------------------------------------------------------------------------------
    def set_entry(
        self,
        name:    str,
        value:   Any
    ) -> CacheEntry:
        """
        Set or update the value of the named cache entry.

        Parameters
        ----------
        name : str
            The name of the entry.
        value : Any
            The new value.

        Returns
        -------
        CacheEntry
            The named cache entry containing the new value.
        """
        # try to get the entry
        try:
            entry = self.get_entry(name = name)
        except Exception:
            entry = UNDEFINED

        # update modified time or create new entry
        if is_defined(entry):
            entry.value      = value
            entry.modified   = now()
        else:
            entry = CacheEntry(value)

        # save the entry in the store
        self.store[name] = entry

        # return the entry
        return entry

    # -------------------------------------------------------------------------------------------------------------------
    def remove_entry( self, name: str ) -> CacheEntry:
        """
        Remove the named cache entry.

        Parameters
        ----------
        name : str
            The entry name.

        Returns
        -------
        CacheEntry
            The entry that was removed
        """
        entry = self.get_entry( name=name )
        del self.store[name]
        return entry

    # -------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, name: str) -> Any:
        """
        Get value of cache entry corresponding to the supplied `name`.

        Parameters
        ----------
        name : str
            The name of the entry.

        Returns
        -------
        Any
            The value.

        Raises
        ------
        KeyError
            When the item does not exist or is expired (and no default/creation logic is defined).
        """
        return self.get_entry(name = name).value

    # -------------------------------------------------------------------------------------------------------------------
    def __setitem__(self, name: str, value: Any) -> None:
        """
        Set the value of the cache entry corresponding to `name`.

        Parameters
        ----------
        name : str
            The name.
        value : Any
            The new value.
        """
        self.set_entry(name, value)

    # -------------------------------------------------------------------------------------------------------------------
    def __delitem__(self, name: str) -> None:
        """
        Remove the cache entry corresponding to the supplied `name`.

        Parameters
        ----------
        name : str
            The name.

        Raises
        ------
        KeyError
            When no such entry exists.
        """
        self.remove_entry(name=name)

    # -------------------------------------------------------------------------------------------------------------------
    def __iter__(self) -> Generator[str, None, None]:
        """
        Iterate over names of entries in the cache.

        Yields
        ------
        str
            The names of the entry.
        """
        for k, _ in self.items():
            yield k

    # -------------------------------------------------------------------------------------------------------------------
    def __len__(self) -> int:
        """
        Return the count of items in the store.

        Returns
        -------
        int
            The count of files in the backing directory which match the naming pattern.
        """
        return len( list( iter(self) ) )

    # -------------------------------------------------------------------------------------------------------------------
    def entry_items(self) -> Generator[ Tuple[str, CacheEntry], None, None ]:
        """
        Iterator over key-entry pairs. This method will exclude pairs where the entry is
        expired or fails validation, but not remove them from the store.

        Yields
        ------
        Tuple[str, CacheEntry]
            key-entry pairs.
        """
        for name, entry in self.store.items():
            # validate entry age (if requested)
            max_age = self.max_age
            if is_defined(max_age):
                if entry.age > self.max_age:
                    continue

            # validate entry (if requested)
            if is_defined(self.validate):
                if not self.validate(name, entry.value):
                    continue

            yield (name, entry)

    # -------------------------------------------------------------------------------------------------------------------
    def items(self) -> Generator[ Tuple[str, Any], None, None ]:
        """
        Iterator over key-value pairs. This method will exclude pairs where the entry is
        expired or fails validation, but not remove them from the store.

        Yields
        ------
        Tuple[str, Any]
            key-value pairs.
        """
        for name, entry in self.entry_items():
            yield (name, entry.value)

    # -------------------------------------------------------------------------------------------------------------------
    def pop( self, name: str ) -> Any:
        """
        Pop the named value from the cache.

        Parameters
        ----------
        name : str
            The name of the enrtry/value.

        Returns
        -------
        CacheEntry
            The value cache entry corresponding to `name` that was removed from the cache.
        """
        return self.remove_entry(name).value
