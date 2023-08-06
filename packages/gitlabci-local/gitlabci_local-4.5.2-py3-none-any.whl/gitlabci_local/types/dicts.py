#!/usr/bin/env python3

# Standard libraries
from re import findall, match

# Dicts class, pylint: disable=too-few-public-methods
class Dicts:

    # Finder
    @staticmethod
    def find(data, path):

        # Variables
        queries = path.split('.')
        result = data if queries else None

        # Iterate through queries
        for query in queries:

            # Parse query to key and index
            matches = match(r'([^\[]*)(\[.*\])*', query).groups()
            if matches[0] and matches[1]:
                key = matches[0]
                indexes = [int(value) for value in findall(r'\[(-?\d+)\]*', matches[1])]
            else:
                key = query
                indexes = []

            # Extract key
            if key and result:
                result = result.get(key, None)

            # Extract index
            for index in indexes:
                if result and -len(result) <= index < len(result):
                    result = result[index]
                else:
                    result = None

            # Empty node
            if not result:
                break

        # Result
        return result
