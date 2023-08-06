def spawn_factory(on: str):
    if on == "mp":
        from .mp import spawn
    elif on == "docker":
        from .docker import spawn
    elif on == "k8s":
        from .k8s import spawn
    else:
        raise ValueError("unexpected platform")
    return spawn
