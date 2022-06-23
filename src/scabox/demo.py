from scabox.class_cpa import ClassCPA
from scabox.encrypt import ZyboEncrypt
from scabox.aes import AESSelectionFct

class Demo:
    
    def hw_aes_cpa_demo(zb,i_byte,n_trace,n_sample,chunk_size):
        
        n_chunk = n_trace // chunk_size
        s_range = 0,n_sample

        cpa_class = ClassCPA(256,s_range,n_chunk)

        for i_chunk in range(n_chunk):

            messages,ciphers,traces,key = ZyboEncrypt.get_leakage(zb.zybo,"hw",n_trace=chunk_size,s_range=s_range,chunk_size=chunk_size,use_filt=True,time_out=2)
            cpa_class.accumulate(traces,ciphers,i_byte)
            corr = cpa_class.correlate(AESSelectionFct.invsbox_k_xor_m___xor___m,n_hyp=256,hw=True,mask=0xFF)
            cpa_class.plot_corr(corr,0x50,chunk_size*(i_chunk+1),i_byte,i_chunk)