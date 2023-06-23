#from CSUtils import DA

def po_init(nrx_active):
    DA.SelectTargetByPattern('HOST')
    #playout memory configuration
    po_mem_config= 0x02400000
    value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, 8, po_mem_config, 0)
    #playout memory offset from base address
    po_offset_address = 0x00000000
    value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_CFG_02')
    DA.WriteMemoryBlock(value, 1, 4, po_offset_address, 0)
    #playout memory base address
    po_base_address = 0x00000000
    value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_CFG_03')
    DA.WriteMemoryBlock(value, 1, 4, po_base_address, 0)

    if(nrx_active == 2):
        #playout memory configuration
        po_mem_config= 0x02400000
        value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_CFG_01')
        DA.WriteMemoryBlock(value, 1, 8, po_mem_config, 0)
        #playout memory offset from base address
        po_offset_address = 0x00000000
        value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_CFG_02')
        DA.WriteMemoryBlock(value, 1, 4, po_offset_address, 0)
        #playout memory base address
        po_base_address = 0x00000000
        value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_CFG_03')
        DA.WriteMemoryBlock(value, 1, 4, po_base_address, 0)



def po_rodin_write_samples(scp_in_re_1, scp_in_im_1, scp_in_re_2, scp_in_im_2, nrx_active,  num_samples):
    DA.SelectTargetByPattern('HOST')
    s_index = 0
    count1 =0
    count2 =0
    shift = 20
    scp_in_int = []
    scp_in2_int = []
    for s_index in range(num_samples*2):
        #data = str(s_index%10)*8
        if(s_index%2==0):
            temp_scp_in = int(scp_in_re_1[count1], 16) << shift
            if (nrx_active ==2):
                temp_scp_in2 = int(scp_in_re_2[count1][0:2]+'00000', 16) << 1
            count1=count1+1
        elif (s_index%2==1):
            temp_scp_in = int(scp_in_im_1[count2], 16) << shift
            if (nrx_active ==2):
                temp_scp_in2 = int(scp_in_im_2[count2][0:2]+'00000', 16) << 1
            count2=count2+1

        scp_in_int.append(temp_scp_in)
        if (nrx_active ==2):
            scp_in2_int.append(temp_scp_in2)

    value = 0x28000000
    DA.WriteMemoryBlock(value, len(scp_in_int), 4, scp_in_int, 0)
    if (nrx_active ==2):
        value = 0x38000000
        DA.WriteMemoryBlock(value, len(scp_in2_int), 4, scp_in2_int, 0)



def po_deassert_memory_map(nrx_active):
    DA.SelectTargetByPattern('HOST')
    #playout memory configuration
    po_mem_config= 0x02200000
    value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_CFG_01')
    DA.WriteMemoryBlock(value, 1, 8, po_mem_config, 0)

    if (nrx_active ==2):
        value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_CFG_01')
        DA.WriteMemoryBlock(value, 1, 8, po_mem_config, 0)


def po_start(num_samples, nrx_active):
    DA.SelectTargetByPattern('HOST')
    #set length of memory
    value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_CFG_04')
    DA.WriteMemoryBlock(value, 1, 2, num_samples, 0)

    if (nrx_active ==2):
        value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_CFG_04')
        DA.WriteMemoryBlock(value, 1, 2, num_samples, 0)


def po_wait_for_done_and_reset(nrx_active):
    DA.SelectTargetByPattern('HOST')
    reset_val = 1
    #write 1 to reset the end flag
    value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_END_STATUS_AND_CLEAR')
    DA.WriteMemoryBlock(value, 1, 2, reset_val, 0)

    if (nrx_active ==2):
        value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_END_STATUS_AND_CLEAR')
        DA.WriteMemoryBlock(value, 1, 2, reset_val, 0)

def po_poll_for_done_and_reset(nrx_active):
    DA.SelectTargetByPattern('HOST')
    #poll for done
    value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
    po_end_status = DA.ReadMemoryBlock(value, 1, 4, 0)
    if(nrx_active == 2):
        value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
        po_end_status2 = DA.ReadMemoryBlock(value, 1, 4, 0)

    while(po_end_status[0] != 2):
        value = DA.EvaluateSymbol('PO_MEM_REGS0.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
        po_end_status = DA.ReadMemoryBlock(value, 1, 4, 0)
        if(nrx_active == 2):
            value = DA.EvaluateSymbol('PO_MEM_REGS1.PO_CAP_MEM_GEN_EVENT_STATUS_AND_CLEAR')
            po_end_status2 = DA.ReadMemoryBlock(value, 1, 4, 0)

        if (nrx_active ==1):
            if(po_end_status[0] == 2):
                break
        elif(nrx_active==2):
            if(po_end_status[0] == 2 and po_end_status2[0] == 2):
                break