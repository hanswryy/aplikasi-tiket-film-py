from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        verify_jwt_in_request()
        if get_jwt().get("role") != "ADMIN":
            return jsonify(error="Admin access required"), 403
        return view(*args, **kwargs)

    return wrapped


def user_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        verify_jwt_in_request()
        if get_jwt().get("role") != "USER":
            return jsonify(error="User access required"), 403
        return view(*args, **kwargs)

    return wrapped
