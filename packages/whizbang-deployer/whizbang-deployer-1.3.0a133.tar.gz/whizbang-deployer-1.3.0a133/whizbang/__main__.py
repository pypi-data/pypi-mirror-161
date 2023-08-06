import sys, logging

from whizbang.container.application_container import ApplicationContainer
from whizbang.domain.menu.menu_invoker import MenuInvoker

from whizbang.util.json_helpers import import_local_json
from whizbang.util.deployment_helpers import merge_child_config

# see: https://python-dependency-injector.ets-labs.org/examples/decoupled-packages.html
from whizbang.util.logger import logger


def execute(solution_type, solution_directory, env_config_file_name: str, client_config_file_name: str = None):
    logger.info("executing command line mode")
    container = create_container(solution_directory, env_config_file_name, client_config_file_name)
    solution_factory = container.solution_factory()
    solution = solution_factory.get_solution(solution_type)
    solution.deploy()


def main(args=None):
    title = r"""
                                         /\\
                                        /  \\
                                       |    |
                                     --:'''':--
                                       :'_' :
                                       _:"":\___
                        ' '      ____.' :::     '._
                       . *=====<<=)           \    :
                        .  '      '-'-'\_      /'._.'
                                         \====:_ ""
                                        .'     \\
      ,. _                        whiz :       :                   
    '-'    ).                         /   :    \\
  (        '  )                       :   .      '.
 ( -  .bang.  - _                     :  : :      :
(    .'  _ )     )                    :__:-:__.;--'
'-  ()_.\,\,   - deployer             '-'   '-'
"""
    print(title)    
    logger.warning("Interactive mode not supported at this time; see documentation.  Call solution.deploy() instead.")


def import_and_merge_configs(current_dir_path: str, base_config_file_path: str, child_config_file_path: str = None):
    """This function merges a base env_config with a child config to produce a final combined configuration."""
    
    default_config_json = import_local_json(f'{current_dir_path}/{base_config_file_path}')
    result = default_config_json
    
    if child_config_file_path is not None:
        logger.info(f'client config {child_config_file_path} specified...')
        client_config_json = import_local_json(f'{current_dir_path}/{child_config_file_path}')

        logger.info(f'attempting to merge client config: {base_config_file_path} with child config: {child_config_file_path}')
        merged_config = merge_child_config(client_config_json, default_config_json)
        
        logger.info(f'merge successful')

        result = merged_config

    return result


def create_container(solution_directory, base_config_file_path: str, child_config_file_path: str = None):
    current_dir_path = str.replace(solution_directory, '\\', '/')
    app_config_json = {
        "current_dir_path": current_dir_path
    }

    environment_config_json = import_and_merge_configs(
        current_dir_path=current_dir_path,
        base_config_file_path=base_config_file_path,
        child_config_file_path=child_config_file_path
    )

    container = ApplicationContainer()
    container.config.app_config.from_dict(app_config_json)
    container.config.environment_config.from_dict(environment_config_json)
    container.wire(modules=[sys.modules[__name__]])
    return container


if __name__ == '__main__':
    main()
