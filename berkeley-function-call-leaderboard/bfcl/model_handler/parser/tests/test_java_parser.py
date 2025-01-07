import unittest
from typing import Any

from bfcl.model_handler.parser.java_parser import parse_java_function_call


class TestJavaParser(unittest.TestCase):

    def test_hash_map_anonymous_inner_class(self):
        node: Any = parse_java_function_call(
            'SQLCompletionAnalyzer.makeProposalsFromObject(object="Customers", useShortName="true", params=new HashMap<>() {{ put("limit", "50"); put("schemaFilter", "public"); }})'
        )
        self.assertEqual(
            [
                {
                    "SQLCompletionAnalyzer.makeProposalsFromObject": {
                        "object": "Customers",

                        # "true" is a string literal here after conversion,
                        # irrespective of whether the model uses
                        # `useShortName=true` or `useShortName="true"`. This
                        # will fail the type check, but let's ignore this and
                        # focus on the hash map below for now.
                        "useShortName": "true",

                        # There is no logic in `java_parser` to handle the
                        # legacy anonymous inner class syntax and convert it
                        # to a Python hash map. This argument is instead
                        # handled by the generic `"object_creation_expression"`
                        # branch in `java_parser`. Models can try to use a
                        # string representation like
                        # "{'limit': '50', 'schemaFilter': 'public'}" (see
                        # `test_hash_map_string` below). I would argue this is
                        # what the prompt actually indicates, but this will just
                        # fail the type check later on.
                        "params": "new HashMap<>()",
                    }
                }
            ],
            node,
        )

    def test_hash_map_string(self):
        node: Any = parse_java_function_call(
            "SQLCompletionAnalyzer.makeProposalsFromObject(object=\"Customers\", useShortName=true, params=\"{'limit': '50', 'schemaFilter': 'public'}\")"
        )
        self.assertEqual(
            [
                {
                    "SQLCompletionAnalyzer.makeProposalsFromObject": {
                        "object": "Customers",
                        "useShortName": "true",

                        # Most models will choose to do this (I would too, given
                        # the prompt), but this will just fail the type check
                        # later on. This is probably easier to parse in
                        # treesitter, if we know what the type of `params`
                        # should be.
                        "params": "{'limit': '50', 'schemaFilter': 'public'}",
                    }
                }
            ],
            node,
        )
