from typing import Optional, List, Any, Dict, Callable, Union, Iterable
from cykhash import Int64Set

from operator import itemgetter
from hashbox.utils import validate_query
from hashbox.mutable.mutable_attr import MutableFieldIndex


class HashBox:
    def __init__(
        self,
        objs: Optional[Iterable[Any]] = None,
        on: Iterable[Union[str, Callable]] = None,
    ):
        if not on:
            raise ValueError("Need at least one field to index on.")
        if objs:
            self.obj_map = {id(obj): obj for obj in objs}
        else:
            self.obj_map = dict()

        # Make an index for each field.
        self.indices = {}
        for field in on:
            self.indices[field] = MutableFieldIndex(field, self.obj_map, objs)

    def find(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> List:
        hits = self._find_ids(match, exclude)
        # itemgetter is about 10% faster than doing a comprehension like [self.objs[ptr] for ptr in hits]
        if len(hits) == 0:
            return []
        elif len(hits) == 1:
            return [
                itemgetter(*hits)(self.obj_map)
            ]  # itemgetter returns a single item here, not in a collection
        else:
            return list(
                itemgetter(*hits)(self.obj_map)
            )  # itemgetter returns a tuple of items here, so make it a list

    def _find_ids(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> Int64Set:
        """
        Perform lookup based on given values. Return a set of object IDs matching constraints.

        If "having" is None / empty, it matches all objects.
        There is an implicit "AND" joining all constraints.
        """
        validate_query(self.indices, match, exclude)

        # perform 'match' query
        hits = None
        if match:
            # find intersection of each field
            for field, value in match.items():
                # if multiple values for a field, find each value and union those first
                field_hits = self._match_any_of(field, value)
                if hits is None:  # first field
                    hits = field_hits
                if field_hits:
                    # intersect this field's hits with our hits so far
                    # intersecting from the smaller set is faster in cykhash sets
                    if len(hits) < len(field_hits):
                        hits = hits.intersection(field_hits)
                    else:
                        hits = field_hits.intersection(hits)
                else:
                    # this field had no matches, therefore the intersection will be empty. We can stop here.
                    return Int64Set()
        else:
            # 'match' is unspecified, so match all objects
            hits = Int64Set(self.obj_map.keys())

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                hits = Int64Set.difference(hits, field_hits)
                if len(hits) == 0:
                    break

        return hits

    def add(self, obj):
        """Add a new object, evaluating any attributes and storing the results."""
        ptr = id(obj)
        self.obj_map[ptr] = obj
        for field in self.indices:
            self.indices[field].add(ptr, obj)

    def remove(self, obj):
        """Remove an object."""
        ptr = id(obj)
        if ptr not in self.obj_map:
            raise KeyError

        for field in self.indices:
            self.indices[field].remove(ptr, obj)
        del self.obj_map[ptr]

    def _match_any_of(self, field: str, value: Any):
        """Get matches for a single field during a find(). If multiple values specified, handle union logic."""
        if isinstance(value, list):
            # take the union of all matches
            matches = Int64Set()
            for v in value:
                v_matches = self.indices[field].get_obj_ids(v)
                # union with the larger set on the left is faster in cykhash
                if len(matches) > len(v_matches):
                    matches = matches.union(v_matches)
                else:
                    matches = v_matches.union(matches)
        else:
            matches = self.indices[field].get_obj_ids(value)
        return matches

    def __contains__(self, obj):
        return id(obj) in self.obj_map

    def __iter__(self):
        return iter(self.obj_map.values())

    def __len__(self):
        return len(self.obj_map)
