import math
from common_utils import *

CRC_ARRAY_SIZE = 4;

def crc32Itr(ui8InByte,bInitializeCRCState,bCRCOutputFlushEn,pui8CRCOutByte,pui32InCrcState):

    ui32CrcState=[0];

    # Extract State Params
    ui32CrcState[0] = pui32InCrcState[0];

    # Extract Config Params
    if (bInitializeCRCState==1):
        ui32CrcState[0]  = 0xFFFFFFFF;

    if (bCRCOutputFlushEn==1):

        flushLoopCnt=[0,1,2,3];
        for k in flushLoopCnt:

            # Taking one byte at a time ..from MSbyte to LSByte
            ui8InByteTemp    = (( (ui32CrcState[0]^0xffffffff) & 0xffffffff ) & 0xFF000000)>>24;# one's complement

            # flipping the bits from left to right to ensure CRC output is in correct order
            pui8CRCOutByte[k] = ((ui8InByteTemp&0x01)<<7) +    \
                ((ui8InByteTemp&0x02)<<5) +    \
                ((ui8InByteTemp&0x04)<<3) +    \
                ((ui8InByteTemp&0x08)<<1) +    \
                ((ui8InByteTemp&0x10)>>1) +    \
                ((ui8InByteTemp&0x20)>>3) +    \
                ((ui8InByteTemp&0x40)>>5) +    \
                ((ui8InByteTemp&0x80)>>7) ;

            ui32CrcState[0]  = (ui32CrcState[0] <<8) & 0xffffffff;


    if ( (bInitializeCRCState!=1) and (bCRCOutputFlushEn!=1) ):
        #print "crc input = ", ui8InByte

        crcLoopCnt=[0,1,2,3,4,5,6,7];
        for k in crcLoopCnt:
            # the following logic is for computation of CRC state for 1 inptut bit
            ui8InBit = ui8InByte&0x01;
            ui32XorBit = (ui32CrcState[0] &0x80000000)>>31 ^ ui8InBit;

            ui32XorWord = (ui32XorBit<<26) + (ui32XorBit<<23) +        \
                            (ui32XorBit<<22) + (ui32XorBit<<16 )+   \
                            (ui32XorBit<<12) + (ui32XorBit<<11) +   \
                            (ui32XorBit<<10) + (ui32XorBit<<8) +    \
                            (ui32XorBit<<7)  + (ui32XorBit<<5)  +   \
                            (ui32XorBit<<4) + (ui32XorBit<<2) +     \
                            (ui32XorBit<<1)  + ui32XorBit;
            ui32CrcState[0]  = (ui32XorWord ^ (ui32CrcState[0] <<1)) & 0xffffffff;

            ui8InByte = ui8InByte>>1;# shift for parsing the next input bit

    # Update State Params
    pui32InCrcState[0]=ui32CrcState[0] ;

def crc32(crc_en, mpdu_len, input_bytes_lsb_first, mpdu_bytes):
    # CRC32 calculation
    ui8CRCOutByte=[0]*CRC_ARRAY_SIZE;
    crc_out=[0]*CRC_ARRAY_SIZE;

    # Initialize CRC32
    ui8InByte=0;
    bInitializeCRCState=1
    bCRCOutputFlushEn=0
    ui32InCrcState = [0];
    ui32InCrcState[0] = ui32InCrcState[0] & 0xffffffff;
    crc32Itr(ui8InByte,bInitializeCRCState,bCRCOutputFlushEn,ui8CRCOutByte,ui32InCrcState);


    if (crc_en == 1):

        # CRC calculation
        for i in range(0, mpdu_len):
            ui8InByte=input_bytes_lsb_first[i];
            bInitializeCRCState=0;
            bCRCOutputFlushEn=0;
            ui32InCrcState[0] = ui32InCrcState[0] & 0xffffffff;

            crc32Itr(ui8InByte,bInitializeCRCState,bCRCOutputFlushEn,ui8CRCOutByte,ui32InCrcState);

        # Calling CRC module to flush out 4-bytes of CRC data
        ui8InByte=0;
        bInitializeCRCState=0 ;
        bCRCOutputFlushEn=1;
        ui32InCrcState[0] = ui32InCrcState[0] & 0xffffffff;
        crc32Itr(ui8InByte,bInitializeCRCState,bCRCOutputFlushEn,crc_out,ui32InCrcState);

        mpdu_with_crc = mpdu_bytes;
        mpdu_with_crc += crc_out

    else:

        for i in range(0, mpdu_len):
            mpdu_with_crc[i]=input_bytes_lsb_first[i]; # should this be bit reversed?
    return mpdu_with_crc

def crc8(ui16InputVal,pui8CRCout):
    """ generates crc8 output """
    # ui16InputVal is 16 bit variable
    # pui8CRCout is array of 1 element

    ui8CRCstate=0xFF;
    ui8CRCstateNew=0;
    ui8FeedBack=0;
    ui8Bitcnt=0;

    for ui8Bitcnt in range(16):
        ui8FeedBack=((ui16InputVal>>ui8Bitcnt) &0x1) ^ ((ui8CRCstate>>7)&0x1);
        ui8CRCstateNew=(ui8FeedBack<<2)+(ui8FeedBack<<1)+ui8FeedBack;
        ui8CRCstate = ui8CRCstateNew ^ (ui8CRCstate<<1);

    ui8FeedBack=0;

    # Bit reversal and not to get CRC-8
    for ui8Bitcnt in range(8):
        temp1 = (ui8CRCstate>>ui8Bitcnt) &0x1 ;
        temp2= not(temp1);
        temp3=7-ui8Bitcnt;
        ui8FeedBack += temp2<<temp3;

    pui8CRCout[0]=ui8FeedBack;

def formMpduDl(format, mpdu_len, eof_bit, mpdu_no, mpdu_dl):
    """ Generates delimiter bytes """
    # Input params: mpdu_len,eof_bit,mpdu_no
    # output parameter: mpdu_dl --> which is array of one element

    resv_bits = 0;

    crc8out=[0]
    crc8out[0]=0;

    if(format == DUT_FrameFormat.MM): # HT
        resv_bits = 0;
        mpdu_low_2bytes=((mpdu_len &(0xFFF) )<<4) | (resv_bits & 0xF);
    if(format >= DUT_FrameFormat.VHT): # VHT
        resv_bit = 0;
        mpdu_low_2bytes=((mpdu_len &(0xFFF) )<<4) | (((mpdu_len &(0x3000))>>12)<<2) | (resv_bit<<1) |  eof_bit;

    # calculate CRC8 on two byte information of mpdu_low_2bytes
    crc8(mpdu_low_2bytes,crc8out);

    dl_sig = 0x4E # bit reversal of signature 0x4E

    mpdu_dl[0] =  (dl_sig<<24) | (crc8out[0] <<16) | mpdu_low_2bytes;

def formMpduNpad(mpdu_length, numPadBytes):
    """ returns number of pad bytes """
    # instead of returning array containing zero pad bytes like matlab, python returning only number of pad bytes.
    # adding pad bytes is done in the file that calls this function.

    # input parameters: mpdu_length  of type just a variable
    # Output parameters: numPadBytes ..is pointer to an array of size 1.

    numPadBytes[0] = int((math.ceil((float(mpdu_length)/4))*4)-mpdu_length);

def formMpduSpacing(num_spacing,mpdu_spacing):
    """ Generates MPDU spacing delimiter """
    # input parameters : num_spacing, this indicates number of times the null delimiter is to be repeated.
    # output paramter  : mpdu_spacing  - array of type char

    ui8CRC_out=[0];
    ui8CRC_out[0]=0xFF;

    # form null mpdu fist and then repeat it for num_spacing times

    #step 1: forming null mpdu

    mpduDelimiter=[0]*4;
    mpdulen=0;
    # this should be set as per the format.
    reservedbit=0;
    EOFbit=1;
    mpduLower2bytes= mpdulen<<2 | (reservedbit<<1) | EOFbit;

    crc_byte=[0];
    crc_byte[0]=0;
    crc8(mpduLower2bytes,crc_byte);

    # bit reversal of crc8
    crc8out=[0];
    crc8out[0]=crc_byte[0];

    delimSig=0x4E;


    # MPDU delimiter
    mpduDelimiter[0] = mpduLower2bytes & 0XFF;
    mpduDelimiter[1] = (mpduLower2bytes>>8) & 0XFF;
    mpduDelimiter[2] = crc_byte[0];
    mpduDelimiter[3] = delimSig;

    #step 2: repeat the null mpdu, num_spacing times
    index=0;
    for repetition in range(num_spacing):
        mpdu_spacing[index]=mpduDelimiter[0];
        mpdu_spacing[index+1]=mpduDelimiter[1];
        mpdu_spacing[index+2]=mpduDelimiter[2];
        mpdu_spacing[index+3]=mpduDelimiter[3];
        index=index+4;
def formMpdu(mpdu_bytes, crc_en, mpdu_idx, mpdu_payload_from_flag, \
                no_mpdus, mpdu_len):
    """ Adds crc32 byte and MPDU delimiter bytes to the payload data """
    #input parameters : mpdu_bytes, crc_en, mpdu_idx, mpdu_payload_from_flag,  no_mpdus,
    # output parameter: mpdu_with_crc - array


    # CRC BIT MAP field : To update the sequence number for each MPDU
    if ((mpdu_payload_from_flag==4) or (mpdu_payload_from_flag==5)):
        mpdu_bytes[23]= mpdu_bytes[23]+(16*((mpdu_idx-1)%16));
        if ((mpdu_idx>16) and (mpdu_idx<33)):
            mpdu_bytes[24]= mpdu_bytes[24]+1;
        elif ((mpdu_idx>32) and (mpdu_idx<49)):
            mpdu_bytes[24]= mpdu_bytes[24]+2;
        elif ((mpdu_idx>48) and (mpdu_idx<65)):
            mpdu_bytes[24]= mpdu_bytes[24]+3;
        else:
            mpdu_bytes[24]= mpdu_bytes[24];


    # pass MPDU data as is to CRC 32 but bit-reverse both i/p and CRCoutput while generating output.

    input_bytes_lsb_first=0*[mpdu_len+1]
    input_bytes_lsb_first=[0]*65536;

    for i in range(0, mpdu_len):
        input_bytes_lsb_first[i]= mpdu_bytes[i];

    # CRC32 calculation
    mpdu_with_crc = crc32(crc_en, mpdu_len, input_bytes_lsb_first, mpdu_bytes)
    return mpdu_with_crc

def formAmpduData(TX_PARAMS, data_bytes_out, mpdu_data):
    """ this function generates the complete AMPDU data  """
    # input parameters:
	#                    TX_PARAMS  - structure
	#                    TXVECTOR   - structure
    # output parameters :
    #                    data_bytes_out  - array
    #                    mpdu_data       - array

    aggregation_en         = TX_PARAMS.aggregation;      # aggregation enabled or not
    payload_len            = TX_PARAMS.length;           # MPDU sub frame length
    num_mpdu               = [0];
    num_mpdu[0]            = TX_PARAMS.nMPDUs;           # number of MPDU sub frames
    delimiter_len          = TX_PARAMS.delimiter_len;    # number of null delimiters
    crc_en                 = 1;           # CRC32 enabled or not
    format                 = TX_PARAMS.format;            # format HT/VHT/..

    # variables to maintain same APIs as that of matlab.
    ldpc_en                = 0;
    nes                    = 0;
    increment_len          = 0;
    mpdu_payload_from_flag = 0;
    mstbc                  = 1; # to avoid division by zero
    ndbps                  = 1;
    npad_bytes_out         = [0]*100;
    agg_config_out         = [0]*100;
    apep_len               = [0];

    # This function is designed to support multiple MPDUs per PSDU. But if aggr_test_en is not enabled
    # then defaults to a single MPDU packet with MPDU length.

    num_flush_bytes = 0;

    mpdu_len_arr=[0]*(num_mpdu[0]); # as index starts from 1
    spacing_arr=[0]*(num_mpdu[0]); # as index starts from 1

    if (aggregation_en == 1):
        if (format > 1):
            for i in range(0,num_mpdu[0]):
                # This length includes 4 bytes of CRC
                mpdu_len_arr[i] = payload_len+(i-1)*increment_len;
                spacing_arr[i] = delimiter_len;

        else:
            # if format is legacy or DSSS then through error
            error('Aggregation Cannot be enabled for Legacy or DSSS');

    else:
        # else send as a single mpdu. (For VHT mode even if aggregation_en is not set will be treated as an aggregated packet.)
        num_mpdu[0] = 1;
        # no  MPDU Delimiter
        mpdu_len_arr[0] = payload_len;


    # This is the number of payload bytes to be generated.
    totalPayloadLength=0;
    for i in range(0,num_mpdu[0]):
        totalPayloadLength = totalPayloadLength + mpdu_len_arr[num_mpdu[0]-1];

    ampduBytesStartPos = 0;
    num_bytes = 0;


    length_of_data_bytes_out=0;
    length_of_data_bytes_out1=0;
    num_spacing=0;

    for mpdu_idx in range(1,num_mpdu[0]+1):

        if (mpdu_idx == num_mpdu[0]):
            last_mpdu = 1;
        else:
            last_mpdu = 0;

        if (mpdu_idx==1):
            first_mpdu = 1;
        else:
            first_mpdu = 0;


        if ((num_mpdu[0]==1) and (format >= DUT_FrameFormat.VHT)):
            eof_bit = 1;
        else:
            eof_bit = 0;


        mpdu_len = mpdu_len_arr[mpdu_idx-1];

        #Add MPDU delimiter only if aggregation enabled or if its a VHT packet
        mpdu_dl=[0];
        mpdu_dl[0]=0;

        if ( (aggregation_en==1) or (format >= DUT_FrameFormat.VHT) ):
            formMpduDl(format, mpdu_len, eof_bit, mpdu_idx, mpdu_dl);

        # This variable is used to find the position from where input bytes has
        # to be considered for each AMPDU packet.
        ampduBytesStartPos = ampduBytesStartPos + num_bytes;
        if (crc_en==1):
            num_bytes = mpdu_len-4;
        else:
            num_bytes = mpdu_len;

        mpdu_bytes_without_crc = mpdu_data
        startIdx=ampduBytesStartPos + 1;

        mpdu_with_crc = formMpdu(mpdu_bytes_without_crc,    \
                    crc_en,                  \
                    mpdu_idx,                \
                    mpdu_payload_from_flag,  \
                    num_mpdu[0],             \
                    num_bytes);


        # last argument to formMpdu is extra argument (compared to matlab) so that already available crc32 (implemented using c as ref)
        # that calculates on byte basis. Matlab CRC32 calculate for entire packt in one go.

        #Add pad bytes only if aggregation enabled
        numPadBytes=[0];
        numPadBytes[0]=0;
        if ((last_mpdu==0) or (format >= DUT_FrameFormat.VHT)):
            # instead of returning array containing zero pad bytes like matlab, python returns only number of pad bytes.
            formMpduNpad(mpdu_len,numPadBytes);

        # follow a different approach in python unlike matlab.
        # write all the data into a file and read the entire AMPDU at the end of this function to buffer data_bytes_out


        numMpduDLBytes=0;
        delim_buf=[]
        if ( (aggregation_en==1) or (format >= DUT_FrameFormat.VHT) ):
            numMpduDLBytes=4;
            for i in range(0,numMpduDLBytes):
                mpduDL=mpdu_dl[0] & 0xFF;
                data_bytes_out.append(mpduDL)
                mpdu_dl[0]=mpdu_dl[0]>>8;


        if (crc_en==1):
            numCRC32Bytes=4;
        else:
            numCRC32Bytes=0;

        for i in range(0,num_bytes+numCRC32Bytes):
            data_bytes_out.append(str(mpdu_with_crc[i]))


        psdu_len=[0]
        psdu_len[0]=0;


        length_of_data_bytes_out =  length_of_data_bytes_out + numMpduDLBytes+num_bytes+ \
                                    numCRC32Bytes+(num_spacing*4);


        if (last_mpdu==1):

            #length(data_bytes_out);
            apep_len = length_of_data_bytes_out;

            if (format >= DUT_FrameFormat.VHT):
                # VHT mode
                num_spacing = 0;
                num_flush_bytes = 5;
            elif (format == DUT_FrameFormat.DSSS):
                num_spacing = 0;
                num_flush_bytes = 0;
                psdu_len[0]    = apep_len;
            else:
                psdu_len_tmp=[0]
                psdu_len_tmp[0]=0;

                num_spacing = 0;
                num_flush_bytes = 0;
                psdu_len[0]     = apep_len;

        else:
            # this condition will be hit only if it is multipacket aggregation
            last_mpdu = 0;
            apep_len = 0;
            psdu_len[0] = 0;
            num_spacing = spacing_arr[mpdu_idx];

        if(num_spacing != 0):
            mpdu_spacing = [0]*4*num_spacing;
            formMpduSpacing(num_spacing,mpdu_spacing);

            #data_bytes_out= [data_bytes_out;mpdu_spacing];
            for i in range(0, ((4*num_spacing)) ):
                data_bytes_out.append(str(mpdu_spacing[i]))

        length_of_data_bytes_out1 = length_of_data_bytes_out1+ numMpduDLBytes+ \
                                    num_bytes+numCRC32Bytes+(4*num_spacing)


    debugPrint("data length = " + str(length_of_data_bytes_out1))
    return length_of_data_bytes_out1
