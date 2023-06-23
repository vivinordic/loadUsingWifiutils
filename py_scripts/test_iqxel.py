#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      vivi
#
# Created:     03/03/2021
# Copyright:   (c) vivi 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from iqxel import *
from common_utils import *

GiLtfType = 2
numLtf = 1
user = 1
standard = 'LDPC'
ruIdx = 1
fecFactor = 1
midample = 10
datarate = 1
nss = 1
ruType = 242

def testVsa():
    equipment = IQXEL('IQXEL_80','10.90.48.121')
    equipment.init_vsa_funcs(standard='11ac',bw='20',streams='1x1',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',chain_sel='1')
    equipment.apply_vsa(bw='20',chn=int(36),streams='1x1')
    equipment.setVsaUserNss(user, nss)
    equipment.setVsaUserCodingStandard(user, standard)
    equipment.vsaEnableDisambiguity()
    equipment.setVsaGiLtfType( GiLtfType)
    equipment.vsaEnableLdpcExtraSymbol()
    equipment.setVsaNumLtf(numLtf)
    equipment.setVsaUserRuIdx(user, ruIdx)
    equipment.setVsaPreFecfactor(fecFactor)
    equipment.vsaDisableDcm(user)
    equipment.vsaDisableDoppler()
    equipment.setVsaMidamplePeriodicity(midample)
    equipment.vsaEnableLtfMode()
    equipment.setVsaUserDatarate(user, datarate)
    equipment.click_analyser('11ac','1x1',pkts='15')

def testVsg():
    equipment = IQXEL('IQXEL_80','10.90.48.121')
    equipment.init_vsg_funcs(standard='11ac',bw='20',streams='1x1',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',test='rx',chain_sel='1')

    equipment.config_11ax()
    equipment.vsgDisableMultiuser()
    equipment.vsgEnableSuFrame()
    equipment.setVsgUserNss(user, nss)
    equipment.setVsgUserCodingStandard(user, standard)
    equipment.vsgDisableDisambiguity()
    equipment.setVsgGiLtfType( GiLtfType)
    equipment.vsgDisableLdpcExtraSymbol()
    equipment.setVsgNumLtf(numLtf)
    equipment.setVsgUserRuIdx(user, ruIdx)
    equipment.setVsgPreFecfactor(fecFactor)
    equipment.vsgDisableDcm(user)
    equipment.vsgDisableDoppler()
    equipment.setVsgMidamplePeriodicity(midample)
    equipment.vsgEnableLtfMode()
    equipment.set_idleinterval(20)
    equipment.setVsgUserDatarate(user, datarate)
    equipment.apply_vsg(bw='20',chn=int(40),streams='1x1')
    equipment.set_macheader()
    equipment.generate_waveform(streams='1x1')
    equipment.set_amplitude('1x1',str(-10))
    equipment.send_packets(streams='1x1')

def testTbVsg():
    equipment = IQXEL('IQXEL_80','10.90.48.121')
    equipment.init_vsg_funcs(standard='11ac',bw='20',streams='1x1',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',test='rx',chain_sel='1')

    equipment.config_11ax()
    equipment.vsgEnableTriggerFrame()
    equipment.vsgEnableMultiuser()
    equipment.setMuNumUser(1)
    equipment.setVsgUserNss(user, nss)
    equipment.setVsgUserCodingStandard(user, standard)
    equipment.vsgDisableDisambiguity()
    equipment.setVsgGiLtfType( GiLtfType)
    equipment.vsgDisableLdpcExtraSymbol()
    equipment.setVsgNumLtf(1)
    equipment.setVsgUserRuIdx(user, ruIdx)
    equipment.setVsgUserNss(1, nss)
    equipment.setVsgPreFecfactor(1)
    equipment.vsgDisableDcm(user)
    equipment.vsgDisableDoppler()
    equipment.setVsgMidamplePeriodicity(midample)
    equipment.vsgDisableLtfMode()
    equipment.set_idleinterval(20)
    equipment.setVsgUserDatarate(user, datarate)
    equipment.set_userMacheader(1)

    equipment.apply_vsg(bw='40',chn=int(40),streams='1x1')
    equipment.set_macheader()
    equipment.generate_waveform(streams='1x1')
    equipment.set_amplitude('1x1',str(-10))
    equipment.send_packets(streams='1x1')

def testErsuVsg():
    equipment = IQXEL('IQXEL_80','10.90.48.121')
    equipment.init_vsg_funcs(standard='11ac',bw='20',streams='1x1',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',test='rx',chain_sel='1')

    equipment.config_11ax()
    equipment.vsgDisableMultiuser()
    equipment.vsgEnableErsuFrame()
    equipment.setVsgExRangeRuType(ruType)
    equipment.setVsgUserNss(user, nss)
    equipment.setVsgUserCodingStandard(user, standard)
    equipment.vsgDisableDisambiguity()
    equipment.setVsgGiLtfType( GiLtfType)
    equipment.vsgDisableLdpcExtraSymbol()
    equipment.setVsgNumLtf(numLtf)
    equipment.setVsgUserRuIdx(user, ruIdx)
    equipment.setVsgPreFecfactor(fecFactor)
    equipment.vsgDisableDcm(user)
    equipment.vsgDisableDoppler()
    equipment.setVsgMidamplePeriodicity(midample)
    equipment.vsgEnableLtfMode()
    equipment.set_idleinterval(20)
    equipment.setVsgUserDatarate(user, datarate)
    equipment.apply_vsg(bw='20',chn=int(40),streams='1x1')
    equipment.set_macheader()
    equipment.generate_waveform(streams='1x1')
    equipment.set_amplitude('1x1',str(-10))
    equipment.send_packets(streams='1x1')

def testMuVsg():
    equipment = IQXEL('IQXEL_80','10.90.48.121')
    equipment.init_vsg_funcs(standard='11ac',bw='20',streams='1x1',stbc='STBC_0',gi='LGI',coding='BCC',greenfield_mode='Mixed',preamble='LONG',payload='1024',test='rx',chain_sel='1')

    equipment.config_11ax()
    equipment.vsgEnableMultiuser()
    #equipment.vsgEnableSuFrame()
    equipment.setMuNumUser(2)
    equipment.setVsgMuRuAllocation('00000000', '1,0,1,0,0,0,0,0,0')
    equipment.apply_vsg(bw='20',chn=int(40),streams='1x1')
    equipment.setVsgGiLtfType(GiLtfType)

    equipment.setVsgUserNss(1, nss)
    equipment.setVsgUserCodingStandard(1, standard)
    equipment.setVsgUserDatarate(1, datarate)
    equipment.vsgDisableDcm(1)
    equipment.set_userMacheader(1)

    equipment.setVsgUserNss(2, nss)
    equipment.setVsgUserCodingStandard(2, standard)
    equipment.setVsgUserDatarate(2, datarate)
    equipment.vsgDisableDcm(2)
    equipment.set_userMacheader(2)

##    equipment.vsgDisableDisambiguity()
##    equipment.vsgDisableLdpcExtraSymbol()
##    equipment.vsgDisableDoppler()
##    equipment.setVsgMidamplePeriodicity(midample)
##
    equipment.set_idleinterval(20)
    equipment.set_macheader()
    equipment.generate_waveform(streams='1x1')
    equipment.set_amplitude('1x1',str(-10))
    equipment.send_packets(streams='1x1')

def main():
    testVsg()
##    equipment.setVsaNumLtf(nltf)
##
##    equipment.vsgEnableSuFrame()

if __name__ == '__main__':
    main()
