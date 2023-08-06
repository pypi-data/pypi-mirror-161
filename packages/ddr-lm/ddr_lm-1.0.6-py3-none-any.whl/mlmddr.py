"""
The lmddr module provides the sdk to prepare a network for DDR. It can deploy the basic DDR infra on all the devices, deploy the use cases (scripts),
and execute the use cases.
"""

from enum import Enum
from os import path

import time
import re
import json

from radkit_common.nglog import debug, warning, info, error, basicConfig, DEBUG

from typing import Optional, Union, List, Dict

from radkit_client.client import *
from radkit_client.device import DeviceDict, Device

from lmautomation import Automation, scp_upload_from_buffer, Model
#import lmerrors
import radkit_client.helpers as lmerrors

basicConfig()


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def deploy_xe_infra(device_list: DeviceDict, usecase: Automation) -> None:
    """
    Deploys the DDR infra on all the XE devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR XE Infra Deploy: DDR Infra Deployment Started")

    flow = lmerrors.DeviceFlow(device_list)
       
    ###################
    # CONFIG SCP SERVER
    ###################

    info("DDR XE Infra Deploy: enable scp") #PVH
    scp_con = flow.exec_wait(["config terminal", "ip scp server enable", "exit"], timeout=300)
    info("DDR XE Infra Deploy: enable scp complete")

    #################################
    # ENABLE GUESTSHELL IN THE DEVICE
    #################################

    try:
        info(
            "DDR XE Infra Deploy: DDR Guestshell Installation Started, may take few minutes"
        )
        g_enable = flow.exec_wait("guestshell enable", timeout=300)
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section enable guestshell in the device"
            + " "
            + str(e)
            + Color.END
        )


    ################################################
    # VERIFY THE GUESTSHELL IS ENABLED IN THE DEVICE
    ################################################

    try:
        g_enable = flow.exec_wait("guestshell enable", timeout=300)
        for result in g_enable.result.values():
            g_enable_list = result.data.split("\n")

        if "Guestshell enabled successfully" in g_enable_list:
            info("DDR XE Infra Deploy: Guestshell Enabled Successfully")
        else:
            raise ValueError(
                "DDR XE Infra Deploy: Guestshell not enabled,, terminating the session\n"
            )
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section verify guestshell in the device"
            + " "
            + str(e)
            + Color.END
        )
                       
    #################################
    # CONFIG THE Passwordless NETCONF
    #################################

    try:
        info("DDR XE Infra Deploy: enable passwordless NETCONF") #PVH
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "iosp_client -c 'netconf-yang' -f netconf_enable guestshell 830", "iosp_client -f netconf_enable_passwordless guestshell guestshell", "exit"],
            exec_error_regex=[],
        )
        info("DDR XE Infra Deploy: enable passwordless NETCONF complete") #PVH

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Infra Deploy: An Exception occured in Passwordless NETCONF enable in the guestshell"
            + " "
            + str(e)
            + Color.END
        )
        
    #######################
    # CREATE the /bootflash/guest-share/ddr directory for DDR execution
    #######################

    try:
        info("DDR XE Infra Deploy: create guest-share ddr directory") #PVH
        ddr_engine_ins = flow.exec_wait(
            ["guestshell", "cd /bootflash", "mkdir guest-share", "cd guest-share", "mkdir ddr", "exit"],
            exec_error_regex=[],
        )
        info("DDR XE Infra Deploy: create guest-share ddr directory complete") #PVH

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Infra Deploy: An Exception occured creating /bootflash/guest-share/ddr directory"
            + " "
            + str(e)
            + Color.END
        )
    
    ###################################
    # COPY THE DDR ENGINE TO THE DEVICE
    ###################################
    try:
        basedir_infr_files = "./files/infra-files"
        class_file = path.join(basedir_infr_files, "ddrclass.py")
        run_file = path.join(basedir_infr_files, "ddrrun.py")
        gp_file = path.join(basedir_infr_files, "genie_parsers.py")
        lib_file = path.join(basedir_infr_files, "ddrlib.py")
        whl_file = path.join(basedir_infr_files, "ddr-python.tar.gz")

        for device in flow.active_devices.values():
            info("DDR XE Infra Deploy: Install DDR Python libraries")
            debug(f"{device.name}: Uploading infra files")
            w_file = device.scp_upload_from_file(
                whl_file, "bootflash:/guest-share/ddr/ddr-python.tar.gz"
            ).wait()
            debug("ddr-python.tar.gz done")
            l_file = device.scp_upload_from_file(
                lib_file, f"bootflash:/guest-share/ddr/ddrlib.py"
            )
            debug("ddrlib.py done")
            c_file = device.scp_upload_from_file(
                class_file, "bootflash:/guest-share/ddr/ddrclass.py"
            ).wait()
            debug("ddrclass.py done")
            d_file = device.scp_upload_from_file(
                run_file, "bootflash:/guest-share/ddr/ddrrun.py"
            ).wait()
            debug("ddrrun.py done")
            g_file = device.scp_upload_from_file(
                gp_file, "bootflash:/guest-share/ddr/genie_parsers.py"
            ).wait()
            debug("genie_parsers.py done")
            info("DDR XE Infra Deploy: Install DDR Python libraries complete")

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section copy the ddr engine files - uploading to bootflash"
            + " "
            + str(e)
            + Color.END
        )

    ##########################################
    # INSTALL PYTHON PACKAGES AND DEPENDENCIES
    ##########################################

    try:
        info("DDR XE Infra Deploy: Install DDR Python Packages and Dependencies - May require several minutes")

        export_ins1 = flow.exec_wait(
                [
                    "guestshell",
                    "tar -xvf /bootflash/guest-share/ddr/ddr-python.tar.gz",
                    "python3 -m pip install pip-21.3.1-py3-none-any.whl --user",
                    "python3 -m pip install pycparser-2.21-py2.py3-none-any.whl --user",
                    "python3 -m pip install ddr_python-0.1.43-py3-none-any.whl --user",
                    "python3 -m pip install ptyprocess-0.7.0-py2.py3-none-any.whl --user",
                    "python3 -m pip install pexpect-4.8.0-py2.py3-none-any.whl --user",
                    "python3 -m pip install ncclient-0.6.9-py2.py3-none-any.whl --user",
                    "python3 -m pip install xmltodict-0.13.0-py2.py3-none-any.whl --user",
                    "python3 -m pip install regex-2022.6.2-cp36-cp36m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl --user",
                    "setuptools-59.6.0-py3-none-any.whl",
                    "rm pip-21.3.1-py3-none-any.whl",
                    "rm pycparser-2.21-py2.py3-none-any.whl",
                    "rm ddr_python-0.1.43-py3-none-any.whl",
                    "rm ptyprocess-0.7.0-py2.py3-none-any.whl",
                    "rm pexpect-4.8.0-py2.py3-none-any.whl",
                    "rm ncclient-0.6.9-py2.py3-none-any.whl",
                    "rm xmltodict-0.13.0-py2.py3-none-any.whl",
                    "rm regex-2022.6.2-cp36-cp36m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
                    "exit"],
                timeout=120
        )
        info("DDR XE Infra Deploy: Install DDR Python Packages and Dependencies complete")

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in the section install python pkgs and dependencies"
            + " "
            + str(e)
            + Color.END
        )

    info("DDR XE Infra Deploy: DDR Infra Deployment Complete")

def deploy_xe_configs(device_list: DeviceDict, usecase: Automation) -> None:
    """
    Deploys the DDR configs on all the XE devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    flow = lmerrors.DeviceFlow(device_list)
    
    ###########################
    # DDR INITIAL BASIC CONFIGS
    ###########################

    # Configuring IOS
    info("DDR XE Infra Deploy: Add configurations for NETCONF notifications")

    try:
        ios_config1 = flow.exec_wait(
            [
                "delete /force flash:saved-before-ddr-configuration",
                "copy running-config flash:saved-before-ddr-configuration"
            ]
        )

        ios_config2 = flow.exec_wait(
            [
                "config t",
                "\n",
                "logging history debugging",
                "logging snmp-trap emergencies",
                "logging snmp-trap alerts",
                "logging snmp-trap critical",
                "logging snmp-trap errors",
                "logging snmp-trap warnings",
                "logging snmp-trap notifications",
                "logging snmp-trap informational",
                "snmp-server enable traps syslog",
                "snmp-server manager",
                "netconf-yang",
                "netconf-yang cisco-ia snmp-trap-control trap-list 1.3.6.1.4.1.9.9.41.2.0.1",
                "ip scp server enable",
                "ip ssh version 2",
                "exit",
                "exit"
            ]
        )


    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Configs Deploy: An Exception occured in the section ddr device basic configs"
            + " "
            + str(e)
            + Color.END
        )

    info("DDR XE Infra Deploy: Add configurations for NETCONF notifications complete")

def deploy_xe_use_case(device_list: DeviceDict, usecase: Automation) -> None:
    """
    Deploys the DDR usecase files on all the XE devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    flow = lmerrors.DeviceFlow(device_list)

    ######################################
    # UPLOAD THE DDR FILES INTO THE DEVICE
    ######################################

    info("DDR XE Workflow Deploy: Start DDR Workflow deployment to device")

    try:
        if usecase.model is Model.CLIPS:

            guestshell = flow.exec_wait(
                [
                    "guestshell",
                    "cd /bootflash/guest-share/ddr/",
                    f"mkdir {usecase.name}",
                    "exit",
                ],
                timeout=300,
            )
#PVH
        # Required ddr CLIPs control files
        
            cp_d_dire = "bootflash:/guest-share/ddr/{}/ddr-devices".format(usecase.name)
            cp_f_dire = "bootflash:/guest-share/ddr/{}/ddr-facts".format(usecase.name)
            cp_fl_dire = "bootflash:/guest-share/ddr/{}/ddr-flags".format(usecase.name)
            cp_r_dire = "bootflash:/guest-share/ddr/{}/ddr-rules".format(usecase.name)

            debug("Deploying files")
            scp_upload_from_buffer(flow, cp_f_dire, "664", usecase.elements["facts"])
            scp_upload_from_buffer(flow, cp_fl_dire, "664", usecase.elements["flags"])
            scp_upload_from_buffer(flow, cp_r_dire, "664", usecase.elements["rules"])

        # Optional ddr CLIPs control files
            
            try:
                cp_tests = "bootflash:/guest-share/ddr/{}/ddr-tests".format(usecase.name)
                scp_upload_from_buffer(flow, cp_tests, "664", usecase.elements["tests"])
            except: pass            

            try:
                cp_init = "bootflash:/guest-share/ddr/{}/ddr-init".format(usecase.name)
                scp_upload_from_buffer(flow, cp_init, "664", usecase.elements["init"])
            except: pass            

            try:
                cp_sim = "bootflash:/guest-share/ddr/{}/ddr-sim".format(usecase.name)
                scp_upload_from_buffer(flow, cp_sim, "664", usecase.elements["sim"])
            except: pass            

        else: # usecase.model is Model.PYTHON:

            guestshell = flow.exec_wait(
                [
                    "guestshell",
                    "cd /bootflash/guest-share/ddr/",
                    f"mkdir {usecase.name}",
                    "exit",
                ],
                timeout=300,
            )


            script = f"{usecase.name}.py"
            bootflash_target = f"bootflash:/guest-share/ddr/{usecase.name}/{script}"
            debug("Deploying files")
            scp_upload_from_buffer(
                flow, bootflash_target, "664", usecase.elements["script"]
            )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Use Case Files Deploy: An Exception occured in the section upload the ddr files into the device"
            + " "
            + str(e)
            + Color.END
        )

    info("DDR XE Workflow Deploy: DDR Workflow deployment to device complete")
  
def execute_use_case(device_list: DeviceDict, usecase: Automation) -> None:

    """
    Exectues DDR use-case on all the devices in the inventory passed as parameter. This function assumes the DDR infra and use cases where
    deployed.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR use case needs to be ran

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    flow = lmerrors.DeviceFlow(device_list)

    try:
        if usecase.model is Model.CLIPS:

            info("DDR Use Case Execute: Executing DDR CLIPS Use Case")
#PVH add other clips files
            exec_cmd = f"guestshell run python3 ddr/ddrrun.py --flags=/bootflash/guest-share/ddr/{usecase.name}/ddr-flags --facts=/bootflash/guest-share/ddr/{usecase.name}/ddr-facts --rules=/bootflash/guest-share/ddr/{usecase.name}/ddr-rules --devices=/bootflash/guest-share/ddr/{usecase.name}/ddr-devices"

#            exec_cmd = f"guestshell run python3 ddr/ddrrun.py --flags=/bootflash/guest-share/ddr/{usecase.name}/ddr-flags --facts=/bootflash/guest-share/ddr/{usecase.name}/ddr-facts --rules=/bootflash/guest-share/ddr/{usecase.name}/ddr-rules --devices=/bootflash/guest-share/ddr/{usecase.name}/ddr-devices --tests=/bootflash/guest-share/ddr/{usecase.name}/ddr-tests --init=/bootflash/guest-share/ddr/{usecase.name}/ddr-init --sim=/bootflash/guest-share/ddr/{usecase.name}/ddr-sim"                                "

            ddr_execute = flow.exec_wait(exec_cmd, timeout=10000)

        else: # usecase.model is Model.PYTHON:
            script = f"{usecase.name}.py"
            info(f"DDR Use Case Execute: Executing DDR Python Use Case: {usecase.name}/{script}")
            ddr_execute = flow.exec_wait(
                f"guestshell run python3 /bootflash/guest-share/ddr/{usecase.name}/{script}",
                timeout=10000,
            )

        for result in ddr_execute.result.values():
            debug(result.data)

        info("DDR Use Case Execute: DDR Use Case Execution Completed")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Use Case Execute: An Exception occured in the section ddr use case execute"
            + " "
            + str(e)
            + Color.END
        )

def collect_xe_data(device_list: DeviceDict, usecase: Automation, return_data=False) -> Union[dict, None]:

    """
    Collect the service impact notification logs generated by the DDR engine in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    info("DDR Collect XE Data: Save Use Case Results")
    flow = lmerrors.DeviceFlow(device_list)
    ######################################################
    # OBTAIN THE DDR SERVICE IMPACT NOTIFICATION LOG FILES
    ######################################################

    try:
        log_path = "bootflash:/guest-share"
#PVH update log processing for CLIPS
        if usecase.model is Model.CLIPS:
            all_files = flow.exec_wait("dir bootflash:/guest-share/")
            for result in all_files.result.values():
                all_files_list = result.data.split("\n")
            first_file = all_files_list[3]
            first_file = first_file.split(" ")
            fn = first_file[-1:]
            for f in fn:
                rt_ins1 = flow.exec_wait(
                    [
                        "guestshell",
                        f"cp /bootflash/guest-share/{f} /bootflash/guest-share/ddr/{usecase.name}/",
                        "exit",
                    ],
                    timeout=300,
                )
                log_path = f"more bootflash:/guest-share/ddr/{usecase.name}/{f}"

#
# DDR Python usecase logs are stored in the use case directory
# Get the most recent use case log which will be the first in the directory
# Return the path to the most recent usecase log
#
# ddmi-cat9300-2#dir bootflash:/guest-share/ddr/pybasic
#   Directory of flash:/guest-share/ddr/pybasic/
#   
#   622646  -rw-             3865   Jul 9 2022 04:21:41 +00:00  DDR-pybasic_TS_07-09-2022_04:21:40.926458
#   622642  -rw-             1422   Jul 9 2022 04:21:34 +00:00  pybasic.py
#   622645  -rw-             3865   Jul 9 2022 04:15:46 +00:00  DDR-pybasic_TS_07-09-2022_04:15:45.550075
#   622644  -rw-             3865   Jul 9 2022 04:03:37 +00:00  DDR-pybasic_TS_07-09-2022_04:03:37.288569
#
# The use case filename is the last token in the line
#
        elif usecase.model is Model.PYTHON:
            log_files = f"dir bootflash:/guest-share/ddr/{usecase.name}"
            all_files = flow.exec_wait(log_files, timeout=100)
            for result in all_files.result.values():
                all_files_list = result.data.split("\n")

            pattern = ".*_TS_.*"
            for ddr_log in all_files_list:
                result = re.match(pattern, ddr_log)
                if result:
                    dir_tokens = ddr_log.split(" ")
                    filename = dir_tokens[-1:]
                    log_path = f"more bootflash:/guest-share/ddr/{usecase.name}/" + str(filename[0])
                    log_content = flow.exec_wait(log_path, timeout=100)
                    break # Exit after selecting most recent use case log
            
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect XE Data: An Exception occured in the section collect the use case logs: Verify DDR infra deployed correctly"
            + " "
            + str(e)
            + Color.END
        )

    info(f"DDR Collect XE Data: DDR Use Case Execution Logs saved in /bootflash/guest-share/ddr/{usecase.name}/")

    ###############################################
    # PRINT THE DDR SERVICE IMPACT NOTIFICATION LOG
    ###############################################

    try:
        if log_path:
            action_func = flow.exec_wait(log_path, timeout=10000)
            if usecase.model is Model.CLIPS:
                return {
                    device.name: json.loads(
                        json.dumps("".join(action_func.result[device.name].data.split("\n")[1:]))
                    )
                    for device in flow.active_devices.values()
                }
            elif usecase.model is Model.PYTHON:
                return {
                    device.name: json.loads(
                        json.dumps("".join(action_func.result[device.name].data.split("\n")[1:]))
                    )
                    for device in flow.active_devices.values()
                }
            else:
                info(f"DDR Collect XE Data: Model type passed is invalid")
                raise ValueError("Invalid model")
                return {}
        else:
            info (f"DDR Collect XE Data: No DDR Use Case Log Stored")
            raise ValueError("No DDR Use Case Stored")

        info("DDR Collect XE Data: DDR Collect Data Execution Ended")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect XE Data: An Exception occured in the section print the DDR use case logs"
            + " "
            + str(e)
            + Color.END
        )

def collect_xe_log(device_list: DeviceDict, usecase: Automation, return_data=False) -> Union[dict, None]:

    """
    Collect the service impact notification logs generated by the DDR engine in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    info("DDR Collect XE Data: Save Use Case Results")
    flow = lmerrors.DeviceFlow(device_list)
    ######################################################
    # OBTAIN THE DDR SERVICE IMPACT NOTIFICATION LOG FILES
    ######################################################

    try:
        log_path = "bootflash:/guest-share"
#PVH update log processing for CLIPS
        if usecase.model is Model.CLIPS:
            all_files = flow.exec_wait("dir bootflash:/guest-share/")
            for result in all_files.result.values():
                all_files_list = result.data.split("\n")
            first_file = all_files_list[3]
            first_file = first_file.split(" ")
            fn = first_file[-1:]
            for f in fn:
                rt_ins1 = flow.exec_wait(
                    [
                        "guestshell",
                        f"cp /bootflash/guest-share/{f} /bootflash/guest-share/ddr/{usecase.name}/",
                        "exit",
                    ],
                    timeout=300,
                )
                log_path = f"bootflash:/guest-share/ddr/{usecase.name}/{f}"
                info(f"DDR Collect XE Log: DDR Use Case Execution Logs saved in /bootflash/guest-share/ddr/{usecase.name}/{f}")
                return log_path

#
# DDR Python usecase logs are stored in the use case directory
# Get the most recent use case log which will be the first in the directory
# Return the path to the most recent usecase log
#
# ddmi-cat9300-2#dir bootflash:/guest-share/ddr/pybasic
#   Directory of flash:/guest-share/ddr/pybasic/
#   
#   622646  -rw-             3865   Jul 9 2022 04:21:41 +00:00  DDR-pybasic_TS_07-09-2022_04:21:40.926458
#   622642  -rw-             1422   Jul 9 2022 04:21:34 +00:00  pybasic.py
#   622645  -rw-             3865   Jul 9 2022 04:15:46 +00:00  DDR-pybasic_TS_07-09-2022_04:15:45.550075
#   622644  -rw-             3865   Jul 9 2022 04:03:37 +00:00  DDR-pybasic_TS_07-09-2022_04:03:37.288569
#
# The use case filename is the last token in the line
#
        elif usecase.model is Model.PYTHON:
            log_files = f"dir bootflash:/guest-share/ddr/{usecase.name}"
            all_files = flow.exec_wait(log_files, timeout=10000)
            for result in all_files.result.values():
                all_files_list = result.data.split("\n")

            pattern = ".*_TS_.*"
            for ddr_log in all_files_list:
                result = re.match(pattern, ddr_log)
                if result:
                    dir_tokens = ddr_log.split(" ")
                    filename = dir_tokens[-1:]
                    filestring = filename[0]
                    log_path = f"bootflash:/guest-share/ddr/{usecase.name}/" + str(filename[0])
                    info(f"DDR Collect XE Log: DDR Use Case Execution Logs saved in /bootflash/guest-share/ddr/{usecase.name}/{filestring}")
                    return log_path
            
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect XE Data: An Exception occured in the section collect the use case logs"
            + " "
            + str(e)
            + Color.END
        )

    ###############################################
    # PRINT THE DDR SERVICE IMPACT NOTIFICATION LOG
    ###############################################

    try:
        if log_path:
            action_func = flow.exec_wait(log_path, timeout=10000)
            if usecase.model is Model.CLIPS:
                return {
                    device.name: json.loads(
                        json.dumps("".join(action_func.result[device.name].data.split("\n")[1:]))
                    )
                    for device in flow.active_devices.values()
                }
            elif usecase.model is Model.PYTHON:
                return {
                    device.name: json.loads(
                        json.dumps("".join(action_func.result[device.name].data.split("\n")[1:]))
                    )
                    for device in flow.active_devices.values()
                }
            else:
                info(f"DDR Collect XE Data: Model type passed is invalid")
                raise ValueError("Invalid model")
                return {}
        else:
            info (f"DDR Collect XE Data: No DDR Use Case Log Stored")
            raise ValueError("No DDR Use Case Stored")

        info("DDR Collect XE Data: DDR Collect Data Execution Ended")
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect XE Data: An Exception occured in the section print the DDR use case logs"
            + " "
            + str(e)
            + Color.END
        )

def collect_data(device_list: DeviceDict, usecase: Automation) -> Union[dict, None]:

    """
    Collect the service impact notification logs generated by the DDR engine in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """

    info("DDR Collect Data: DDR Collect Data Execution Started\n")
    flow = lmerrors.DeviceFlow(device_list)
    
    #######################################################
    # EXECUTE THE OS INFRA BASED ON THE OS VERSION DETECTED
    #######################################################

    try:
        xedevices = []
        flow.exec_wait("\x1a")
        ver_check = flow.exec_wait("show version", timeout=300)
        for device in flow.active_devices.values():
            if "Cisco IOS XE Software" in ver_check.result[device.name].data:
                xedevices.append(device.name)
                device.attributes.ephemeral['os']='iosxe'
            else:
                raise ValueError(
                f"DDR Infra Deploy: Valid Cisco OS Version not detected in device - {device.name}, terminating the session\n"
            )

        xe_dict = flow.active_devices.subset(xedevices)

        if xe_dict:
            info(collect_xe_data(xe_dict, usecase))

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Collect Data: An Exception occured in the section verify cisco os version on the device"
            + " "
            + str(e)
            + Color.END
        )


def cleanup_infra(device_list: DeviceDict):

    """
    Cleans the DDR infra on all the devices in the inventory passed as parameter.

    :device_list: an DeviceDictionary containing the list of devices on which the DDR infra needs to be deployed

    :returns: nothing
    :raises: Lazy Meastro exception in case the connectivity is fully lost during deployment.
    """
    info("DDR Clean Deploy: DDR Clean Deployment Started")
    flow = lmerrors.DeviceFlow(device_list)

    #####################################
    # REMOVE THE DDR FILES FROM THE FLASH
    #####################################

    try:
        delete_files = flow.exec_wait(
            [
                "delete /force bootflash:/guest-share/ddr/ddrclass.py",
                "delete /force bootflash:/guest-share/ddr/ddrrun.py",
                "delete /force bootflash:/guest-share/ddr/genie_parsers.py",
                "delete /force bootflash:/guest-share/ddr/ddrlib.py",
                "delete /force bootflash:/guest-share/ddr/ddr-python.tar.gz",
                "delete /force bootflash:/guest-share/ddr/ddr-pytest.tar.gz"
            ],
            exec_error_regex=[],
        )

    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR Clean Deploy: An Exception occured in the section remove the ddr files from the flash"
            + " "
            + str(e)
            + Color.END
        )
#PVH
#    try:
#        ddr_engine_ins = flow.exec_wait(
#            ["guestshell", "cd /home/guestshell/", "rm -rf *", "exit"],
#            exec_error_regex=[],
#        )

#    except Exception as e:
#        raise Exception(
#            Color.BOLD
#            + Color.RED
#            + f"DDR Clean Deploy: An Exception occured in the section remove the ddr dir from the guestshell" 
#            + " "
#            + str(e)
#            + Color.END
#        )

    info(f"DDR Remove: DDR Runtime is removed from device")


def restore_xe_config(device_list: DeviceDict):

    ###################################################
    # COPY THE RUNNING CONFIGS BEFORE THE DDR INSTALLED
    ###################################################

    flow = lmerrors.DeviceFlow(device_list)

    try:
        copy_run_configs = flow.exec_wait(
            ["config replace flash:saved-before-ddr-configuration force",
             "delete /force flash:saved-before-ddr-configuration"
            ],
            exec_error_regex=[],
        )
        info("DDR Device running-config restored: DDR applied configurations removed")
    except Exception as e:
        raise Exception (
            Color.BOLD
            + Color.RED
            + f"DDR Clean Deploy: An Exception occured in restore_xe_config"
            + " "
            + str(e)
            + Color.END
        )
        
def guestshell_remove(device_list: DeviceDict):

    #################################
    # REMOVE GUESTSHELL IN THE DEVICE
    #################################

    flow = lmerrors.DeviceFlow(device_list)

    try:
        info("DDR Remove: Guestshell Removed from device")
        
        g_enable = flow.exec_wait("guestshell destroy", timeout=300)
    except Exception as e:
        raise Exception(
            Color.BOLD
            + Color.RED
            + f"DDR XE Infra Deploy: An Exception occured in guestshell_remove from the device"
            + " "
            + str(e)
            + Color.END
        )

