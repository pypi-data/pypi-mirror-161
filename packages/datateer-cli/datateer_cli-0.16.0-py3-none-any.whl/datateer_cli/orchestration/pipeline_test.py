# import os

# from datateer.prefect import PipelineFlow
# from datateer.prefect.tasks import DbtTask, LoadSettingsTask

# CRON_SCHEDULE = "0 7 * * *"  # 7am UTC, 2am EST
# FLOW_NAME = f"example1"

# # if os.getenv("DATATEER_ENV") is None or os.getenv("DATATEER_ENV") == "local":
# #     # load in environment variables if we are running this flow from a development environment. Otherwise, the environment variables will be pre-loaded already
# #     from dotenv import load_dotenv

# #     load_dotenv()

# # load_settings = LoadSettingsTask(name="load settings")
# # dbt_setup = DbtTask(name="dbt setup", operations=["debug", "deps"])
# # dbt_seed = DbtTask(name="dbt seed", operations=["seed"])
# # dbt_run = DbtTask(name="dbt run", operations=["run"])
# # dbt_test = DbtTask(name="dbt test", operations=["test"])

# # env = os.getenv("DATATEER_ENV")
# with PipelineFlow(FLOW_NAME, cron=CRON_SCHEDULE if env == "prod" else None, notify_service_desk_on_error=True) as flow:
#     dbt_setup.set_upstream(load_settings)
#     dbt_seed.set_upstream(dbt_setup)
#     dbt_run.set_upstream(dbt_seed)
#     dbt_test.set_upstream(dbt_run)
