#! python
import sys
import purestorage
import requests
import time
import logging
import smtplib
from email.mime.text import MIMEText

#get start timespamp for email notification
starttime = time.localtime(time.time())
starttime = time.strftime("%y/%m/%d %H:%M", starttime)


#Send email with start time
startmsg = MIMEText("Reporting Database Snap started at: " + starttime)
sender ='PURE01@CO.ORG'
recipient = 'DatabaseTeam@CO.ORG,storageadmin@co.org'
startmsg['Subject'] = 'Reporting Database Snap Started'
startmsg['From'] = sender
startmsg['To'] = recipient
mailserver = smtplib.SMTP('smtp.co.org')
mailserver.sendmail(sender, recipient.split(','), startmsg.as_string())
mailserver.quit()



#Set up logging file
logging.basicConfig(filename='dbsnap-python.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('--------------------Script Started------------------------')



#Disable certificate warnings
requests.packages.urllib3.disable_warnings()


#Connect to pure array and create an array
array = purestorage.FlashArray("10.10.10.10", api_token="frg-1928392-andndnd01910")

#List and Log existing luns on MyDBServer 
MyDbServerLog = array.list_host_connections("MyDbServer")
logging.info(MyDbServerLog)

#Disconnect existing Luns that contain old copy of database, the two luns here are DB_DATA_SNAP & DB_LOG_SNAP
array.disconnect_host("MyDbServer", "DB_DATA_SNAP")
array.disconnect_host("MyDbServer", "DB_LOG_SNAP")


#delete old Luns
array.destroy_volume("DB_DATA_SNAP")
array.destroy_volume("DB_LOG_SNAP")
array.eradicate_volume("DB_DATA_SNAP")
array.eradicate_volume("DB_LOG_SNAP")

#Create another log entry with host mappings after LUNs have been removed
MyDbServerLog = array.list_host_connections("MyDbServer")
logging.info(MyDbServerLog)


#Create snap of prod database assuming DB lives on FLASHDATA & FLAShGLOG Luns
array.create_snapshots(["FLASHSQLDATA","FLASHSQLLOG"],suffix="python")

#Copy snap to a volume for read/write mapping to host
array.copy_volume("FLASHSQLDATA.python", "DB_DATA_SNAP")
array.copy_volume("FLASHSQLLOG.python", "DB_LOG_SNAP")

#Mapp the new volumes to the host
array.connect_host("MyDbServer", "DB_DATA_SNAP")
array.connect_host("MyDbServer", "DB_LOG_SNAP")


#Delete the snaps since we no longer need them
array.destroy_volume("FLASHSQLDATA.python")
array.destroy_volume("FLASHSQLLOG.python")
array.eradicate_volume("FLASHSQLDATA.python")
array.eradicate_volume("FLASHSQLLOG.python")


#Create final log entry after new Luns have been mapped to the host
MyDbServerLog = array.list_host_connections("MyDbServer")
logging.info(MyDbServerLog)

#Disconnect from the array
array.invalidate_cookie()


#Create time stamp for end of script
endtime = time.localtime(time.time())
endtime = time.strftime("%y/%m/%d %H:%M", endtime)


#Send completion email
endmsg = MIMEText("Reporting Database Snap completed at: " + endtime)
sender ='PURE01@CO.ORG'
recipient = 'DatabaseTeam@CO.ORG,storageadmin@co.org'
endmsg['Subject'] = 'Reporting Database Snap Completed'
endmsg['From'] = sender
endmsg['To'] = recipient
mailserver = smtplib.SMTP('smtp.co.org')
mailserver.sendmail(sender, recipient.split(','), endmsg.as_string())
mailserver.quit()


#Close logging file 
logging.info('--------------------Script   Ended------------------------')

 

