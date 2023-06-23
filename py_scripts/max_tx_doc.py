#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     17/03/2022
# Copyright:   (c) vivi 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from common_utils import *
import sys
from lookup_tables import *

def save_to_doc(standard,freq,datarate,channel_list,powerDict):
    global document_path
    document_path='maxpower.docx'
    try:
        document = Document(document_path)
    except:
        document = Document()
    paragraphs_obj=document.paragraphs
    paragraphs=[]
    for p in paragraphs_obj:
        paragraphs.append(p.text)
    if("MAX TX POWER" not in paragraphs):
        document.add_heading("MAX TX POWER", level=1)
    if('Max TX Power across Channels' not in paragraphs):
        document.add_heading('Max TX Power across Channels', level=2)
    if(standard=='HESU'):
        if("HESU - "+freq+"GHz" not in paragraphs):
            document.add_heading("HESU - "+freq+"GHz", level=3)
    elif(standard=='HEERSU'):
        if("HEERSU - "+freq+"GHz" not in paragraphs):
            document.add_heading("HEERSU - "+freq+"GHz", level=3)
    elif(standard=='HETB'):
        if("HETB - "+freq+"GHz" not in paragraphs):
            document.add_heading("HETB - "+freq+"GHz", level=3)
    elif(standard=='11ac'):
        if("VHT - "+freq+"GHz" not in paragraphs):
            document.add_heading("VHT - "+freq+"GHz", level=3)
    elif(standard=='11n'):
        if("HT - "+freq+"GHz" not in paragraphs):
            document.add_heading("HT - "+freq+"GHz", level=3)
    elif(standard=='11g'):
        if("Legacy - "+freq+"GHz" not in paragraphs):
            document.add_heading("Legacy - "+freq+"GHz", level=3)
    elif(standard=='11a'):
        if("Legacy - "+freq+"GHz" not in paragraphs):
            document.add_heading("Legacy - "+freq+"GHz", level=3)
    elif(standard=='11b'):
        if("DSSS - "+freq+"GHz" not in paragraphs):
            document.add_heading("DSSS - "+freq+"GHz", level=3)
    table = document.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    if (standard == 'HETB'):
        hdr_cells[0].text = 'RU Allocation'
    else:
        hdr_cells[0].text = 'Channel'
    if ((standard=='11b') | (standard=='11g')):
        hdr_cells[1].text = 'Max TX power for '+ datarate +'Mbps'
    else:
        hdr_cells[1].text = 'Max TX power for '+ datarate
    hdr_cells[2].text = 'Expected Max TX power value '
    for i in range(len(channel_list)):
        row_cells = table.add_row().cells
        row_cells[0].text = str(channel_list[i])
        row_cells[1].text = str(powerDict[channel_list[i]])
        row_cells[2].text = str(TX_max_power_reference[standard]['1x1']['20'][datarate])
##    for datarate in data_rate.split(','):
##        if(datarate in sensitivity_amp_dict[chn].keys()):
##            row_cells = table.add_row().cells
##            row_cells[0].text = str(datarate)
##            if('TBT' in str(sensitivity_amp_dict[chn][datarate])):
##                row_cells[1].text = str(sensitivity_amp_dict[chn][datarate])
##            else:
##                row_cells[1].text = str(round(float(sensitivity_amp_dict[chn][datarate]),2))
    try:
        document.save(document_path)
    except:
        document.save(document_path+'_'+str(time.time())+'.docx')



def main(argv):

    standard = argv[1]
    freq = argv[2]
    datarate = argv[3]

    inputFilePath = os.path.abspath('copy')
    file_name = os.path.join(inputFilePath, argv[4]) # '2.4G_1x1_1_ALLCHANNELS_20.xlsx'
    workbook = xlrd.open_workbook(file_name)

    # Read the common Params from the workbook
    commonParamsSheet = workbook.sheet_by_name('Sheet1')
    if (standard == 'HETB'):
        Channels = commonParamsSheet.col_slice(colx=1, start_rowx=1) # Read RU allocation value
        powers = commonParamsSheet.col_slice(colx=10, start_rowx=1) # Read max tx power
    else:
        Channels = commonParamsSheet.col_slice(colx=0, start_rowx=1) # Read channel number
        powers = commonParamsSheet.col_slice(colx=8, start_rowx=1) # Read max tx power
    channel_list = []
    power_list = []
    powerDict = {}
    for cell in Channels:
        channel_list.append(int(cell.value))
    for cell in powers:
        power_list.append(cell.value)
    for i in range(len(channel_list)):
        powerDict.update({channel_list[i]:power_list[i]})
    #channel_list = [1,2,3,4,5,6,7,8,9,10,11,12,13]
    #power_list = [12.6,12.7,12.6,12.7,12.6,12.6,12.5,12.6,12.6,10.8,12.5,12.7,12.7]
    channel_list.sort()
    save_to_doc(standard,freq,datarate,channel_list,powerDict)

if __name__ == '__main__':
    main(sys.argv)
