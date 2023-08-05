import json
from typing import Optional

from graphql_jwt.shortcuts import get_token


class GraphQLMixin:
    def execute(
        self,
        query: str,
        variables: Optional[dict] = None,
        as_user: Optional = None,
        files: Optional[dict] = None,
        extra_token_data: Optional[dict] = None,
    ):
        headers = {}
        if as_user:
            if extra_token_data is None:
                extra_token_data = {}
            headers[
                "HTTP_AUTHORIZATION"
            ] = f"JWT {get_token(as_user, **extra_token_data)}"

        data = {
            "operations": json.dumps({"query": query, "variables": variables or {}})
        }
        if files:
            mapping = {i: [k] for i, k in enumerate(files.keys())}
            data["map"] = json.dumps(mapping)
            for i, keys in mapping.items():
                data[i] = files[keys[0]]
                if hasattr(data[i], "seek"):
                    data[i].seek(0)

        return self.client.post("/graphql", data=data, **headers)
