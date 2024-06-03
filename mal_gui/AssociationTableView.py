from PySide6.QtWidgets import QWidget,QTableView,QVBoxLayout
from PySide6.QtGui import QStandardItemModel,QStandardItem

import os
import csv


class AssociationDefinitions(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.associationInfo = None

        csvAssociationInfoFileName = 'AssociationInfo.csv'
        # csvAssociationInfoFileName = f'{os.getcwd()}/mal-toolbox-gui/mal_gui/AssociationInfo.csv'

        self.tableAssociationView = QTableView(self)
        
        self.associationInfoModel = QStandardItemModel()
        
        #headers for the columns
        self.associationInfoModel.setHorizontalHeaderLabels(['AssocLeftAsset', 'AssocLeftField', 'AssocName', 'AssocRightField','AssocRightAsset'])
    
        self.associationInfoModel.removeRows(0, self.associationInfoModel.rowCount())
        
        with open(csvAssociationInfoFileName, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                items = [QStandardItem(field) for field in row]
                self.associationInfoModel.appendRow(items)
         
        self.associationInfo = self.associationInfoModel
                
        self.tableAssociationView.setModel(self.associationInfoModel)
        
        layout = QVBoxLayout()
        layout.addWidget(self.tableAssociationView)
        
        # Set the layout to the widget
        self.setLayout(layout)
        
    def getAssociationInfo(self):
        return self.associationInfo
    
    
    
    
    
    
    # def loadAssociationInfoFromMarFile(self, csvEquivalentMarfileName):
    #     #Everytime before loading data , remove existing data
    #     self.associationInfoModel.removeRows(0, self.associationInfoModel.rowCount())
        
    #     with open(csvEquivalentMarfileName, 'r') as file:
    #         reader = csv.reader(csvEquivalentMarfileName)
    #         for row in reader:
    #             items = [QStandardItem(field) for field in row]
    #             self.associationInfoModel.appendRow(items)
                
        # #load data into the table
        # data = [
        #     ["Row1-Col1", "Row1-Col2", "Row1-Col3", "Row1-Col4"],
            
        #     ["Row2-Col1", "Row2-Col2", "Row2-Col3", "Row2-Col4"],
        #     ["Row3-Col1", "Row3-Col2", "Row3-Col3", "Row3-Col4"],
        # ]
        
        # for row in data:
        #     items = [QStandardItem(field) for field in row]
        #     self.model.appendRow(items)
        
        
        # # Hardware:
        # ["Hardware","hostHardware", "SysExecution" , "sysExecutedApps", "Application"],
        # ["PhysicalZone","physicalZones","ZoneInclusion","hardwareSystems","Hardware"],
        # ["Data","hostedData","DataHosting","hardware","Hardware"],
        # ["User","users","HardwareAccess","hardwareSystems","Hardware"],
        # ["HardwareVulnerability","vulnerabilities","hardwareVulnerability","hardware","Hardware"],
        
        
        # # SoftwareProduct:
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "SoftwareProduct appSoftProduct,AppSoftwareProduct,softApplications Application
        # "SoftwareVulnerability softProductVulnerabilities,ApplicationVulnerability,softwareProduct SoftwareProduct

        # # "Application:
        # "Hardware hostHardware,SysExecution,sysExecutedApps Application
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "SoftwareProduct appSoftProduct,AppSoftwareProduct,softApplications Application
        # "Application hostApp,AppExecution,appExecutedApps Application
        # "IDPS protectorIDPSs,AppProtection,protectedApps Application
        # "Data containedData,AppContainment,containingApp Application
        # "Data sentData,SendData,senderApp Application
        # "Data receivedData,ReceiveData,receiverApp Application
        # "Data dataDependedUpon,Dependence,dependentApps Application
        # "IAMObject executionPrivIAMs,ExecutionPrivilegeAccess,execPrivApps Application
        # "IAMObject highPrivAppIAMs,HighPrivilegeApplicationAccess,highPrivApps Application
        # "IAMObject lowPrivAppIAMs,LowPrivilegeApplicationAccess,lowPrivApps Application
        # "RoutingFirewall managedRoutingFw,ManagedBy,managerApp Application
        # "Network networks,NetworkExposure,applications Application
        # "Application applications,ApplicationConnection,appConnections ConnectionRule
        # "Application inApplications,InApplicationConnection,ingoingAppConnections ConnectionRule
        # "Application outApplications,OutApplicationConnection,outgoingAppConnections ConnectionRule
        # "SoftwareVulnerability vulnerabilities,ApplicationVulnerability,application Application


        # # "IDPS:
        # "Hardware hostHardware,SysExecution,sysExecutedApps Application
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "SoftwareProduct appSoftProduct,AppSoftwareProduct,softApplications Application
        # "Application hostApp,AppExecution,appExecutedApps Application
        # "IDPS protectorIDPSs,AppProtection,protectedApps Application
        # "Data containedData,AppContainment,containingApp Application
        # "Data sentData,SendData,senderApp Application
        # "Data receivedData,ReceiveData,receiverApp Application
        # "Data dataDependedUpon,Dependence,dependentApps Application
        # "IAMObject executionPrivIAMs,ExecutionPrivilegeAccess,execPrivApps Application
        # "IAMObject highPrivAppIAMs,HighPrivilegeApplicationAccess,highPrivApps Application
        # "IAMObject lowPrivAppIAMs,LowPrivilegeApplicationAccess,lowPrivApps Application
        # "RoutingFirewall managedRoutingFw,ManagedBy,managerApp Application
        # "Network networks,NetworkExposure,applications Application
        # "Application applications,ApplicationConnection,appConnections ConnectionRule
        # "Application inApplications,InApplicationConnection,ingoingAppConnections ConnectionRule
        # "Application outApplications,OutApplicationConnection,outgoingAppConnections ConnectionRule
        # "SoftwareVulnerability vulnerabilities,ApplicationVulnerability,application Application

        # # "PhysicalZone:
        # "PhysicalZone physicalZones,ZoneInclusion,hardwareSystems Hardware
        # "PhysicalZone physicalZones,ZoneInclusion,networks Network
        # "User users,ZoneAccess,physicalZones PhysicalZone

        # # "Information:
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Information infoDependedUpon,Dependence,dependentApps Application

        # # "Data:
        # "Data hostedData,DataHosting,hardware Hardware
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Data containedData,AppContainment,containingApp Application
        # "Data sentData,SendData,senderApp Application
        # "Data receivedData,ReceiveData,receiverApp Application
        # "Data dataDependedUpon,Dependence,dependentApps Application
        # "Data containingData,DataContainment,containedData Data
        # "Data transitData,DataInTransit,transitNetwork Network
        # "Credentials encryptCreds,EncryptionCredentials,encryptedData Data
        # "Credentials signingCreds,SigningCredentials,signedData Data
        # "IAMObject readingIAMs,ReadPrivileges,readPrivData Data
        # "IAMObject writingIAMs,WritePrivileges,writePrivData Data
        # "IAMObject deletingIAMs,DeletePrivileges,deletePrivData Data


        # # "IAMObject:
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "IAMObject executionPrivIAMs,ExecutionPrivilegeAccess,execPrivApps Application
        # "IAMObject highPrivAppIAMs,HighPrivilegeApplicationAccess,highPrivApps Application
        # "IAMObject lowPrivAppIAMs,LowPrivilegeApplicationAccess,lowPrivApps Application
        # "IAMObject readingIAMs,ReadPrivileges,readPrivData Data
        # "IAMObject writingIAMs,WritePrivileges,writePrivData Data
        # "IAMObject deletingIAMs,DeletePrivileges,deletePrivData Data
        # "IAMObject IAMOwners,HasPrivileges,subprivileges Privileges
        # "IAMObject managers,AccountManagement,managedIAMs IAMObject


        # # "Identity:
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "IAMObject executionPrivIAMs,ExecutionPrivilegeAccess,execPrivApps Application
        # "IAMObject highPrivAppIAMs,HighPrivilegeApplicationAccess,highPrivApps Application
        # "IAMObject lowPrivAppIAMs,LowPrivilegeApplicationAccess,lowPrivApps Application
        # "IAMObject readingIAMs,ReadPrivileges,readPrivData Data
        # "IAMObject writingIAMs,WritePrivileges,writePrivData Data
        # "IAMObject deletingIAMs,DeletePrivileges,deletePrivData Data
        # "IAMObject IAMOwners,HasPrivileges,subprivileges Privileges
        # "IAMObject managers,AccountManagement,managedIAMs IAMObject
        # "Identity identities,IdentityCredentials,credentials Credentials
        # "Identity parentId,CanAssume,childId Identity
        # "Group memberOf,MemberOf,groupIds Identity
        # "User users,UserAssignedIdentities,userIds Identity

        # # "Privileges:
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "IAMObject executionPrivIAMs,ExecutionPrivilegeAccess,execPrivApps Application
        # "IAMObject highPrivAppIAMs,HighPrivilegeApplicationAccess,highPrivApps Application
        # "IAMObject lowPrivAppIAMs,LowPrivilegeApplicationAccess,lowPrivApps Application
        # "IAMObject readingIAMs,ReadPrivileges,readPrivData Data
        # "IAMObject writingIAMs,WritePrivileges,writePrivData Data
        # "IAMObject deletingIAMs,DeletePrivileges,deletePrivData Data
        # "IAMObject IAMOwners,HasPrivileges,subprivileges Privileges
        # "IAMObject managers,AccountManagement,managedIAMs IAMObject


        # # "Group:
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "IAMObject executionPrivIAMs,ExecutionPrivilegeAccess,execPrivApps Application
        # "IAMObject highPrivAppIAMs,HighPrivilegeApplicationAccess,highPrivApps Application
        # "IAMObject lowPrivAppIAMs,LowPrivilegeApplicationAccess,lowPrivApps Application
        # "IAMObject readingIAMs,ReadPrivileges,readPrivData Data
        # "IAMObject writingIAMs,WritePrivileges,writePrivData Data
        # "IAMObject deletingIAMs,DeletePrivileges,deletePrivData Data
        # "IAMObject IAMOwners,HasPrivileges,subprivileges Privileges
        # "IAMObject managers,AccountManagement,managedIAMs IAMObject
        # "Group memberOf,MemberOf,groupIds Identity
        # "Group parentGroup,MemberOf,childGroups Group

        # # "Credentials:
        # "Data containerData,InfoContainment,information Information
        # "Data dataReplicas,Replica,replicatedInformation Information
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "Credentials encryptCreds,EncryptionCredentials,encryptedData Data
        # "Credentials signingCreds,SigningCredentials,signedData Data
        # "Identity identities,IdentityCredentials,credentials Credentials
        # "Credentials hashes,HashedCredentials,origCreds Credentials
        # "Credentials credentials,ConditionalAuthentication,requiredFactors Credentials

        # # "User:
        # "User users,HardwareAccess,hardwareSystems Hardware
        # "User users,ZoneAccess,physicalZones PhysicalZone
        # "User users,UserAssignedIdentities,userIds Identity

        # # "Network:
        # "Network networks,NetworkExposure,applications Application
        # "PhysicalZone physicalZones,ZoneInclusion,networks Network
        # "Data transitData,DataInTransit,transitNetwork Network
        # "Network networks,NetworkConnection,netConnections ConnectionRule
        # "Network inNetworks,InNetworkConnection,ingoingNetConnections ConnectionRule
        # "Network outNetworks,OutNetworkConnection,outgoingNetConnections ConnectionRule
        # "Network diodeInNetworks,DiodeInNetworkConnection,diodeIngoingNetConnections ConnectionRule

        # # "RoutingFirewall:
        # "Hardware hostHardware,SysExecution,sysExecutedApps Application
        # "Information infoDependedUpon,Dependence,dependentApps Application
        # "SoftwareProduct appSoftProduct,AppSoftwareProduct,softApplications Application
        # "Application hostApp,AppExecution,appExecutedApps Application
        # "IDPS protectorIDPSs,AppProtection,protectedApps Application
        # "Data containedData,AppContainment,containingApp Application
        # "Data sentData,SendData,senderApp Application
        # "Data receivedData,ReceiveData,receiverApp Application
        # "Data dataDependedUpon,Dependence,dependentApps Application
        # "IAMObject executionPrivIAMs,ExecutionPrivilegeAccess,execPrivApps Application
        # "IAMObject highPrivAppIAMs,HighPrivilegeApplicationAccess,highPrivApps Application
        # "IAMObject lowPrivAppIAMs,LowPrivilegeApplicationAccess,lowPrivApps Application
        # "RoutingFirewall managedRoutingFw,ManagedBy,managerApp Application
        # "Network networks,NetworkExposure,applications Application
        # "Application applications,ApplicationConnection,appConnections ConnectionRule
        # "Application inApplications,InApplicationConnection,ingoingAppConnections ConnectionRule
        # "Application outApplications,OutApplicationConnection,outgoingAppConnections ConnectionRule
        # "SoftwareVulnerability vulnerabilities,ApplicationVulnerability,application Application
        # "RoutingFirewall routingFirewalls,FirewallConnectionRule,connectionRules ConnectionRule

        # # "ConnectionRule:
        # "Application applications,ApplicationConnection,appConnections ConnectionRule
        # "Application inApplications,InApplicationConnection,ingoingAppConnections ConnectionRule
        # "Application outApplications,OutApplicationConnection,outgoingAppConnections ConnectionRule
        # "Network networks,NetworkConnection,netConnections ConnectionRule
        # "Network inNetworks,InNetworkConnection,ingoingNetConnections ConnectionRule
        # "Network outNetworks,OutNetworkConnection,outgoingNetConnections ConnectionRule
        # "Network diodeInNetworks,DiodeInNetworkConnection,diodeIngoingNetConnections ConnectionRule
        # "RoutingFirewall routingFirewalls,FirewallConnectionRule,connectionRules ConnectionRule


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Vulnerability:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SoftwareVulnerability:
# SoftwareVulnerability softProductVulnerabilities,ApplicationVulnerability,softwareProduct SoftwareProduct
# SoftwareVulnerability vulnerabilities,ApplicationVulnerability,application Application
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HardwareVulnerability:
# HardwareVulnerability vulnerabilities,hardwareVulnerability,hardware Hardware



        
        