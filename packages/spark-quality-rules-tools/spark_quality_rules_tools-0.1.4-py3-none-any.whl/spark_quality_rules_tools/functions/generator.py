import warnings

warnings.filterwarnings('always')
warnings.filterwarnings('ignore')


def get_creating_directory(path=None):
    import os
    from spark_quality_rules_tools import get_color, get_color_b

    if path in ("", None):
        raise Exception(f'required variable path')

    if not os.path.exists(f'{path}'):
        os.makedirs(f'{path}')
        print(f"{get_color('Directory Created:')} {get_color_b(path)}")
    else:
        print(f"{get_color('Directory Exists:')} {get_color_b(path)}")


def get_path_workspace(user_sandbox=None,
                       uuaa_code='fina',
                       project_sda='CDD'):
    import os
    import sys

    if user_sandbox is None:
        user_sandbox = os.getenv('JPY_USER')
        if user_sandbox in ("", None):
            raise Exception(f'required variable user_sandbox')

    is_windows = sys.platform.startswith('win')
    pj_dir_workspace = ""

    pj_dq_dir_uuaa_code = os.path.join(uuaa_code, "data", "projects", project_sda, "data_quality_rules")
    pj_dq_dir_sandbox_dq_metrics = f"/data/sandboxes/{pj_dq_dir_uuaa_code}/data/users/{user_sandbox}/dq/metrics"
    pj_dq_dir_sandbox_dq_refusals = f"/data/sandboxes/{pj_dq_dir_uuaa_code}/data/users/{user_sandbox}/dq/refusals"
    pj_dq_dir_name = "data_quality_rules"
    pj_dq_dir_artifacts_python = os.path.join(pj_dir_workspace, "artifacts", "python")
    pj_dq_dir_name = os.path.join(pj_dir_workspace, pj_dq_dir_name)
    pj_dq_dir_repository_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "repository")
    pj_dq_dir_repository_txt_name = os.path.join(pj_dq_dir_repository_name, "txt")
    pj_dq_dir_repository_bucket_name = os.path.join(pj_dq_dir_repository_name, "bucket")
    pj_dq_dir_confs_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_confs")
    pj_dq_dir_hocons_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_hocons")
    pj_dq_dir_reports_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_reports")
    pj_dq_dir_reports_export_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_reports_export")
    pj_dq_dir_resolve_name = os.path.join(pj_dir_workspace, pj_dq_dir_name, "data_resolve")

    if is_windows:
        pj_dq_dir_uuaa_code = pj_dq_dir_uuaa_code.replace("\\", "/")
        pj_dq_dir_sandbox_dq_metrics = pj_dq_dir_sandbox_dq_metrics.replace("\\", "/")
        pj_dq_dir_sandbox_dq_refusals = pj_dq_dir_sandbox_dq_refusals.replace("\\", "/")
        pj_dq_dir_artifacts_python = pj_dq_dir_artifacts_python.replace("\\", "/")
        pj_dq_dir_name = pj_dq_dir_name.replace("\\", "/")
        pj_dq_dir_repository_name = pj_dq_dir_repository_name.replace("\\", "/")
        pj_dq_dir_repository_txt_name = pj_dq_dir_repository_txt_name.replace("\\", "/")
        pj_dq_dir_repository_bucket_name = pj_dq_dir_repository_bucket_name.replace("\\", "/")
        pj_dq_dir_confs_name = pj_dq_dir_confs_name.replace("\\", "/")
        pj_dq_dir_hocons_name = pj_dq_dir_hocons_name.replace("\\", "/")
        pj_dq_dir_reports_name = pj_dq_dir_reports_name.replace("\\", "/")
        pj_dq_dir_reports_export_name = pj_dq_dir_reports_export_name.replace("\\", "/")
        pj_dq_dir_resolve_name = pj_dq_dir_resolve_name.replace("\\", "/")

    get_creating_directory(path=pj_dq_dir_name)
    get_creating_directory(path=pj_dq_dir_artifacts_python)
    get_creating_directory(path=pj_dq_dir_repository_name)
    get_creating_directory(path=pj_dq_dir_repository_txt_name)
    get_creating_directory(path=pj_dq_dir_repository_bucket_name)
    get_creating_directory(path=pj_dq_dir_confs_name)
    get_creating_directory(path=pj_dq_dir_hocons_name)
    get_creating_directory(path=pj_dq_dir_reports_name)
    get_creating_directory(path=pj_dq_dir_reports_export_name)
    get_creating_directory(path=pj_dq_dir_resolve_name)

    os.environ['pj_dq_dir_name'] = pj_dq_dir_name
    os.environ['pj_dq_dir_artifacts_python'] = pj_dq_dir_artifacts_python
    os.environ['pj_dq_dir_repository_name'] = pj_dq_dir_repository_name
    os.environ['pj_dq_dir_repository_txt_name'] = pj_dq_dir_repository_txt_name
    os.environ['pj_dq_dir_repository_bucket_name'] = pj_dq_dir_repository_bucket_name
    os.environ['pj_dq_dir_confs_name'] = pj_dq_dir_confs_name
    os.environ['pj_dq_dir_hocons_name'] = pj_dq_dir_hocons_name
    os.environ['pj_dq_dir_reports_name'] = pj_dq_dir_reports_name
    os.environ['pj_dq_dir_reports_export_name'] = pj_dq_dir_reports_export_name
    os.environ['pj_dir_workspace'] = pj_dir_workspace
    os.environ['pj_dq_dir_uuaa_code'] = pj_dq_dir_uuaa_code
    os.environ['pj_dq_dir_sandbox_dq_metrics'] = pj_dq_dir_sandbox_dq_metrics
    os.environ['pj_dq_dir_sandbox_dq_refusals'] = pj_dq_dir_sandbox_dq_refusals
    os.environ['pj_dq_dir_resolve_name'] = pj_dq_dir_resolve_name


def get_spark_session(user_sandbox=None):
    import os
    from pyspark.sql import SparkSession
    from spark_quality_rules_tools import get_color, get_color_b

    dir_uuaa_code = os.getenv("pj_dq_dir_uuaa_code")
    dir_sandbox_dq_metrics = os.getenv("pj_dq_dir_sandbox_dq_metrics")
    dir_sandbox_dq_refusals = os.getenv("pj_dq_dir_sandbox_dq_refusals")
    if user_sandbox is None:
        user_sandbox = os.getenv('JPY_USER')
        if user_sandbox in ("", None):
            raise Exception(f'required variable user_sandbox')
    if dir_uuaa_code in ("", None):
        raise Exception(f'required environment: pj_dq_dir_uuaa_code')
    if dir_sandbox_dq_metrics in ("", None):
        raise Exception(f'required environment: pj_dq_dir_sandbox_dq_metrics')
    if dir_sandbox_dq_refusals in ("", None):
        raise Exception(f'required environment: pj_dq_dir_sandbox_dq_refusals')

    os.environ['UUAA_CODE'] = dir_uuaa_code
    os.environ['JPY_USER'] = user_sandbox
    os.environ['SANDBOX_DQ_METRICS'] = dir_sandbox_dq_metrics
    os.environ['SANDBOX_DQ_REFUSALS'] = dir_sandbox_dq_refusals

    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("JONAP") \
        .getOrCreate()
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
    sc = spark.sparkContext
    sc._conf.setExecutorEnv("UUAA_CODE", os.getenv("UUAA_CODE"))
    sc._conf.setExecutorEnv("JPY_USER", os.getenv("JPY_USER"))
    sc._conf.setExecutorEnv("SANDBOX_DQ_METRICS", os.getenv("SANDBOX_DQ_METRICS"))
    sc._conf.setExecutorEnv("SANDBOX_DQ_REFUSALS", os.getenv("SANDBOX_DQ_REFUSALS"))

    print(f"{get_color('Created Session Spark for user:')} {get_color_b(user_sandbox)}")
    return spark, sc


def get_creating_directory_txt_file_empty(uuaa_name=None,
                                          table_name=None,
                                          confs_list=None):
    import os
    import sys
    from spark_quality_rules_tools import get_color, get_color_b

    is_windows = sys.platform.startswith('win')
    dir_repo_txt_name = os.getenv("pj_dq_dir_repository_txt_name")
    if dir_repo_txt_name in ("", None):
        raise Exception(f'required environment: pj_dq_dir_repository_txt_name')
    if uuaa_name in ("", None):
        raise Exception(f'required variable uuaa_name')
    if table_name in ("", None):
        raise Exception(f'required variable table_name')
    if confs_list in ("", None, []):
        raise Exception(f'required variable confs_list')

    for conf_name in confs_list:
        dir_repo_txt_name = os.getenv("pj_dq_dir_repository_txt_name")
        dir_repo_txt_name_filename = os.path.join(dir_repo_txt_name, uuaa_name, table_name, f"{conf_name}.txt")
        if is_windows:
            dir_repo_txt_name_filename = dir_repo_txt_name_filename.replace("\\", "/")
        os.makedirs(os.path.dirname(dir_repo_txt_name_filename), exist_ok=True)
        open(dir_repo_txt_name_filename, "a").close()

        print(f"{get_color('Creating file empty:')} {get_color_b(dir_repo_txt_name_filename)}")


def get_repository_data(repo_urls=None):
    import git
    import os
    import sys
    from spark_quality_rules_tools import get_color, get_color_b

    is_windows = sys.platform.startswith('win')
    dir_repository_bucket_name = os.getenv("pj_dq_dir_repository_bucket_name")
    if dir_repository_bucket_name is None:
        raise Exception(f'required environment: pj_dq_dir_repository_bucket_name')
    if repo_urls is None:
        raise Exception(f'required variable repo_urls:[]')

    for repo_url in repo_urls:
        repo_name = str(repo_url.split("/")[-1]).split(".")[0]
        repo_path = os.path.join(os.getenv("pj_dq_dir_repository_bucket_name"), repo_name)
        if is_windows:
            repo_path = repo_path.replace("\\", "/")

        if not os.path.exists(f'{repo_path}'):
            git.Repo.clone_from(repo_url, repo_path)
            print(f"{get_color('Clone Repo:')} {get_color_b(repo_name)}")
        else:
            repo = git.Repo(repo_path)
            origin = repo.remote("origin")
            origin.fetch()
            print(f"{get_color('Pull Repo:')} {get_color_b(repo_name)}")
            pass
    print(f"{get_color('Repo completed:')} {get_color_b(dir_repository_bucket_name)}")


def get_transform_repo_to_txt():
    import os
    import sys
    import shutil
    from spark_quality_rules_tools import get_color, get_color_b

    is_windows = sys.platform.startswith('win')
    dir_repo_txt_name = os.getenv('pj_dq_dir_repository_txt_name')
    dir_repo_bucket_name = os.getenv("pj_dq_dir_repository_bucket_name")
    if dir_repo_txt_name is None:
        raise Exception(f'required environment: pj_dq_dir_repository_txt_name')
    if dir_repo_bucket_name is None:
        raise Exception(f'required environment: pj_dq_dir_repository_bucket_name')

    if os.path.exists(dir_repo_txt_name):
        shutil.rmtree(dir_repo_txt_name)
    os.makedirs(dir_repo_txt_name, exist_ok=True)

    dir_repo_bucket_names = [f for f in os.listdir(dir_repo_bucket_name) if not f.startswith('.')]
    for directory in dir_repo_bucket_names:
        dir_repo_dq = os.path.join(dir_repo_bucket_name, directory)
        dir_repo_dq = os.path.join(dir_repo_dq, "skynet", "src", "main", "resources", "dq")
        if is_windows:
            dir_repo_dq = dir_repo_dq.replace("\\", "/")
        dir_repo_dqs = [f for f in os.listdir(dir_repo_dq) if not f.startswith('.')]
        for uuaa in dir_repo_dqs:
            dir_repo_dq_uuaa = os.path.join(dir_repo_dq, uuaa)
            if is_windows:
                dir_repo_dq_uuaa = dir_repo_dq_uuaa.replace("\\", "/")
            dir_repo_dq_uuaas = [f for f in os.listdir(dir_repo_dq_uuaa) if not f.startswith('.')]
            for table in dir_repo_dq_uuaas:
                dir_repo_dq_uuaa_table = os.path.join(dir_repo_dq_uuaa, table, "master")
                if is_windows:
                    dir_repo_dq_uuaa_table = dir_repo_dq_uuaa_table.replace("\\", "/")

                if os.path.exists(dir_repo_dq_uuaa_table):
                    dir_repo_dq_uuaa_tables = [f for f in os.listdir(dir_repo_dq_uuaa_table) if not f.startswith('.')]
                    for conf in dir_repo_dq_uuaa_tables:
                        dir_repo_dq_uuaa_table_filename = os.path.join(dir_repo_dq_uuaa_table, conf)
                        if is_windows:
                            dir_repo_dq_uuaa_table_filename = dir_repo_dq_uuaa_table_filename.replace("\\", "/")

                        _file_name, _file_extension = os.path.splitext(conf)
                        if str(_file_extension).startswith(".conf"):
                            conf_url = dir_repo_dq_uuaa_table_filename
                            conf_name_origin_full = str(conf_url.split("/")[-1])
                            conf_name_replace_full = conf_name_origin_full.split("_")
                            if len(conf_name_replace_full) >= 2:
                                conf_name_replace_full = conf_name_replace_full[2:]
                            conf_name_replace_full = "".join(conf_name_replace_full)

                            conf_name = str(conf_name_replace_full.split(".")[0])
                            conf_name_txt = f"{conf_name}.txt"
                            uuaa_name = str(conf_url.split("/")[-4])
                            table_name = str(conf_url.split("/")[-3])

                            dir_repo_uuaa_table_file = os.path.join(dir_repo_txt_name, uuaa_name, table_name, conf_name_txt)
                            if is_windows:
                                dir_repo_uuaa_table_file = dir_repo_uuaa_table_file.replace("\\", "/")

                            if not os.path.exists(os.path.dirname(dir_repo_uuaa_table_file)):
                                os.makedirs(os.path.dirname(dir_repo_uuaa_table_file), exist_ok=True)

                            try:
                                with open(conf_url) as f:
                                    hammurabi_conf = f.read()
                            except:
                                with open(conf_url, encoding="utf-8") as f:
                                    hammurabi_conf = f.read()

                            with open(f'{dir_repo_uuaa_table_file}', 'w') as f:
                                f.write(hammurabi_conf)
    print(f"{get_color('Send repo to txt has been completed:')} {get_color_b(dir_repo_txt_name)}")


def quality_rules_download_jar(jar_url=None):
    import requests
    import sys
    import os
    from spark_quality_rules_tools import get_color, get_color_b

    is_windows = sys.platform.startswith('win')
    dir_artifacts_python = os.getenv('pj_dq_dir_artifacts_python')
    jar_name = "hammurabi-sandbox-spark3.jar"
    if dir_artifacts_python is None:
        raise Exception(f'required environment: pj_dq_dir_artifacts_python')
    if jar_url is None:
        jar_url = "http://artifactory-flegetonte.live.mx.ether.igrupobbva/artifactory/list/" \
                  "gl-analytics-artifacts-data-generic/jars/hammurabi-sandbox-3.4.2-jar-with-dependencies.jar"

    dir_artifacts_python_jar_file = os.path.join(dir_artifacts_python, jar_name)
    if is_windows:
        dir_artifacts_python_jar_file = dir_artifacts_python_jar_file.replace("\\", "/")
    if os.path.isfile(dir_artifacts_python_jar_file):
        os.remove(dir_artifacts_python_jar_file)

    with requests.get(jar_url, stream=True, verify=True) as r:
        r.raise_for_status()
        with open(dir_artifacts_python_jar_file, 'wb+') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"{get_color('Download finished on:')} {get_color_b(dir_artifacts_python_jar_file)}")


def quality_rules_extract_parameters():
    import os
    import sys
    import re
    import shutil
    import json
    from spark_quality_rules_tools import get_color, get_color_b

    is_windows = sys.platform.startswith('win')
    dir_repo_txt_name = os.getenv('pj_dq_dir_repository_txt_name')
    dir_confs_name = os.getenv('pj_dq_dir_confs_name')
    if dir_repo_txt_name is None:
        raise Exception(f'required environment: pj_dq_dir_repository_txt_name')
    if dir_confs_name is None:
        raise Exception(f'required environment: pj_dq_dir_confs_name')
    if os.path.exists(dir_confs_name):
        shutil.rmtree(dir_confs_name)
    os.makedirs(dir_confs_name, exist_ok=True)

    dir_uuaas = [f for f in os.listdir(dir_repo_txt_name) if not f.startswith('.')]
    for uuaa in dir_uuaas:
        dir_repo_uuaa = os.path.join(dir_repo_txt_name, uuaa)
        if is_windows:
            dir_repo_uuaa = dir_repo_uuaa.replace("\\", "/")
        dir_repo_uuaas = [f for f in os.listdir(dir_repo_uuaa) if not f.startswith('.')]
        for table in dir_repo_uuaas:
            dir_repo_uuaa_table = os.path.join(dir_repo_uuaa, table)
            if is_windows:
                dir_repo_uuaa_table = dir_repo_uuaa_table.replace("\\", "/")
            dir_repo_uuaa_tables = [f for f in os.listdir(dir_repo_uuaa_table) if not f.startswith('.')]
            for conf in dir_repo_uuaa_tables:
                conf_name = str(conf.split(".")[0])
                dir_repo_uuaa_table_filename = os.path.join(dir_repo_uuaa_table, conf)
                dir_confs_filename = os.path.join(dir_confs_name, uuaa, table, conf)
                dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa, table, f"parameter-{conf_name}.json")

                if is_windows:
                    dir_repo_uuaa_table_filename = dir_repo_uuaa_table_filename.replace("\\", "/")
                    dir_confs_filename = dir_confs_filename.replace("\\", "/")
                    dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")

                os.makedirs(os.path.dirname(dir_confs_filename_parameters), exist_ok=True)

                with open(dir_repo_uuaa_table_filename) as f:
                    hammurabi_conf = f.read()

                with open(dir_confs_filename, 'w') as f:
                    f.write(hammurabi_conf)

                variables_1 = sorted(list(set(re.findall(r'{([a-zA-Z_.-]+)}', hammurabi_conf))))
                variables_2 = sorted(list(set(re.findall(r'{?([a-zA-Z_.-]+)}', hammurabi_conf))))

                variables_list = list(set(variables_1 + variables_2))
                variables_dict = {variables: "" for variables in variables_list}

                parameter_dict = dict()
                parameter_dict[uuaa] = list()
                parameter_dict[uuaa].append({"table": table, "conf_name": conf, "parameters": variables_dict})

                with open(f"{dir_confs_filename_parameters}", "w") as f:
                    json.dump(parameter_dict, f, indent=4)

        print(f"{get_color('Generated json parameters for uuaas:')} {get_color_b(uuaa)} from {get_color_b(dir_repo_uuaa)}")


def quality_rules_get_conf_parameter(uuaa_name=None,
                                     table_name=None,
                                     confs_list=None):
    import json
    import sys
    import os
    from spark_quality_rules_tools import get_color, get_color_b

    is_windows = sys.platform.startswith('win')
    dir_confs_name = os.getenv('pj_dq_dir_confs_name')
    if dir_confs_name is None:
        raise Exception(f'required environment: pj_dq_dir_confs_name')

    quality_rules_extract_parameters()

    for conf_name in confs_list:
        conf_name_txt = f"{conf_name}.txt"
        parameter_conf_name_json = f"parameter-{conf_name}.json"
        dir_confs_filename_txt = os.path.join(dir_confs_name, uuaa_name, table_name, conf_name_txt)
        dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa_name, table_name, parameter_conf_name_json)

        if is_windows:
            dir_confs_filename_txt = dir_confs_filename_txt.replace("\\", "/")
            dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")

        if not os.path.isfile(dir_confs_filename_txt):
            raise Exception(f'No exists txt file: {conf_name_txt}')

        if not os.path.isfile(dir_confs_filename_parameters):
            raise Exception(f'No exists json parameter: {parameter_conf_name_json}')

        with open(dir_confs_filename_parameters) as f:
            parameter_conf = f.read()
            parameter_conf = json.loads(parameter_conf)

        params_parametes = parameter_conf[uuaa_name][0]["parameters"]
        params_parametes = json.dumps(params_parametes, indent=4)

        print(f"{get_color(f'================================')} ")
        print(f"{get_color('uuaa name :')} {get_color_b(uuaa_name)}")
        print(f"{get_color('table name:')} {get_color_b(table_name)}")
        print(f"{get_color('conf name :')} {get_color_b(parameter_conf_name_json)}")
        print(f"{get_color('parameters:')} {get_color_b(params_parametes)}")
        print(f"{get_color('=================================')} ")


def quality_rules_get_run_parameter(spark=None,
                                    sc=None,
                                    uuaa_name=None,
                                    table_name=None,
                                    conf_name=None,
                                    parameter_conf_list=None):
    import json
    import sys
    import gc
    import os
    from datetime import datetime
    from tqdm import tqdm
    from pyhocon.converter import HOCONConverter
    from pyspark.sql import functions as func
    from spark_quality_rules_tools import get_color, get_color_b
    from spark_quality_rules_tools import get_replace_resolve_parameter
    from IPython.core.display import HTML, display

    is_windows = sys.platform.startswith('win')
    dir_confs_name = os.getenv('pj_dq_dir_confs_name')
    dir_hocons_name = os.getenv('pj_dq_dir_hocons_name')
    dir_reports_name = os.getenv('pj_dq_dir_reports_name')
    uuaa_code = os.getenv("UUAA_CODE")
    user_sandbox = os.getenv("JPY_USER")
    dir_sandbox_dq_metrics = os.getenv("pj_dq_dir_sandbox_dq_metrics")
    dir_sandbox_dq_refusals = os.getenv("pj_dq_dir_sandbox_dq_refusals")

    if dir_confs_name is None:
        raise Exception(f'required environment: pj_dq_dir_confs_name')
    if dir_hocons_name is None:
        raise Exception(f'required environment: pj_dq_dir_hocons_name')
    if dir_reports_name is None:
        raise Exception(f'required environment: pj_dq_dir_reports_name')
    if uuaa_code is None:
        raise Exception(f'required environment: UUAA_CODE')
    if user_sandbox is None:
        raise Exception(f'required environment: JPY_USER')
    if dir_sandbox_dq_metrics is None:
        raise Exception(f'required environment: pj_dq_dir_sandbox_dq_metrics')

    for params_parameter_conf in tqdm(parameter_conf_list):
        from pyhocon import ConfigFactory
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        current_datetime_str = now.strftime("%Y%m%d%H%M")

        conf_name_txt = f"{conf_name}.txt"
        parameter_conf_name_json = f"parameter-{conf_name}.json"
        dir_confs_filename_txt = os.path.join(dir_confs_name, uuaa_name, table_name, conf_name_txt)
        dir_confs_filename_parameters = os.path.join(dir_confs_name, uuaa_name, table_name, parameter_conf_name_json)

        if is_windows:
            dir_confs_filename_txt = dir_confs_filename_txt.replace("\\", "/")
            dir_confs_filename_parameters = dir_confs_filename_parameters.replace("\\", "/")

        if not os.path.isfile(dir_confs_filename_txt):
            raise Exception(f'No exists txt file: {conf_name_txt}')

        if not os.path.isfile(dir_confs_filename_parameters):
            raise Exception(f'No exists json parameter: {parameter_conf_name_json}')

        with open(dir_confs_filename_txt) as f:
            txt_conf = f.read()

        with open(dir_confs_filename_parameters) as f:
            parameter_conf = f.read()
            parameter_conf = json.loads(parameter_conf)

        params_parameter = parameter_conf[uuaa_name][0]["parameters"]
        validate_parameter_keys = list(set(params_parameter.keys()))
        validate_parameter_conf_keys = list(set([b for a in parameter_conf_list for b in a.keys()]))
        validate_comparate_parameters = (sorted(validate_parameter_keys) == sorted(validate_parameter_conf_keys))
        if not validate_comparate_parameters:
            raise Exception(f'Need more variables the parameters: parameter_conf_list')

        cutoff_date = ""
        for k, v in params_parameter_conf.items():
            if str(k).upper() == "ODATE":
                cutoff_date = str(v).replace("-", "").strip()
            elif str(k).upper() == "CUTOFF_DATE":
                cutoff_date = str(v).replace("-", "").strip()
            txt_conf = txt_conf.replace(f'${{{k}}}', v)
            txt_conf = txt_conf.replace(f'${{?{k}}}', v)

        conf_name_conf = f"{conf_name}_{cutoff_date}.conf"
        dir_hocons_filename_conf = os.path.join(dir_hocons_name, uuaa_name, table_name, conf_name_conf)
        dir_reports_name_filename = os.path.join(dir_reports_name, f"{conf_name}_{current_datetime_str}_{cutoff_date}.csv")
        if is_windows:
            dir_hocons_filename_conf = dir_hocons_filename_conf.replace("\\", "/")
            dir_reports_name_filename = dir_reports_name_filename.replace("\\", "/")

        os.makedirs(os.path.dirname(dir_hocons_filename_conf), exist_ok=True)

        conf_file = ConfigFactory.parse_string(txt_conf)
        hocons_file = HOCONConverter.to_hocon(conf_file)
        with open(dir_hocons_filename_conf, "w") as f:
            f.write(hocons_file)

        Path = spark._jvm.org.apache.hadoop.fs.Path
        fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
        if fs.exists(Path(dir_sandbox_dq_metrics)):
            fs.delete(Path(dir_sandbox_dq_metrics), True)
        if fs.exists(Path(dir_sandbox_dq_refusals)):
            fs.delete(Path(dir_sandbox_dq_refusals), True)

        conf = sc._jvm.java.io.File(dir_hocons_filename_conf)
        ConfigFactory = sc._jvm.com.typesafe.config.ConfigFactory
        parsed_conf = ConfigFactory.parseFile(conf)
        resolve_path = get_replace_resolve_parameter(sc=sc)
        resolvedConfig = parsed_conf.withFallback(resolve_path).resolve()
        Standalone = sc._jvm.com.datio.hammurabi.standalone
        result = Standalone.Hammurabi.run(spark._jsparkSession, resolvedConfig)
        display(HTML("<style>pre { white-space: pre !important; }</style>"))
        if result == 2:
            print(f"{get_color('Problem to build the execution, possible configuration or poorly defined rule')} ")
            break
        else:
            if result == 1:
                print(f"{get_color('Quality validation failed, critical rule failed')} ")
            elif result == 0:
                print(f"{get_color('Quality validation has passed. This means that there is no critical rule that has failed.')} ")

            metrics_df = spark.read.parquet(dir_sandbox_dq_metrics)
            metrics_filter = metrics_df.filter(
                func.col("gf_quality_rule_execution_date") > func.unix_timestamp(func.lit(current_datetime)).cast('timestamp'))
            metrics_filter_pandas = metrics_filter.toPandas()
            metrics_filter_pandas.to_csv(dir_reports_name_filename, index=False)

            del metrics_df, metrics_filter, metrics_filter_pandas
            gc.collect()

            print(f"{get_color(f'================================')} ")
            print(f"{get_color('uuaa name :')} {get_color_b(uuaa_name)}")
            print(f"{get_color('table name:')} {get_color_b(table_name)}")
            print(f"{get_color('conf name :')} {get_color_b(parameter_conf_name_json)}")
            print(f"{get_color('cutoff date:')} {get_color_b(cutoff_date)}")
            print(f"{get_color('Generating a file csv:')} {get_color_b(dir_reports_name_filename)}")
            print(f"{get_color('=================================')} ")


def get_compress_report():
    import os
    import sys
    import zipfile
    import shutil
    from spark_quality_rules_tools import get_color, get_color_b

    is_windows = sys.platform.startswith('win')
    dir_reports_name = os.getenv('pj_dq_dir_reports_name')
    dir_reports_export_name = os.getenv("pj_dq_dir_reports_export_name")
    if dir_reports_name is None:
        raise Exception(f'required environment: pj_dq_dir_reports_name')
    if dir_reports_export_name is None:
        raise Exception(f'required environment: pj_dq_dir_reports_export_name')

    dir_reports_export_zipname = os.path.join(dir_reports_export_name, 'zip_report_hammurabi.zip')
    if is_windows:
        dir_reports_export_zipname = dir_reports_export_zipname.replace("\\", "/")

    zipf = zipfile.ZipFile(dir_reports_export_zipname, 'w', zipfile.ZIP_DEFLATED)
    if os.path.isfile(dir_reports_export_name):
        shutil.rmtree(dir_reports_export_name)
        os.makedirs(dir_reports_export_name)

    for root, dirs, files in os.walk(dir_reports_name):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()
    print(f"{get_color('Complete compress file:')} {get_color_b(dir_reports_export_zipname)}")


def get_quality_run_repo_local(project_sda=None,
                               repo_urls=None):
    from spark_quality_rules_tools import get_color

    print(f"{get_color('===Generate Pipeline===')} ")
    print(f"{get_color('1. Generate WorkSpace')} ")
    # Get Path WorkSpace
    get_path_workspace(project_sda=project_sda)

    print(f"{get_color('2. Generate Repo Local')} ")
    # Get Repo Local
    get_repository_data(repo_urls=repo_urls)

    print(f"{get_color('3. Generate Repo to Txt')} ")
    # Get Transform Repo to TXT
    get_transform_repo_to_txt()

    print(f"{get_color('Complete Pipeline')} ")
    print(f"{get_color('========================')} ")


def get_quality_run_sandbox(project_sda=None,
                            spark=None,
                            sc=None,
                            uuaa_name=None,
                            table_name=None,
                            conf_name=None,
                            parameter_conf_list=None,
                            is_download_jar=False,
                            jar_url=None,
                            is_report_compress=False):
    from spark_quality_rules_tools import get_color

    print(f"{get_color('===Generate Pipeline===')} ")
    print(f"{get_color('1. Generate WorkSpace')} ")
    # Get Path WorkSpace
    get_path_workspace(project_sda=project_sda)

    print(f"{get_color('2. Download Jar Hammurabi')} ")
    # Download Jar
    if is_download_jar:
        if jar_url:
            quality_rules_download_jar(jar_url=jar_url)
        else:
            quality_rules_download_jar()

    print(f"{get_color('3. Extract Parameter')} ")
    # Extract y Show Parameter
    quality_rules_extract_parameters()

    print(f"{get_color('4. Run  Hammurabi')} ")
    # Get Run Parameters Json
    quality_rules_get_run_parameter(spark=spark,
                                    sc=sc,
                                    uuaa_name=uuaa_name,
                                    table_name=table_name,
                                    conf_name=conf_name,
                                    parameter_conf_list=parameter_conf_list)

    # Zip Compress Reports
    if is_report_compress:
        print(f"{get_color('5. Report Compress')} ")
        get_compress_report()

    print(f"{get_color('Complete Pipeline')} ")
    print(f"{get_color('========================')} ")
