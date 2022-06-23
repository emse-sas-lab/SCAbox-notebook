import time
import serial
import serial.tools.list_ports
import numpy as np

from scabox.smooth import SmoothFilter

START_RAW_TAG = b"\xfd\xfd\xfd\xfd"
START_TRACE_TAG = b"\xfe\xfe\xfe\xfe"
END_ACQ_TAG = b"\xff\xff\xff\xff"
END_LINE_TAG = b";;\n"
    

class ZyboEncrypt:

    def encrypt(zybo, mode, message,key,s_min,s_max):
           
        cmd = "aes -m %s -d %s -k %s -c %d -e %d\n"%(mode,"".join("%02x"%e for e in message),"".join("%02x"%e for e in key),s_min,s_max)
        
        #print("Command sent: %s"%cmd,end="")
        
        byte_msg = cmd.encode()

        # Set a long timeout to complete handshake
        zybo.timeout = 1

        # Send aes command to zybo
        zybo.write(byte_msg)
        
        # Read and discard everything that may be in the input buffer
        _ = zybo.read_all()
        
        # Send fifo command to zybo
        zybo.write("fifo\n".encode())
               
        # Read in what zybo sent
        header = zybo.read_until("code: ".encode())    
        data = list(zybo.read_until(";;".encode())[0:-2])
        
        if (s_max-s_min)-len(data) >= 0:
            data = None
            res = -1
        else:
            data = np.array(data)[s_min:s_max]
            data = SmoothFilter.smooth(data,len(data),"antismooth",box_size=20,box_type="blackman")
            res = 0
                               
        # Reset the timeout
        zybo.timeout = 5

        return res,data
  
    def get_leakage(zybo, mode, n_trace, s_range, chunk_size = 250,use_filt=True,time_out=10):
        
        i_trace = 0
        n_sample = s_range[1] - s_range[0]
        
        max_fail = 10000
        
        fail_count = 0
        msg_fail_count = 0
        cph_fail_count = 0
        smp_fail_count = 0
        
        key = [0]*16
        key_parsed = False
        msg_parsed = False
        cph_parsed = False
        smp_parsed = False
        
        messages = np.zeros((n_trace,16),dtype=np.uint8)
        ciphers = np.zeros((n_trace,16),dtype=np.uint8)
        key = np.zeros(16,dtype=np.uint8)
        samples = np.zeros((n_trace,n_sample),dtype=np.double)
            
        
        # Read and discard everything that may be in the input buffer
        _ = zybo.read_all() 
        
        while(i_trace < n_trace):
            
            print("\rTrace acquired: %d/%d Errors: %d"%(i_trace,n_trace,fail_count),end="")
            
            # build the command and send it to the zybo board
            cmd = "sca -m %s -t %d -c %d -e %d\n"%(mode, chunk_size, s_range[0], s_range[1])
            byte_cmd = cmd.encode()

            # Set a long timeout to complete handshake
            timeout = zybo.timeout
            zybo.timeout = time_out
                         
            # Send sca command to zybo
            zybo.write(byte_cmd)

            # Read header info 
            header = zybo.read_until(START_TRACE_TAG)
            
            # Extract the key
            if not key_parsed:
                res,key = DataParser.parse_key(header)
                if not res: key_parsed = True
                           
            # Read all the data from serial
            serial_data = zybo.read_until(b";;\r\n>")
            data_lines = serial_data.split(b";;\r\n")
                        
            # For each line, extract message, cipher and samples
            for i_line,line in enumerate(data_lines):
                                                
                # init parsed states
                if line.find(START_TRACE_TAG) > -1:                                      
                    cph_parsed = False
                    msg_parsed = False
                    smp_parsed = False
                    
                # parse the message
                if line.find(b"plains") > -1: 

                    res,pt = DataParser.parse_message(line)
                    if not res:
                        msg_parsed = True 
                    else:
                        fail_count += 1
                        msg_fail_count += 1
                    
                # parse the cipher
                if line.find(b"ciphers") > -1: 

                    res,ct = DataParser.parse_cipher(line)
                    if not res:
                        cph_parsed = True 
                    else:
                        fail_count += 1
                        cph_fail_count += 1
                        
                # parse the samples
                if line.find(b"code") > -1:
                    
                    res,data = DataParser.parse_samples(line,s_range)
                                        
                    if not res:
                        smp_parsed = True 
                    else:
                        fail_count += 1
                        smp_fail_count += 1
                                                    
                if smp_parsed and cph_parsed and msg_parsed:
                    messages[i_trace] = pt 
                    ciphers[i_trace] = ct 
                    if use_filt:
                        samples[i_trace] = SmoothFilter.smooth(data,len(data),"antismooth",box_size=25,box_type="blackman")
                    else:
                        samples[i_trace] = data
                    i_trace += 1
                    
                    cph_parsed = False
                    msg_parsed = False
                    smp_parsed = False
                
                if i_trace >= n_trace:
                    break 
                    
                if fail_count > max_fail:
                    print("\nMax error surpassed exiting\n") 
                    i_trace = n_trace
                    break
        
        print("\rTrace acquired: %d/%d Errors: %d"%(i_trace,n_trace,fail_count))
        print("Message Errors: %d"%msg_fail_count)
        print("Cipher Errors: %d"%cph_fail_count)
        print("Sample Errors: %d"%smp_fail_count)
        
        # Reset the timeout
        zybo.timeout = timeout

        # Read and discard everything that may be in the input buffer
        _ = zybo.read_all()     

        return messages,ciphers,samples,key
            
class DataParser:
    
    def parse_key(str_data):
    
        try: 
            key = str_data[str_data.find(b"keys:")+5:str_data.find(END_LINE_TAG)-7].replace(b' ', b'')
            key_str = key.decode("utf-8") 
            key = [int(key_str[i*2]+key_str[i*2+1],16) for i in range(0,16)]
        except:
            #print("Error during key parsing, please retry")
            return -1,""
        else:
            #print("Key: %s"%key_str)
            return 0,key
                
    def parse_message(str_data):
        
        try:
            message = str_data[str_data.find(b"plains:")+7::].replace(b' ', b'')               
            message_str = message.decode("utf-8") 
            message = [int(message_str[i*2]+message_str[i*2+1],16) for i in range(0,16)]
        except:
            #print("Error during message parsing")
            return -1,""
        else:
            return 0,message
        
    def parse_cipher(str_data):
        
        try:
            cipher = str_data[str_data.find(b"ciphers:")+8::].replace(b' ', b'')                
            cipher_str = cipher.decode("utf-8") 
            cipher = [int(cipher_str[i*2]+cipher_str[i*2+1],16) for i in range(0,16)]
        except:
            #print("Error during cipher parsing")
            return -1,""
        else:
            return 0,cipher
        
    def parse_samples(str_data,s_range):
        
        n_sample = s_range[1] - s_range[0]
        
        try: 
            samples = list(str_data[str_data.find(b"code:")+6::])
        except:
            #print("Error during sample parsing")
            return -1,None
        else:
            
            if n_sample-len(samples) != 0:
                
                #print(len(samples))
                #return 0,np.pad(samples,(0,n_sample-len(samples)),'constant')
                return -1,None
            else:
                return 0,np.array(samples)[s_range[0]:s_range[1]]
            