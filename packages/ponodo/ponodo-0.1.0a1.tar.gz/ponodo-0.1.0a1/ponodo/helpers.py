def import_class(cls: str):
    import importlib

    module_path = ".".join(cls.split(".")[:-1])
    klass = cls.split(".")[-1:][0]
    module = importlib.import_module(module_path)
    return getattr(module, klass)


def debug(*, header="", compile_flags=None, **kwargs):

    import sys

    from IPython import InteractiveShell
    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.terminal.ipapp import load_default_config

    config = kwargs.get("config")
    if config is None:
        config = load_default_config()
        config.InteractiveShellEmbed = config.TerminalInteractiveShell
        kwargs["config"] = config
    using = kwargs.get("using", "sync")
    if using:
        kwargs["config"].update(
            {
                "TerminalInteractiveShell": {
                    "loop_runner": using,
                    "colors": "NoColor",
                    "autoawait": using != "sync",
                }
            }
        )
    # save ps1/ps2 if defined
    ps1 = None
    ps2 = None
    try:
        ps1 = sys.ps1
        ps2 = sys.ps2
    except AttributeError:
        pass
    # save previous instance
    saved_shell_instance = InteractiveShell._instance
    if saved_shell_instance is not None:
        cls = type(saved_shell_instance)
        cls.clear_instance()
    frame = sys._getframe(1)
    shell = InteractiveShellEmbed.instance(
        _init_location_id="{}:{}".format(frame.f_code.co_filename, frame.f_lineno),
        colors="neutral",
        **kwargs
    )
    shell(
        header=header,
        stack_depth=2,
        compile_flags=compile_flags,
        _call_location_id="{}:{}".format(frame.f_code.co_filename, frame.f_lineno),
    )
    InteractiveShellEmbed.clear_instance()
    # restore previous instance
    if saved_shell_instance is not None:
        cls = type(saved_shell_instance)
        cls.clear_instance()
        for subclass in cls._walk_mro():
            subclass._instance = saved_shell_instance
    if ps1 is not None:
        sys.ps1 = ps1
        sys.ps2 = ps2
