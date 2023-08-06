import copy
from typing import Dict

import dict_tools.differ as differ
import dict_tools.update

__func_alias__ = {"profile_": "profile"}
__contracts__ = ["soft_fail"]


async def profile_(
    hub,
    ctx,
    name: str,
    provider_name: str,
    profile_name: str = None,
    source_profile: str = None,
    acct_data: Dict = None,
    **kwargs,
):
    """
    :param hub:
    :param ctx:
    :param name: The name of the profile to add to acct
    :param provider_name: The name of the provider that this profile should be used for
    :param profile_name: The name of the new profile to add, defaults to the state name
    :param source_profile: The name of the profile to
    :param acct_data: The acct_data used as a source for existing profiles
    :param kwargs: Any extra keyword arguments will be passed directly into the new profile

    Extend the profiles of the current run with information passed to this state.
    The goal is not to write your acct_file for you with automation;.
    The purpose of this state is to dynamically create credentials for things like assuming new roles
      -- which can be re-calculated every run with negligible overhead.

    .. warning::

        This state intentionally does not implement ctx.test.
        If a profile can be created then it is used for test runs same as real runs.

    .. code-block:: yaml

        state_name:
          acct.profile:
            - provider_name: test
            - profile_name: default
            - source_profile: default
            - key_1: value_1
            - key_2: value_2
    """
    result = dict(comment=[], changes=None, new_state=None, name=name, result=True)
    if "profiles" not in hub.idem.RUNS[ctx.run_name]["acct_data"]:
        hub.idem.RUNS[ctx.run_name]["acct_data"]["profiles"] = {}

    before = list(
        hub.idem.RUNS[ctx.run_name]["acct_data"]["profiles"]
        .get(provider_name, {})
        .keys()
    )

    if profile_name is None:
        profile_name = name

    # Verify that we are not overwriting an existing profile unless explicitly asked to
    if profile_name in hub.idem.RUNS[ctx.run_name]["acct_data"]["profiles"].get(
        provider_name, {}
    ):
        result["comment"] += [
            f"Overwriting '{profile_name}' under provider '{provider_name}'"
        ]

    if ctx.test:
        result["comment"] += [
            "This state does not run in test mode",
            "If a profile can be successfully created then it is used for test runs same as real runs",
        ]

    # Copy from an existing profile first if one was given, else create a new one
    if source_profile:
        # Get the acct_data from the current run
        acct_data = acct_data or hub.idem.RUNS[ctx.run_name]["acct_data"]
        new_profile = copy.deepcopy(
            acct_data["profiles"].get(provider_name, {}).get(source_profile, {})
        )
    else:
        # Create a new raw profile
        new_profile = {}

    # Overwrite values in the new profile that exist in kwargs
    new_profile.update(kwargs)
    # Prepare the new profile to be merged onto tune RUNS dictionary
    profiles = {provider_name: {profile_name: new_profile}}

    # The value after the last dot is the plugin, everything before that is the provider sub
    provider_sub = provider_name.rsplit(".", maxsplit=1)[0]

    # Run the profiles through the gather plugins and update them with any changes
    processed_profiles = await hub.acct.init.process(
        [provider_sub], profiles, hard_fail=True
    )
    dict_tools.update.update(profiles, processed_profiles)

    # Update the profiles in the RUNS structure
    dict_tools.update.update(
        hub.idem.RUNS[ctx.run_name]["acct_data"]["profiles"], profiles
    )
    # Return the only profile keys that have been changed for this state since the values contain secure information
    after = list(
        hub.idem.RUNS[ctx.run_name]["acct_data"]["profiles"]
        .get(provider_name, {})
        .keys()
    )

    # Calculate changes directly to prevent sending a new_state to ESM
    result["changes"] = differ.deep_diff({"profiles": before}, {"profiles": after})

    return result
