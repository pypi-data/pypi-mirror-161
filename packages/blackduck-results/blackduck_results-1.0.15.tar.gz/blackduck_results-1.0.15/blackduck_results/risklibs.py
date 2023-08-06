"""
Report the offending libraries from a given project,version in a short format suitable for jira/slack notifications. Include all subprojects.

@Author: Fabio Arciniegas <fabio_arciniegas@trendmicro.com>

Based on samples from synopsys hub blackduck api by @author: gsnyder
"""

import argparse
from io import StringIO
from blackduck.HubRestApi import HubInstance
import pandas as pd
import os
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def cli():
    """
    Parse parameters from cli and invoke report function
    """
    parser = argparse.ArgumentParser(
        description=
        """Report the offending libraries from a given project+version in a short format suitable for jira/slack notifications. Note blackduck connection depends on a .restconfig.json file which must be present in the current directory. It's format is: 

        {
        "baseurl": "https://foo.blackduck.xyz.com",
        "api_token": "YOUR_TOKEN_HERE",
        "insecure": true,
        "debug": false
        }

""")
    parser.add_argument("project_name")
    parser.add_argument("version_name")
    parser.set_defaults(operational=False)
    parser.add_argument("-c",
                        "--cutoff",
                        default="high",
                        choices=["medium", "high", "critical", "low"],
                        help="Minimum level of risk to report")
    parser.add_argument("-f",
                        "--format",
                        default="SHORT",
                        choices=["SHORT", "PANDAS", "CSV", "JSON", "HTML"],
                        help="Report format")
    parser.add_argument(
        "--tree",
        dest="tree",
        action="store_true",
        help=
        "Print tree of subprojects as stats are being gathered. POSIX exit codes for OK, DATA_ERR, CONFIG (0,65,78). "
    )
    parser.set_defaults(tree=False)


    parser.add_argument(
        "--urls",
        dest="urls",
        action="store_true",
        help=
        "Print url of offending components as part of output"
    )
    parser.set_defaults(urls=False)
    
    args = parser.parse_args()
    headers = {
        "c": "Component",
        "v": "Version",
        "critical": "Critical Security Risk",
        "high": "High Security Risk",
        "medium": "Medium Security Risk",
        "low": "Low Security Risk",
        "os": "Operational Risk"
    }

    df = None
    tree = 0 if args.tree else -1
    try:
        df = stats(args.project_name, args.version_name, args.operational,
                   args.cutoff, headers, tree)
    except NameError as e:
        eprint(e)
        sys.exit(os.EX_DATAERR)
    except Exception as e:
        eprint(e)
        sys.exit(os.EX_CONFIG)

    summarize_and_output(df, args.cutoff, headers, args.format, args.urls)
    sys.exit(os.EX_OK)


def summarize_and_output(df, cutoff, headers, style="SHORT", urls=True):
    if df is None:
        return
    df['Total'] = df.loc[:, headers["critical"]:headers[cutoff]].sum(axis=1)
    output_results(df[df['Total'] > 0], style, urls)


def output_results(df_unsorted, style="SHORT", urls=True):
    """
    Format a dataframe with the results
    """
    df = df_unsorted.sort_values(by=['Component'])
    if style == "SHORT":
        for index, rec in df.iterrows():
            url = "" if not urls else rec['URL']
            print(f"{rec['Project']} {rec['Component']} {rec['Version']} {url}")
    if style == "HTML":
        if df.empty:
            return
        print("<ul>")
        last_group = None
        for index, rec in df.iterrows():
            if last_group != rec['Component']:
                print(f"<li><a href='{rec['URL']}'>{rec['Component']} {rec['Version']}</a> affects ")
                last_group = rec['Component']
            print(rec['Project'] + " ")
        print("</ul>")
    if style == "PANDAS":
        print(df.to_string(index=False, header=False))
    if style == "CSV":
        output = StringIO()
        df.to_csv(output, index=False, header=False)
        print(output.getvalue())
    if style == "JSON":
        output = StringIO()
        df.to_json(output, orient="records")
        print(output.getvalue())


def stats(
        project_name,
        version_name,
        operational,
        cutoff,
        headers={
            "c": "Component",
            "v": "Version",
            "critical": "Critical Security Risk",
            "high": "High Security Risk",
            "medium": "Medium Security Risk",
            "low": "Low Security Risk",
        },
        tree=-1):
    """
    Return a pandas frame with the stats of the project.
    :param str project: The project name in blackduck
    :param str version: The version name in blackduck
    :param bool operational: whether to include operational risks (security risks only otherwise)
    :param dict headers: headers for resulting frame
    :param int tree : level of indentation fo tree print -1 for no tree
    """
    hub = HubInstance()
    project = hub.get_project_by_name(project_name)
    if not project:
        raise NameError("Project name invalid/not found.")

    version = hub.get_version_by_name(project, version_name)
    if not version:
        raise NameError("Version name invalid/not found.")

    bom_components = None

    try:
        bom_components = hub.get_version_components(version, limit=999)
    except Exception as e:
        print(e)
        raise RuntimeError("Configuration file for Synopsys Blackduck missing or invalid, Consult https://github.com/blackducksoftware/hub-rest-api-python/blob/master/blackduck/HubRestApi.py")

    projectlist = []
    compnamelist = []
    compversionlist = []
    compurllist = []
    critsecrisklist = []
    highsecrisklist = []
    medsecrisklist = []
    lowsecrisklist = []

    total_df = pd.DataFrame({
        'Project': [],
        'Component': [],
        'Version': [],
        'URL': [],
        headers["critical"]: [],
        headers["high"]: [],
        headers["medium"]: [],
        headers["low"]: [],
    })

    for bom_components in bom_components['items']:
        if len(bom_components['activityData']) == 0:
            if tree > -1:
                eprint(("\t"*tree)+bom_components['componentName'])
            total_df = pd.concat([
                total_df,
                stats(bom_components['componentName'],
                      bom_components['componentVersionName'],
                      operational,
                      cutoff="low",
                      headers=headers, tree= tree+1 if tree >-1 else -1)])
            continue

        projectlist.append(project_name)
        securityRiskProfile = bom_components['securityRiskProfile']
        compname = bom_components['componentName']
        compnamelist.append(compname)
        compversion = bom_components['componentVersionName']
        compversionlist.append(compversion)
        compurl = bom_components['componentVersion']
        compurllist.append(compurl)
        lowsecrisk = securityRiskProfile['counts'][2]['count']
        lowsecrisklist.append(lowsecrisk)
        medsecrisk = securityRiskProfile['counts'][3]['count']
        medsecrisklist.append(medsecrisk)
        highsecrisk = securityRiskProfile['counts'][4]['count']
        highsecrisklist.append(highsecrisk)
        critsecrisk = securityRiskProfile['counts'][5]['count']
        critsecrisklist.append(critsecrisk)

    df = pd.DataFrame({
        'Project': projectlist,
        'Component': compnamelist,
        'Version': compversionlist,
        'URL': compurllist,
        headers["critical"]: critsecrisklist,
        headers["high"]: highsecrisklist,
        headers["medium"]: medsecrisklist,
        headers["low"]: lowsecrisklist,
    })

    total_df = pd.concat([total_df, df])
    if cutoff == "medium":
        total_df.drop(columns=[headers["low"]], inplace=True)
    if cutoff == "high":
        total_df.drop(columns=[headers["medium"], headers["low"]],
                      inplace=True)
    if cutoff == "critical":
        total_df.drop(
            columns=[headers["medium"], headers["low"], headers["high"]],
            inplace=True)
    return total_df.drop_duplicates()


if __name__ == "__main__":
    cli()
