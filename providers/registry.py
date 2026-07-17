_PROVIDER_REGISTRY: dict[str, type] = {}


def register_provider(name: str, cls: type) -> None:
    _PROVIDER_REGISTRY[name] = cls


def get_provider_class(name: str) -> type:
    cls = _PROVIDER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown provider '{name}'. Available: {list(_PROVIDER_REGISTRY.keys())}"
        )
    return cls


def list_providers() -> list[str]:
    return list(_PROVIDER_REGISTRY.keys())
