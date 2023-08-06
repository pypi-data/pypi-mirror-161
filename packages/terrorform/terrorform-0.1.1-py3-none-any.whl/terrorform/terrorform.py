import json
import sys
import subprocess


TERRORFORM_OPTIONS = {
    # non-global options for terraform need to be placed *after* the workflow keyword
    # when using the CLI, while global options are placed *before* the workflow keyword
    # TODO: this list is not exhaustive, but Terraform documentation doesn't appear to
    #  provide a centralized global parameter list. Will need to look into it more.
    "NON_GLOBAL_KW_OPTIONS": [
        "-input", "-lock", "-lock-timeout", "-refresh", "-replace", "-target",
        "-var", "-var-file", "-parallelism", "-state", "-state-out", "-backup"
    ],
    # Suppress user prompts for approval at runtime for apply and destroy workflows.
    # Overriding this flag is not recommended, as the prompt itself will not actually
    # display at runtime, and the program will hang for an indefinite period of time
    # before crashing.
    "AUTO_APPROVE": True,
    # Prevent terraform from placing state locking on .tfstate files.
    "LOCK": False,
    # Terraform does not expose any option to suppress output, so this flag is used
    # in the subprocess.run() command in the cmd() function below
    "SILENT": False
}


class arg(tuple):
    """
    Wrapper class for proper formatting of a terraform keyword argument.
    """

    def __str__(self):
        return f"{self[0]}={json.dumps(self[1])}"

    def __repr__(self):
        return str(self)


class var(tuple):
    """
    Wrapper class for proper formatting of custom terraform variables in a
    CLI command (as opposed to being located within a .ftvars file).
    """

    def __str__(self):
        return \
            f"-var=\'{self[0]}=" \
            f"{self[1] if isinstance(self[1], str) else json.dumps(self[1])}\'"

    def __repr__(self):
        return str(self)


class terrorform:
    """
    Wrapper for terraform CLI
    """

    @staticmethod
    def _cmd(workflow: str, kw_args: dict, boolean_flags: list, var_args: dict):
        """
        Construct a terraform CLI command.
        """

        global_args = [
            str(arg(t)) for t in kw_args.items()
            if t[0] not in TERRORFORM_OPTIONS.get("NON_GLOBAL_KW_OPTIONS", [])
        ]
        non_global_args = [
            str(arg(t)) for t in kw_args.items()
            if t[0] in TERRORFORM_OPTIONS.get("NON_GLOBAL_KW_OPTIONS", [])
        ]
        custom_vars = [str(var(t)) for t in var_args.items()]

        return " ".join(
            ["terraform"] + global_args + [workflow] +
            non_global_args + boolean_flags + custom_vars
        )

    @staticmethod
    def cmd(_cmd: str):
        """
        Execute a shell command.
        """
        return subprocess.run(
            _cmd,
            encoding="UTF-8",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL if TERRORFORM_OPTIONS.get("SILENT", True) else sys.stdout
        )

    @staticmethod
    def _init(kw_args: dict = None, boolean_flags: list = None, vars_dict: dict = None):
        """
        Construct CLI command for init workflow.
        """
        return terrorform._cmd(
            "init",
            kw_args if kw_args is not None else {},
            boolean_flags if boolean_flags is not None else [],
            vars_dict if vars_dict is not None else {}
        )

    @staticmethod
    def init(kw_args: dict = None, boolean_flags: list = None, vars_dict: dict = None, dry: bool = False):
        """
        Run terraform init workflow.
        """
        _cmd = terrorform._init(kw_args, boolean_flags, vars_dict)
        return _cmd if dry else terrorform.cmd(_cmd)

    @staticmethod
    def _configure_default_kw_args(kw_args: dict = None):
        """
        Ensure keyword arguments dict for apply and destroy workflows
        contains key(s) that this library requires to function properly.
        """

        if kw_args is None:
            return {"-lock": TERRORFORM_OPTIONS.get("LOCK", False)}
        else:
            return {**kw_args, "-lock": TERRORFORM_OPTIONS.get("LOCK", False)} \
                if "-lock" not in kw_args \
                else kw_args

    @staticmethod
    def _configure_default_boolean_flags(boolean_flags: list = None):
        """
        Ensure boolean flags list for apply and destroy workflows contains
        flag(s) that this library requires to function properly.
        """

        if boolean_flags is None:
            return ["-auto-approve"] if TERRORFORM_OPTIONS.get("AUTO_APPROVE", True) else []
        else:
            return boolean_flags + ["-auto-approve"] \
                if TERRORFORM_OPTIONS.get("AUTO_APPROVE", True) and "-auto-approve" not in boolean_flags \
                else boolean_flags

    @staticmethod
    def _apply(kw_args: dict = None, boolean_flags: list = None, vars_dict: dict = None):
        """
        Construct CLI command for apply workflow
        """
        return terrorform._cmd(
            "apply",
            terrorform._configure_default_kw_args(kw_args),
            terrorform._configure_default_boolean_flags(boolean_flags),
            vars_dict if vars_dict is not None else {}
        )

    @staticmethod
    def apply(kw_args: dict = None, boolean_flags: list = None, vars_dict: dict = None, dry: bool = False):
        """
        Run terraform apply workflow.
        """

        _cmd = terrorform._apply(kw_args, boolean_flags, vars_dict)
        return _cmd if dry else terrorform.cmd(_cmd)

    @staticmethod
    def _destroy(kw_args: dict = None, boolean_flags: list = None, vars_dict: dict = None):
        """
        Construct CLI command for destroy workflow
        """
        return terrorform._cmd(
            "destroy",
            terrorform._configure_default_kw_args(kw_args),
            terrorform._configure_default_boolean_flags(boolean_flags),
            vars_dict if vars_dict is not None else {}
        )

    @staticmethod
    def destroy(kw_args: dict = None, boolean_flags: list = None, vars_dict: dict = None, dry: bool = False):
        """
        Run terraform destroy workflow.
        """
        _cmd = terrorform._destroy(kw_args, boolean_flags, vars_dict)
        return _cmd if dry else terrorform.cmd(_cmd)


# top-level synonyms
init = terrorform.init
apply = terrorform.apply
destroy = terrorform.destroy
