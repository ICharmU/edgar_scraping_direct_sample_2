import os
from pathlib import Path
import json
import shutil
import pandas as pd
import numpy as np
from pandasql import sqldf
from datetime import datetime

from typing import List

pd.set_option('display.max_rows', None)


def find_valid_paths() -> List:
    """
    Returns a list of company paths based on the company JSONs available.
    """
    data_fp = "json_data/"
    dir = os.fsencode(data_fp)

    company_file_paths = list()

    for file in os.listdir(dir):
        fname = os.fsdecode(file)
        if fname and ".json" in fname:
            company_file_paths.append(fname)

    return company_file_paths


def generate_company_data() -> List:
    """
    Returns a list containing dictionaries with company identifiable information and diluted EPS
    """
    company_data = list()
    for json_fname in company_file_paths[:]:
        fp = Path("json_data") / json_fname
        with open(fp) as f:
            data = json.load(f)
            relevant_metrics = dict()
            try:
                name = data["entityName"]
                if not name:
                    raise Exception()
                
                cik = data["cik"]
                relevant_metrics["company_info"] = {
                    "cik": cik,
                    "name": name,
                }

                # if cik != 2488: 
                #     continue
                
                if VERBOSE:
                    print(name, cik)

                relevant_metrics["diluted_eps"] = data["facts"]["us-gaap"]["EarningsPerShareDiluted"]
                metrics = list()
                for filing in relevant_metrics["diluted_eps"]["units"]["USD/shares"]:
                    if "frame" in filing:
                        filing_metrics = {
                            "cik": cik,
                            "start": filing["start"],
                            "end": filing["end"],
                            "filing_date": filing["filed"],
                            "diluted_eps": filing["val"],
                            "fiscal_year": filing["fy"],
                            "quarter": filing["fp"],
                        }
                        metrics.append(filing_metrics)
                relevant_metrics.pop("diluted_eps", None)
                relevant_metrics["metrics"] = metrics
                company_data.append(relevant_metrics)
            except:
                continue

    return company_data


def get_annual_forms(quarterly: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    quarterly - 

    Returns a dataframe containing only annual indices. 
    Annual being defined as 300 < days < 400 between the start and end of the period
    """
    annual_forms = quarterly.copy()

    annual_forms = annual_forms.loc[((annual_forms["end"] - annual_forms["start"]).dt.days > 300) & ((annual_forms["end"] - annual_forms["start"]).dt.days < 400),:]
    annual_forms.loc[annual_forms.index, "fiscal_year_start"] = annual_forms["start"]
    annual_forms.loc[annual_forms.index, "fiscal_year_end"] = annual_forms["end"]
    annual_forms = annual_forms[["fiscal_year_start", "fiscal_year_end"]]

    return annual_forms


def get_fiscal_years(annual_forms: pd.DataFrame, quarterly: pd.DataFrame) -> pd.DataFrame:
    """
    Attaches a fiscal year to each entry according to the start and end of the period.
    
    Note that the fiscal year is arbitrary and may differ from the actual fiscal year (+/- 1).
    The fiscal year groupings align with the actual fiscal year groupings.

    Parameters
    annual_forms - dataframe containing the annual records which cannot be removed from their fiscal year
    quarterly - 
    """
    quarterly = quarterly.copy()

    quarterly[["quarter", "fiscal_year"]] = None
    quarterly.loc[annual_forms.index, "quarter"] = "Q4"
    quarterly = quarterly.sort_values(by=["start", "end"])

    # avoid cross joining
    query = """
    SELECT *
    FROM quarterly q
    JOIN annual_forms a
    WHERE q.start >= a.fiscal_year_start AND q.end <= a.fiscal_year_end
    """
    merge_year = sqldf(query, locals())
    merge_year["fiscal_year"] = (
        merge_year
        .groupby(["fiscal_year_start", "fiscal_year_end"])["fiscal_year_end"]
        .transform(lambda x: datetime.strptime(min(x)[:10], "%Y-%m-%d").year)
    )

    quarterly = quarterly.merge(merge_year, left_index=True, right_index=True, suffixes=("", "_"))
    quarterly = quarterly[[
        "cik",
        "start",
        "end",
        "diluted_eps",
        "fiscal_year_"
    ]].rename(columns={"fiscal_year_": "fiscal_year"}).sort_values(by=["end", "start"])

    return quarterly


def annual_to_quarterly_eps(quarterly: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    annual: all records from fiscal years containing 3 quarterly reports
            and 1 annual report not in quarterly terms.

    Returns all annual reports in terms of 4th quarter EPS
    """
    quarterly = quarterly.copy()

    quarterly = quarterly.groupby("fiscal_year").filter(lambda x: (len(x) >= 4) or any(x["fiscal_year"] == max(quarterly["fiscal_year"])))
    annual_filter = (
        quarterly
        .groupby("fiscal_year")
        .transform(lambda x: len(x) == 4)["start"] 
        | ((quarterly["end"] - quarterly["start"]).apply(lambda x: x.days) <= 100)
        | (quarterly["fiscal_year"] == quarterly["fiscal_year"].max())
    )

    # quarterly should have 4 * # unique years + # quarters from current years entries
    quarterly = quarterly[annual_filter].reset_index(drop=True)

    quarterly["is_annual"] = ((quarterly["end"] - quarterly["start"]).apply(lambda x: x.days) > 100)

    annual = quarterly.groupby("fiscal_year").filter(lambda x: any(x["is_annual"]))

    annual = annual.copy()
    annual["is_annual"] = 2*annual["is_annual"] - 1
    annual["diluted_eps"] *= annual["is_annual"]

    annual_eps = annual.groupby("fiscal_year")["diluted_eps"].apply(np.sum)
    small_annual = annual.query("is_annual == 1")
    annual = (
        small_annual
        .merge(annual_eps, on="fiscal_year", suffixes=("_remove", ""))
        .drop(columns=["diluted_eps_remove"])
    )

    quarterly = quarterly[quarterly["is_annual"] == False]
    quarterly = (
        pd.concat([quarterly, annual])
        .reset_index(drop=True)
        .sort_values(by=["end"])
        .rename(columns={"is_annual": "manually_calculated"})
    )

    return quarterly


def get_quarterly_figures(c_data: dict) -> pd.DataFrame:
    quarterly = pd.DataFrame(c_data["metrics"])
    dt_cols = ["start", "end", "filing_date"]
    for cname in dt_cols:
        quarterly[cname] = pd.to_datetime(quarterly[cname], format=r"%Y-%m-%d")

    annual_forms = get_annual_forms(quarterly)
    quarterly = get_fiscal_years(annual_forms, quarterly)
    quarterly = annual_to_quarterly_eps(quarterly)
    quarterly["quarter"] = quarterly.index % 4 + 1 # 0 indexing

    return quarterly


if __name__ == "__main__":
    print("starting...")
    VERBOSE = True # run with print statements

    company_file_paths = find_valid_paths()
    company_data = generate_company_data()

    OVERWRITE = True
    if OVERWRITE:
        data_fp = "quarterly_eps_data/"
        if os.path.exists(data_fp):
            shutil.rmtree(data_fp)

        download_dir = os.path.join(os.getcwd(), "quarterly_eps_data")
        os.makedirs(download_dir, exist_ok=True)

    failed_extraction = set()
    for c_data in company_data:
        try:
            quarterly_data = get_quarterly_figures(c_data)
            cik = quarterly_data.loc[0, "cik"]
            save_fp = Path("quarterly_eps_data") / f"CIK{str(cik).zfill(10)}.csv"
            quarterly_data.to_csv(save_fp, index=False, float_format="%.15f")
            if VERBOSE:
                print(save_fp)
        except Exception as e:
            # print(e)
            try:
                cik
            except:
                # print(c_data)
                continue
            failed_extraction.add(cik)
            continue

    failed_extraction = list(failed_extraction)
    failed_extraction = pd.DataFrame(failed_extraction, columns=["cik"])
    failed_extraction.to_csv("quarterly_eps_data/_failed_extraction.csv", index=False)

    print(f"failed to extract {len(failed_extraction)} / {len(company_file_paths)} ({len(failed_extraction)/len(company_file_paths) * 100:.3f}%)")