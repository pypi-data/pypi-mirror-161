# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from azureml.core import Experiment, ScriptRunConfig, Environment
from azureml.core.environment import CondaDependencies
import os
from omegaconf import OmegaConf
import hydra
from hydra.core.hydra_config import HydraConfig
from shrike.pipeline.aml_connect import azureml_connect
from shrike._core import (
    is_eyesoff_helper,
    b64_decode,
    b64_encode,
    experimental,
    POLYMER_FEED,
)
from shrike.pipeline import AMLPipelineHelper


def merge_serialize_config_with_default(serialized_config):
    default_config = AMLPipelineHelper._default_config()
    cfg = OmegaConf.merge(
        default_config, OmegaConf.structured(b64_decode(serialized_config))
    )
    return cfg


def get_or_create_env(ws, env_name, is_eyesoff):
    try:
        env = Environment.get(ws, env_name)
    except Exception:
        env = Environment(env_name)
        conda_dep = CondaDependencies.create(
            pip_packages=[
                "ray>=1.7.0",
                "shrike[pipeline]>=1.28.0",
            ],
            python_version="3.8",
            pip_indexurl=POLYMER_FEED if is_eyesoff else None,
        )
        env.python.conda_dependencies = conda_dep
    return env


@experimental()
@hydra.main(config_name="default")
def ray_actor_on_shrike(cfg):
    default_config = AMLPipelineHelper._default_config()
    cfg = OmegaConf.merge(default_config, cfg)
    env_name = "ray_env"

    aml = cfg.aml
    ws = azureml_connect(
        aml_subscription_id=aml.subscription_id,
        aml_resource_group=aml.resource_group,
        aml_workspace_name=aml.workspace_name,
        aml_auth=aml.get("auth", "interactive"),
        aml_tenant=aml.get("tenant", None),
        aml_force=aml.get("force", False),
    )
    env = get_or_create_env(
        ws, env_name, is_eyesoff_helper(aml.get("tenant", None), aml.subscription_id)
    )
    compute_target = cfg.compute.default_compute_target

    script = os.path.join(HydraConfig.get().runtime.cwd, cfg.run.script)
    with open(script) as file:
        contents = file.read()

    script_config = ScriptRunConfig(
        source_directory=".",
        command=["echo", "'" + contents + "'"]
        + "> script.py && python script.py --serialized_config".split()
        + [b64_encode(OmegaConf.to_yaml(cfg))],
        compute_target=compute_target,
        environment=env,
    )
    exp = Experiment(ws, cfg.run.experiment_name)
    run = exp.submit(script_config)
    print(run.get_portal_url())
    run.wait_for_completion()
