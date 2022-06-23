import math
import numpy as np

class SmoothFilter:

    @classmethod
    def smooth(cls,data_array,n_sample,smooth_mode="smooth",box_size=10,box_type="blackman"):

        box = math.floor(box_size/2)

        if(smooth_mode == "smooth"): #smooth
            if(box_size%2 == 0):  #even
                data_array[box:n_sample-box+1] = cls.LL_smooth(data_array,box_size,box_type)
                data_array[0:box] = data_array[box]
                data_array[n_sample-box:n_sample] =  data_array[n_sample-box-1]
            else: #odd
                data_array[box:n_sample-box] = cls.LL_smooth(data_array,box_size,box_type)
                data_array[0:box] = data_array[box]
                data_array[n_sample-box-1:n_sample] = data_array[n_sample-box-2]
        else: #antismooth
            temp = cls.LL_smooth(data_array,box_size,box_type)
            if(box_size%2 == 0):  #even
                data_array[box:n_sample-box+1] = data_array[box:n_sample-box+1] - temp
                data_array[0:box] = data_array[box]
                data_array[n_sample-box:n_sample] =  data_array[n_sample-box-1]
            else: #odd
                data_array[box:n_sample-box] = data_array[box:n_sample-box] - temp
                data_array[0:box] = data_array[box]
                data_array[n_sample-box-1:n_sample] = data_array[n_sample-box-2]

        return data_array

    @classmethod
    def LL_smooth(cls, data, box_pts, box_type="blackman"):

        """ apply convolution on the input array

        :param data: input data array
        :type data: array
        :param box_pts: the size of the convolution box in samples
        :type box_pts: int    
        :param box_type: the type of convolution box to use: rectangle, hanning, bartlett or blackman
        :type box_type: str      
        :return: a 2D numpy array containing the filtered curves
        :rtype: numpy 
        """  

        if box_type == "rectangle":
            box = np.ones(box_pts)
        elif box_type == "hanning":
            box = np.hanning(box_pts)
        elif box_type =="bartlett":
            box = np.bartlett(box_pts)
        elif box_type == "blackman":
            box = np.blackman(box_pts)
        else:
            box = np.ones(box_pts)     

        smoothed_data = np.convolve(data, box, mode='valid') / np.sum(box)
        return smoothed_data