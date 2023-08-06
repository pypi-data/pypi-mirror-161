import pandas as pd

SPLIT_REQUEST_AT_SIZE_BYTES = 104857600  # 100 MB

# The following values are calculated by benchmarking request payload sizes
UNIT_DATA_SIZE_BY_SERIES = {
    r"NP\/BuyCurve": 23630,
    r"NP\/SellCurve": 23630,
    r"NP\/IntradayTrades": 520,
    r".*": 170,
}

# For the following, the first match is the one used, so it needs to be ordered
# correctly
# The values are roughly equal to len(archimedes.list_series_price_areas(series_id))
DEFAULT_NUMBER_OF_SUB_IDS = {
    r"IV\/.*": 1,
    r"MET\/forecast_wind_speed_10m_at_windfarms": 11,
    r"MET\/observation_wind_speed_10m_at_windfarms": 11,
    r"MET\/.*": 18,
    r"NP\/SysPrices": 1,
    r"NP\/AreaBlockPricesPeak": 15,
    r"NP\/AutomaticReserveDownVolume": 11,
    r"NP\/AutomaticReserveUpVolume": 11,
    r"NP\/BuyCurve": 1,
    r"NP\/Capacities": 10,
    r"NP\/CapacitiesPrognosis": 28,
    r"NP\/ConsumptionPrognosis": 18,
    r"NP\/FlowsAtAreaPrice": 28,
    r"NP\/FlowsAtSystemPrice": 5,
    r"NP\/IntradayTrades": 30,
    r"NP\/NetExchange": 7,
    r"NP\/PhysicalCapacities": 6,
    r"NP\/ProductionTotals": 18,
    r"NP\/ProductionTotalPrognosis": 17,
    r"NP\/ProductionWindPower": 17,
    r"NP\/ProductionWindPrognosis": 16,
    r"NP\/ReductionReasons": 16,
    r"NP\/SellCurve": 1,
    r"NP\/SystemPrices": 1,
    r"NP\/TotalConsumption": 18,
    r"NP\/TurnoverAtSystemPrice": 1,
    r"NP\/VolumeAcceptedBlocksBuy": 1,
    r"NP\/VolumeAcceptedBlocksSell": 1,
    r"NP\/.*": 12,
    r"OMX\/.*": 1,
    r"SN\/ConsumptionTotal": 8,
    r"SN\/FCRWVolume": 1,
    r"SN\/FlowExport": 1,
    r"SN\/FlowImport": 1,
    r"SN\/FlowNet": 1,
    r"SN\/ProductionHydro": 6,
    r"SN\/ProductionNuclear": 3,
    r"SN\/ProductionThermal": 8,
    r"SN\/ProductionTotal": 8,
    r"SN\/ProductionUnspecifiedSource": 5,
    r"SN\/ProductionWind": 8,
    r"SN\/WeeklyMTS.*Time": 1206,
    r"SN\/.*": 5,
    r".*": 12,
}

# The series_ids that appear as a result fo the following SQL queries:
# with s2 as (
# 	with s1 as (
# 		select
# 	    	subpath(series_id, 0, 2) as series_prefix,
# 	       	ltree2text(series_id) as sid
# 	    from observations --this should also be done for observations_json and forecasts
# 	    order by from_dt desc
# 	)
# 	    select
# 	    	series_prefix,
# 	    	sid,
# 	    	array_length(string_to_array(sid, '.'), 1) - 1 as c
# 	    from s1
# )
# select distinct(series_prefix) from s2 where c>2
PERMUTATION_RESULTS = {
    r"NP\/Capacities": 2,
    r"NP\/CapacitiesPrognosis": 2,
    r"NP\/FlowsAtAreaPrice": 2,
    r"NP\/FlowsAtSystemPrice": 2,
    r"NP\/IntradayTrades": 2,
    r"NP\/PhysicalCapacities": 2,
    r"NP\/ReductionReasons": 2,
}

# The following values come from estimating how many data points per series_ids exist
NUMBER_OF_DATA_POINTS_PER_HOUR = {
    r"NP\/CapacitiesPrognosis": 0.046,
    r"NP\/IntradayTrades": 4,
    r"OMX\/.*": 0.00034,
    r"SN\/WeeklyMTS.*Time": 1 / (7 * 24),
    r".*": 1,
}

END_OF_TODAY = pd.Timestamp.utcnow().replace(
    hour=0, minute=0, second=0, microsecond=0
) + pd.Timedelta(days=1)

DATE_RANGE = {
    r"IV\/BrentOil": (
        pd.to_datetime("2000-01-04 22:00:00+00"),
        END_OF_TODAY,
    ),
    r"IV\/CarbonEmissionsEUA": (
        pd.to_datetime("2008-07-04 16:00:00+00"),
        END_OF_TODAY,
    ),
    r"IV\/Coal": (
        pd.to_datetime("2008-12-08 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"IV\/NaturalGas": (
        pd.to_datetime("2000-01-04 22:00:00+00"),
        END_OF_TODAY,
    ),
    r"MET\/forecast_.*": (
        pd.to_datetime("2019-11-26 13:00:00+00"),
        END_OF_TODAY,
    ),
    r"MET\/.*": (
        pd.to_datetime("2013-09-01 00:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/BuyCurve": (
        pd.to_datetime("2013-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/FlowsAtSystemPrice": (
        pd.to_datetime("2015-12-31 23:00:00+00"),
        pd.to_datetime("2019-01-08 22:00:00+00"),
    ),
    r"NP\/HydroReservoir.*": (
        pd.to_datetime("2017-01-01 00:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/IntradayTrades": (
        pd.to_datetime("2010-01-01 00:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/NetFlowsAtSystemPrice": (
        pd.to_datetime("2013-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/SellCurve": (
        pd.to_datetime("2013-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/VolumeAcceptedBlocksBuy": (
        pd.to_datetime("2013-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/VolumeAcceptedBlocksSell": (
        pd.to_datetime("2013-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"NP\/.*": (
        pd.to_datetime("2015-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/Consumption": (
        pd.to_datetime("2000-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/ConsumptionTotal": (
        pd.to_datetime("2022-04-25 12:46:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/FCRNPrice": (
        pd.to_datetime("2013-01-07 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/FCRNVolume": (
        pd.to_datetime("2013-01-07 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/FCRWVolume": (
        pd.to_datetime("2013-01-11 23:00:00+00"),
        pd.to_datetime("2021-01-10 22:00:00+00"),
    ),
    r"SN\/FlowExport": (
        pd.to_datetime("2018-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/FlowImport": (
        pd.to_datetime("2018-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/FlowNet": (
        pd.to_datetime("2018-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/ProductionHydro": (
        pd.to_datetime("2022-04-25 12:46:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/ProductionNuclear": (
        pd.to_datetime("2022-04-25 12:46:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/ProductionThermal": (
        pd.to_datetime("2022-04-25 12:46:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/ProductionTotal": (
        pd.to_datetime("2022-04-25 12:46:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/ProductionUnspecifiedSource": (
        pd.to_datetime("2022-04-25 12:46:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/ProductionWind": (
        pd.to_datetime("2022-04-25 12:46:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/Production": (
        pd.to_datetime("2000-12-31 23:00:00+00"),
        END_OF_TODAY,
    ),
    r"SN\/WeeklyMTS.*Time": (
        pd.to_datetime("2007-01-01 00:00:00+00"),
        pd.Timestamp.utcnow() + pd.Timedelta(days=7),
    ),
    r"OMX\/.*": (
        pd.to_datetime("2022-02-28 23:00:00+00"),
        pd.Timestamp.utcnow() + pd.Timedelta(days=10 * 365),
    ),
    r".*": (
        pd.to_datetime("2010-01-01 00:00:00+00"),
        END_OF_TODAY,
    ),
}
