import warnings

warnings.filterwarnings('always')
warnings.filterwarnings('ignore')


def get_replace_resolve_parameter(sc=None):
    import os
    import sys
    from spark_quality_rules_tools.utils import BASE_DIR
    from spark_quality_rules_tools.utils.color import get_color, get_color_b
    from pyhocon.converter import HOCONConverter
    from pyhocon import ConfigFactory

    is_windows = sys.platform.startswith('win')
    user_sandbox = os.getenv('JPY_USER')
    dir_uuaa_code = os.getenv("pj_dq_dir_uuaa_code")
    dir_resolve_name = os.getenv("pj_dq_dir_resolve_name")
    dir_resource_resolve = os.path.join(BASE_DIR, "utils", "resource", "resolve.conf")
    dir_resolve_filename = os.path.join(dir_resolve_name, "resolve.conf")

    if user_sandbox in ("", None):
        raise Exception(f'required environment JPY_USER')
    if dir_uuaa_code in ("", None):
        raise Exception(f'required environment pj_dq_dir_uuaa_code')
    if dir_resolve_name in ("", None):
        raise Exception(f'required environment pj_dq_dir_resolve_name')

    if is_windows:
        dir_resource_resolve = dir_resource_resolve.replace("\\", "/")
        dir_resolve_filename = dir_resolve_filename.replace("\\", "/")

    with open(dir_resource_resolve) as f:
        resolve_conf = f.read()
    variables_dict = dict(UUAA_CODE=None, JPY_USER=None)
    variables_dict["UUAA_CODE"] = dir_uuaa_code
    variables_dict["JPY_USER"] = user_sandbox

    for k, v in variables_dict.items():
        resolve_conf = resolve_conf.replace(f'${{{k}}}', v)
        resolve_conf = resolve_conf.replace(f'${{?{k}}}', v)

    conf_file = ConfigFactory.parse_string(resolve_conf)
    hocons_file = HOCONConverter.to_hocon(conf_file)
    with open(dir_resolve_filename, "w") as f:
        f.write(hocons_file)

    ConfigFactory = sc._jvm.com.typesafe.config.ConfigFactory
    conf2 = sc._jvm.java.io.File(dir_resolve_filename)
    resolve = ConfigFactory.parseFile(conf2)
    print(f"{get_color('Complete resolve file:')} {get_color_b(dir_resolve_filename)}")
    return resolve
