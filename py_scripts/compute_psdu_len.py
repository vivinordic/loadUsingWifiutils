import math

def compute_psdu_len(mstbc,apep_len,nes,ndbps,ldpc_en, psdu_len):

    # input parameters: mstbc,apep_len,nes,ndbps,ldpc_en
    # output parameter: psdu_len:  array of size 1.

    if (ldpc_en==1):
        nsyminit = mstbc * ( math.ceil((8.0*apep_len + 16)/(float(mstbc*ndbps))) );
        psdu_len[0] = math.floor(float(nsyminit*ndbps - 16)/8.0);
    else:
        nsym = mstbc * math.ceil((8.0*apep_len + 16 + 6.0*nes)/(float(mstbc*ndbps)));
        psdu_len[0] = math.floor((nsym*ndbps - 16 - 6.0*nes)/8.0);

