import numpy as np
import os 
import progressbar
import time
import matplotlib.pyplot as plt
from IPython.display import display, clear_output

class ClassCPA:
    
    def __init__(self,n_class=256,s_range=(0,10),n_chunks=100):
        
        self.sum_avg = np.zeros(s_range[1]-s_range[0],dtype=np.double)
        self.sum_var = np.zeros(s_range[1]-s_range[0],dtype=np.double)
        self.sum_avg_class = np.zeros((256,s_range[1]-s_range[0]),dtype=np.double)
        self.sum_pop_class = np.zeros(256,dtype=np.uint32)
        
        self.concord = np.zeros((n_chunks,256),dtype=np.double)
        
        plt.rcParams['figure.figsize'] = [20, 10]
        
        self.fig = plt.figure()
        gs = self.fig.add_gridspec(2,2)
        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax2 = self.fig.add_subplot(gs[1, 0])
        self.ax3 = self.fig.add_subplot(gs[:, 1])


    def accumulate(self,traces,messages,i_byte):
        
        for i in range(traces.shape[0]):
            self.sum_avg += traces[i]
            self.sum_var += np.square(traces[i])
            self.sum_avg_class[messages[i][i_byte]] += traces[i]
            self.sum_pop_class[messages[i][i_byte]] += 1
            
    def correlate(self,selection_fct=None, n_hyp=256, mask = 0xFF,hw=True):

        n_class = self.sum_avg_class.shape[0]
        n_trace = np.sum(self.sum_pop_class)
        n_sample = self.sum_avg.shape[0]
                
        correlation = np.zeros((n_class,n_sample),dtype=np.double)
        
        # global averages
        global_avg =  np.divide(self.sum_avg,n_trace) 
        global_var =  np.divide(self.sum_var,n_trace) - np.square(global_avg)
        
        x_class_avg = np.divide(self.sum_avg_class,self.sum_pop_class[:, np.newaxis],\
            out=np.zeros(self.sum_avg_class.shape, dtype=float), where=self.sum_pop_class[:, np.newaxis]!=0) 
        
        # turn global variance into standard deviation
        x_global_std = np.sqrt(global_var)
        x_global_avg = global_avg
        
        for i_hyp in progressbar.progressbar(range(n_hyp)):
            y_class_hyp = np.array([self.get_leakage_model_val(selection_fct,i_class,i_hyp,hw=hw,mask=mask) for i_class in range(n_class)],dtype=float)
            y_class_avg = np.divide(np.sum(np.multiply(self.sum_pop_class,y_class_hyp),axis=0),n_trace)         
            y_class_var = np.divide(np.sum(np.multiply(self.sum_pop_class, np.square(y_class_hyp)),axis=0),n_trace) - np.square(y_class_avg) 
            y_class_std = np.sqrt(y_class_var)       
            DXY = np.sum(np.multiply(self.sum_pop_class[:, np.newaxis],np.multiply(x_class_avg,y_class_hyp[:, np.newaxis])),axis=0)
            correlation[i_hyp] = np.divide(DXY, n_trace) - np.multiply(x_global_avg, y_class_avg)
            std = np.multiply(y_class_std,x_global_std)
            correlation[i_hyp] = np.divide(correlation[i_hyp], std,out=np.zeros(correlation.shape[1], dtype=float), where=std!=0) 
        
        return abs(correlation)
    
    def get_leakage_model_val(self,selection_fct,message,hyp,hw=True,mask=0xFF):

        if hw:
            return bin(selection_fct(hyp,message) & mask).count("1")
        else:
            return selection_fct(hyp,message) & mask

    def plot_corr(self,corr,expected_key,n_trace,i_byte,i_chunk):
        
        self.concord[i_chunk] = np.max(corr,axis=1)
        key_guess = np.argmax(np.max(np.abs(corr),axis=1))  
        
        clear_output(wait=True)
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        self.ax1.plot(corr.transpose(),"lightgrey")
        self.ax1.set_xlabel('Samples') 
        self.ax1.set_ylabel('Corr') 
        
        self.fig.suptitle('CPA results: nTrace = %d, Byte: %d, Guess: 0x%02x'%(n_trace,i_byte,key_guess))
        
        self.ax1.set_title('Temporal Correlation')
        self.ax2.set_title('Average Power Consumption')
        self.ax3.set_title('Key Guess Progression')
        
        self.ax2.plot(self.sum_avg/n_trace)
        self.ax3.plot(self.concord,"lightgrey")
        
        if key_guess == expected_key:
            self.ax1.plot(corr[expected_key],"r")
            self.ax3.plot(self.concord[:,expected_key],"r")
        else:
            self.ax1.plot(corr[expected_key],"b:")
            self.ax1.plot(corr[key_guess],"r:")
            self.ax3.plot(self.concord[:,expected_key],"b:")
            self.ax3.plot(self.concord[:,key_guess],"r:")
        
        display(self.fig)