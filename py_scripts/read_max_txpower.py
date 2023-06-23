import os
import re
import sys
import xlsxwriter

import xlrd
standard_evm_dict={
    '2.4':
    {
        '1':'9','2':'9','5.5':'9','11':'9',
        '6':'5','9':'8','12':'10','18':'13','24':'16','36':'19','48':'22','54':'25',
        'MCS0':'5','MCS1':'10','MCS2':'13','MCS3':'16','MCS4':'19','MCS5':'22','MCS6':'25','MCS7':'27',
        'MCS8':'5','MCS9':'10','MCS10':'13','MCS11':'16','MCS12':'19','MCS13':'22','MCS14':'25','MCS15':'27',
    },
    '5':
    {
        '6':'5','9':'8','12':'10','18':'13','24':'16','36':'19','48':'22','54':'25',
        'MCS0':'5','MCS1':'10','MCS2':'13','MCS3':'16','MCS4':'19','MCS5':'22','MCS6':'25','MCS7':'27','MCS8':'30','MCS9':'32'
    }
}

base = os.getcwd()
source = os.path.join(base,'copy')
files_in_cwd= os.listdir(source)
# exit(0)
twoptfour_20=[]
twoptfour_40=[]
best_tx_power_list=[]
row_num=2
xls_name=sys.argv[1]
xls_name = os.path.join(source,xls_name)
data_rate=sys.argv[2]
bw=sys.argv[3]+'Mhz'
band = data_rate.split('_')[0] + 'GHz'
workbook_maxtxpower = xlsxwriter.Workbook(xls_name+'.xlsx')
worksheet_maxtxpower = workbook_maxtxpower.add_worksheet()
bold_maxtxpower = workbook_maxtxpower.add_format({'bold': 1})
streams = sys.argv[4]
standard = sys.argv[5]

if (standard == 'HETB'):
    worksheet_maxtxpower.write_row('A1',['Channel','RU Allocation','bw','Expected EVM','Prev Power_1','Prev EVM_1(-ve)','Prev Spectrum','Curr Power_1','Curr EVM_1','Curr Spectrum','Interpolated Power'],bold_maxtxpower)
elif (streams == '2x2'):
    worksheet_maxtxpower.write_row('A1',['Channel','Expected EVM','Prev Power_1','Prev EVM_1(-ve)','Prev Spectrum1','Curr Power_1','Curr EVM_1','Curr Spectrum2','Interpolated Power_1','Prev Power_2','Prev EVM(-ve)_2','Prev Spectrum2','Curr Power_2','Curr EVM_2','Curr Spectrum2','Interpolated Power_2','Final Power'],bold_maxtxpower)
else:
    worksheet_maxtxpower.write_row('A1',['Channel','Expected EVM','Prev Power_1','Prev EVM_1(-ve)','Prev Spectrum','Curr Power_1','Curr EVM_1','Curr Spectrum','Interpolated Power'],bold_maxtxpower)

for f in files_in_cwd:
    if('TX_Consolidated' not in f):
        continue
    if ((standard !='11g')&(standard !='11b')):
        if(bw not in f):
            continue
    if ((standard != 'HESU') & (standard != 'HEERSU') & (standard != 'HETB')):
        if(streams not in f):
            continue
        if(band not in f):
            continue
    if(standard not in f):
        continue
    #for bw in bw_list:
    # if('40' in f):
        # ch_list=[38,46,54,62]
    # else:
        # ch_list=[1,6,11]
    data=[]
    print f
    ch=f.split('Chn')[1].split('_')[0]
    if (standard == '11g'):
        ch = ch.split('.')[0]
    data.append(int(ch))
    if (standard =='HETB'):
        data += [f.split('RUAL')[1].split('_')[1],bw]
    data.append((float(standard_evm_dict[data_rate.split('_')[0]][data_rate.split('_')[1]])))
    xls_file=os.path.join(source,f)
    # xls_file='TX_Consolidated_11n_1x1_1_2.4GHz_Chn'+str(ch)+'_'+bw+'Mhz_LGI_BCC_Mixed_STBC_0.xlsx'
    print xls_file
    wb = xlrd.open_workbook(xls_file)
    sheet = wb.sheet_by_name('Sheet1')
    measured_power_list=[]
    measured_evm_list=[]
    spectrum_pass_list=[]
    for indx in range(1,sheet.nrows):
        if (streams == '1x1'):
            measured_power_list.append(float(sheet.cell(indx,6).value))
            measured_evm_list.append(float(sheet.cell(indx,7).value))
            if (standard =='11b'):
                spectrum_pass_list.append((sheet.cell(indx,22).value))
            else:
                spectrum_pass_list.append((sheet.cell(indx,30).value))
        if (streams == '2x2'):
            measured_power_list.append(float(sheet.cell(indx,6).value))
            measured_evm_list.append(float(sheet.cell(indx,8).value))
            spectrum_pass_list.append((sheet.cell(indx,22).value))
    # print measured_evm_list
    step_num=0
    # print measured_power_list
    rev_power=reversed(measured_power_list)
    rev_power=[]
    for p in reversed(measured_power_list):
        rev_power.append(p)
    rev_evm=[]
    for e in reversed(measured_evm_list):
        rev_evm.append(e)
    rev_spectrum=[]
    for sp in reversed(spectrum_pass_list):
        rev_spectrum.append(sp)
    # print rev_power
    # print rev_evm
    for evm in rev_evm:

        if(step_num==0):
            prev_evm=0
            curr_evm=evm
            prev_spec ='NA'
            curr_spec=rev_spectrum[step_num]

        else:
            prev_evm=curr_evm
            curr_evm=evm
            prev_spec =curr_spec
            curr_spec=rev_spectrum[step_num]
        # print evm,standard_evm_dict['5']['MCS7']
        best_tx_power=0
        print 'prev',step_num
        if(float(evm) > float(standard_evm_dict[data_rate.split('_')[0]][data_rate.split('_')[1]])):
            if (rev_spectrum[step_num] =='Spectrum mask failure'):
                step_num+=1
                continue
            # print 'GREATER',rev_power
            print 'curr_evm',curr_evm
            print 'prev_evm',prev_evm
            # print 'rev_power[step_num-1]',rev_power[step_num-1],float(prev_evm)
            # print 'rev_power[step_num]',rev_power[step_num],float(evm)
            # print 'rev_power',(rev_power[step_num-1]+rev_power[step_num])/2
            # print 'rev_power',str(round((rev_power[step_num-1]+rev_power[step_num])/2,1))
            if ((float(curr_evm) > float(standard_evm_dict[data_rate.split('_')[0]][data_rate.split('_')[1]])) & (prev_evm==0)):
                best_tx_power=(round(rev_power[step_num],1))
            elif (prev_spec =='Spectrum mask failure'):
                best_tx_power=(round(rev_power[step_num],1))
            else:
                best_tx_power=(round(rev_power[step_num-1]+(((float(standard_evm_dict[data_rate.split('_')[0]][data_rate.split('_')[1]])-prev_evm)*(rev_power[step_num]-rev_power[step_num-1]))/(curr_evm-prev_evm)),1))
            break
        step_num+=1
    print 'curr',step_num
    best_tx_power_list.append(best_tx_power)
    print best_tx_power,step_num,len(rev_power),step_num-1
    if (step_num >0):
        data.append((rev_power[step_num-1]))
    else:
        data.append("NA")
    data.append((prev_evm))
    data.append((prev_spec))
    try:
        data.append((rev_power[step_num]))
    except:
        data.append(("NA"))
    data.append((curr_evm))
    data.append((curr_spec))
    best_tx_power-=0
    data.append((best_tx_power))
    if (streams == '2x2'):
        measured_power_list=[]
        measured_evm_list=[]
        for indx in range(1,sheet.nrows):
            measured_power_list.append(float(sheet.cell(indx,7).value))
            measured_evm_list.append(float(sheet.cell(indx,9).value))
            spectrum_pass_list.append((sheet.cell(indx,23).value))
        # print measured_evm_list
        step_num=0
        # print measured_power_list
        rev_power=reversed(measured_power_list)
        rev_power=[]
        for p in reversed(measured_power_list):
            rev_power.append(p)
        rev_evm=[]
        for e in reversed(measured_evm_list):
            rev_evm.append(e)
        rev_spectrum=[]
        for sp in reversed(spectrum_pass_list):
            rev_spectrum.append(sp)
        # print rev_power
        # print rev_evm
        for evm in rev_evm:

            if(step_num==0):
                prev_evm=0
                curr_evm=evm
                prev_spec ='NA'
                curr_spec=rev_spectrum[step_num]

            else:
                prev_evm=curr_evm
                curr_evm=evm
                prev_spec =curr_spec
                curr_spec=rev_spectrum[step_num]
            # print evm,standard_evm_dict['5']['MCS7']
            best_tx_power1=0
            print 'prev',step_num
            if(float(evm) > float(standard_evm_dict[data_rate.split('_')[0]][data_rate.split('_')[1]])):
                if (rev_spectrum[step_num] =='Spectrum mask failure'):
                    step_num+=1
                    continue
                # print 'GREATER',rev_power
                print 'curr_evm',curr_evm
                print 'prev_evm',prev_evm
                if ((float(curr_evm) > float(standard_evm_dict[data_rate.split('_')[0]][data_rate.split('_')[1]])) & (prev_evm==0)):
                    best_tx_power1=(round(rev_power[step_num],1))
                elif (prev_spec =='Spectrum mask failure'):
                    best_tx_power1=(round(rev_power[step_num],1))
                else :
                    best_tx_power1=(round(rev_power[step_num-1]+(((float(standard_evm_dict[data_rate.split('_')[0]][data_rate.split('_')[1]])-prev_evm)*(rev_power[step_num]-rev_power[step_num-1]))/(curr_evm-prev_evm)),1))
                break
            step_num+=1
        print 'curr',step_num
        best_tx_power_list.append(best_tx_power1)
        print best_tx_power1,step_num,len(rev_power),step_num-1
        if (step_num >0):
            data.append((rev_power[step_num-1]))
        else:
            data.append('NA')
        data.append((prev_evm))
        data.append((prev_spec))
        try:
            data.append((rev_power[step_num]))
        except:
            data.append(("NA"))
        data.append((curr_evm))
        data.append((curr_spec))
        best_tx_power1-=0
        data.append((best_tx_power1))
        final_power = min(best_tx_power1 , best_tx_power)
        data.append((final_power))
    print data
    worksheet_maxtxpower.write_row('A'+str(row_num), data)
    row_num+=1
    # print best_tx_power1
    #exit(0)
workbook_maxtxpower.close()
print best_tx_power_list