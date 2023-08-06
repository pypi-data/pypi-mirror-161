from datetime import datetime


def bucket_key(
    variable,
    model_id,
    init: datetime,
    hour: int,
    environment,
    resolution,
    region,
    experiment=None,
):

    if environment == "production":
        bucket = "sofar-wx-data-production"
    elif environment == "staging":
        bucket = "sofar-wx-data-staging"
    elif environment == "dev":
        bucket = "sofar-wx-data-dev"

    init_date = init.strftime("%Y%m%d")
    init_cycle = init.strftime("%H")

    if experiment is not None:
        experiment = f"{experiment}"
    else:
        experiment = ""

    hour = "%03i" % hour
    key = (
        f"{model_id}/"
        f"{init_date}/"
        f"{init_cycle}/"
        f"{resolution}/"
        f"{region}/"
        f"{experiment}/"
        f"{model_id}.{init_date}.{init_cycle}.f{hour}.{variable}.nc"
    )
    return bucket, key
