#!/usr/bin/python2.7

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
__author__ = "Michael Shanley (Oracle A-Team)"
__copyright__ = "Copyright (c) 2016  Oracle and/or its affiliates. All rights reserved."
__version__ = "1.0.0.0"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import getopt
import os
from pprint import pprint
import sys
from urlparse import urlparse
import traceback

from oc_provision_wrappers import commerce_setup_helper 
from oc_provision_wrappers import load_user_metadata
from oc_provision_wrappers.atg import create_atg_server_layers 
from oc_provision_wrappers.atg.v11_2 import atg_helper
from oc_provision_wrappers.atg.v11_2 import atgpatch_helper
from oc_provision_wrappers.database.v12c import oracle_rdbms_install
from oc_provision_wrappers.endeca.v11_2 import cas_helper
from oc_provision_wrappers.endeca.v11_2 import mdex_helper
from oc_provision_wrappers.endeca.v11_2 import platform_helper
from oc_provision_wrappers.endeca.v11_2 import tools_helper
from oc_provision_wrappers.java import java_generic
from oc_provision_wrappers.otd.v11_1 import otd_config
from oc_provision_wrappers.otd.v11_1 import otd_helper
from oc_provision_wrappers.sshkeys import copy_ssh_keys_helper
from oc_provision_wrappers.storage import advanced_storage_helper
from oc_provision_wrappers.storage import storage_helper
from oc_provision_wrappers.wls.v12_1_3 import weblogic_create_datasources    
from oc_provision_wrappers.wls.v12_1_3 import weblogic_create_machine
from oc_provision_wrappers.wls.v12_1_3 import weblogic_create_managed_server
from oc_provision_wrappers.wls.v12_1_3 import weblogic_domain_config
from oc_provision_wrappers.wls.v12_1_3 import weblogic_domain_settings
from oc_provision_wrappers.wls.v12c import weblogic_helper
from oc_provision_wrappers.wls.v12_1_3 import weblogic_install_managed_server
from oc_provision_wrappers.wls.v12_1_3 import weblogic_packer
from oc_provision_wrappers.wls import weblogic_boot_properties
from oc_provision_wrappers.wls import weblogic_create_managed_scripts
from oc_provision_wrappers import setup_logger


sys.path.insert(0, os.path.abspath(".."))

full_path = os.path.dirname(os.path.abspath(__file__))

# root key to get from our datasource
root_json_key = 'commerceSetup' 

# url for user-data
user_data_url = "http://192.0.0.192/latest/user-data"

json_ds = None
install_java = None
install_atg = None
install_atgpatch = None
install_mdex = None
install_platform = None
install_tools = None
install_cas = None
install_otd = None
config_otd = None
copy_ssh_keys = None
add_storage = None
advanced_storage = None
install_weblogic = None
managed_wl_server = None
create_wl_domain = None
config_wl_domain = None
config_wl_ds = None
create_wl_servers = None
create_wl_machines = None
create_wl_bootfiles = None
pack_wl_domain = None
install_oracle_db = None
showDebug = None



try:
    opts, args = getopt.getopt(sys.argv[1:], '', ['java', 'addstorage', 'advancedStorage', 'weblogic', 'weblogicDomain', 'weblogicBootFiles', 'weblogicManagedServer',
                                                  'weblogicPackDomain', 'weblogicSettings', 'weblogicDatasources', 'weblogicServers', 'weblogicMachines', 'atg', 'atgpatch',
                                                  'mdex', 'platformServices', 'toolsAndFramework', 'cas', 'endeca', 'dgraph', 'otdInstall', 'otdConfig',
                                                  'copy-ssh-keys', 'db', 'debug', 'configSource='])
except getopt.GetoptError as err:
    print "Argument error", err
    sys.exit(2)

for opt, arg in opts:
    if opt in ('--mdex', '--endeca', '--dgraph'):
        install_mdex = True        
    if opt in ('--platformServices', '--endeca', '--dgraph'):
        install_platform = True        
    if opt in ('--toolsAndFramework', '--endeca'):
        install_tools = True        
    if opt in ('--cas', '--endeca'):
        install_cas = True        
    if opt == '--java':
        install_java = True        
    if opt == '--atg':
        install_atg = True
    if opt == '--atgpatch':
        install_atgpatch = True                       
    if opt == '--otdInstall':
        install_otd = True
    if opt == '--otdConfig':
        config_otd = True   
    if opt == '--copy-ssh-keys':
        copy_ssh_keys = True 
    if opt == '--addstorage':
        add_storage = True
    if opt == '--advancedStorage':
        advanced_storage = True        
    if opt == '--weblogic':
        install_weblogic = True
    if opt == '--weblogicManagedServer':
        managed_wl_server = True        
    if opt == '--weblogicDomain':
        create_wl_domain = True   
    if opt == '--weblogicPackDomain':
        pack_wl_domain = True                  
    if opt == '--weblogicSettings':
        config_wl_domain = True 
    if opt == '--weblogicDatasources':
        config_wl_ds = True            
    if opt == '--weblogicServers':
        create_wl_servers = True
    if opt == '--weblogicMachines':
        create_wl_machines = True
    if opt == '--weblogicBootFiles':
        create_wl_bootfiles = True        
    if opt == '--db':
        install_oracle_db = True
    if opt == '--debug':
        showDebug = True                                                                                              
    if opt == '--configSource':
        json_ds = arg
        
    # else:
    #    sys.exit(2)

configData = None

logger = setup_logger.setup_shared_logger('')

if json_ds == None:
    logger.info("using default json configs \n")
    json_ds = full_path + '/defaultJson/defaultConfig.json'
    configData = commerce_setup_helper.load_json_from_file(json_ds, root_json_key) 
elif json_ds == "user-data":
    logger.info("loading json from user metadata")
    configData = load_user_metadata.load_user_metadata(user_data_url, root_json_key)
elif json_ds.startswith('file'):
    logger.info("checking for file based json data")
    junk, filename = json_ds.split(":")
    file_ds = full_path + '/defaultJson/' + filename
    if os.path.isfile(file_ds):
        configData = commerce_setup_helper.load_json_from_file(file_ds, root_json_key)     
else:
    test_for_url = urlparse(json_ds)
    isUrl = bool(test_for_url.scheme)
    if isUrl: 
        logger.info("loading json from external URL")
        configData = commerce_setup_helper.load_json_from_url(json_ds, root_json_key)    

if configData == None:
    logger.error("no configution data could be loading. Exiting")
    sys.exit()
 

if showDebug:
    print 'ARGV      :', sys.argv[1:]
    pprint (configData)

if copy_ssh_keys:
    try:
        copy_ssh_keys_helper.copy_keys(configData, full_path)
    except:
        traceback.print_exc()
        pass    
    
if add_storage:
    try:
        storage_helper.mount_storage(configData, full_path)
    except:
        traceback.print_exc()
        pass    

if advanced_storage:
    try:
        advanced_storage_helper.advanced_storage(configData, full_path)
    except:
        traceback.print_exc()
        pass
       
if install_java:
    try:
        java_generic.install_java(configData, full_path) 
    except:
        traceback.print_exc()
        pass
    
if install_weblogic:
    try:
        weblogic_helper.install_weblogic(configData, full_path)
    except:
        traceback.print_exc()
        pass    
        
if create_wl_domain:
    try:
        weblogic_domain_config.create_wl_domain(configData, full_path)
    except:
        traceback.print_exc()
        pass         
    
if config_wl_domain:
    try:
        weblogic_domain_settings.config_wl_domain(configData, full_path)
    except:
        traceback.print_exc()
        pass    
    
if config_wl_ds:
    try:
        weblogic_create_datasources.config_wl_datasources(configData, full_path)
    except:
        traceback.print_exc()
        pass           
     
if create_wl_machines:
    try:
        # for adding to already running domain
        weblogic_create_machine.create_machines(configData, full_path)
    except:
        traceback.print_exc()
        pass      
    
if create_wl_servers:
    try:
        # for adding to already running domain
        weblogic_create_managed_server.create_servers(configData, full_path)
    except:
        traceback.print_exc()
        pass      

if pack_wl_domain:
    try:
        weblogic_packer.pack_domain(configData, full_path)
    except:
        traceback.print_exc()
        pass     
    
if managed_wl_server:
    try:
        weblogic_install_managed_server.unpack_domain(configData, full_path)
    except:
        traceback.print_exc()
        pass

if create_wl_bootfiles:
    try:
        weblogic_boot_properties.create_boot_properties(configData, full_path)
    except:
        traceback.print_exc()
        pass   

if managed_wl_server or create_wl_domain:
    try:
        # keep this after boot files. Without them, instances won't start
        weblogic_create_managed_scripts.create_managed_scripts(configData, full_path)
    except:
        traceback.print_exc()
        pass  
                       
if install_atg:
    try:
        atg_helper.install_atg(configData, full_path)
        # This may be useful as its own option in the future. Leave here w/ATG install for now
        create_atg_server_layers.generate_atg_server_layers(configData, full_path)
    except:
        traceback.print_exc()
        pass

if install_atgpatch:
    try:
        atgpatch_helper.install_atgpatch(configData, full_path) 
    except:
        traceback.print_exc()
        pass         
            
if install_mdex:
    try:
        mdex_helper.install_mdex(configData, full_path)
    except:
        traceback.print_exc()
        pass
    
if install_platform:
    try:
        platform_helper.install_platformServices(configData, full_path)
    except:
        traceback.print_exc()
        pass    

if install_tools:
    try:
        tools_helper.install_toolsAndFramework(configData, full_path)    
    except:
        traceback.print_exc()
        pass    
    
if install_cas:
    try:
        cas_helper.install_cas(configData, full_path)
    except:
        traceback.print_exc()
        pass    
    
if install_otd:
    try:
        otd_helper.install_otd(configData, full_path)
    except:
        traceback.print_exc()
        pass    

if config_otd:
    try:
        otd_config.config_otd(configData, full_path) 
    except:
        traceback.print_exc()
        pass         

if install_oracle_db:
    try:
        oracle_rdbms_install.install_oracle(configData, full_path)
    except:
        traceback.print_exc()
        pass    

logger.info("Setup Complete")      
