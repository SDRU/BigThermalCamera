# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 10:47:33 2021

@author: Sandora
"""

import os
import PySpin
import sys
import matplotlib.pyplot as plt
import numpy as np
import pdb

def acquire_images(cam, nodemap, nodemap_tldevice, row_low, row_high, col_low, col_high):
    """
    This function acquires and saves 10 images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True

        # Set acquisition mode to continuous
        #
        #  *** NOTES ***
        #  Because the example acquires and saves 10 images, setting acquisition
        #  mode to continuous lets the example finish. If set to single frame
        #  or multiframe (at a lower number of images), the example would just
        #  hang. This would happen because the example has been written to
        #  acquire 10 images while the camera would have been programmed to
        #  retrieve less than that.
        #
        #  Setting the value of an enumeration node is slightly more complicated
        #  than other node types. Two nodes must be retrieved: first, the
        #  enumeration node is retrieved from the nodemap; and second, the entry
        #  node is retrieved from the enumeration node. The integer value of the
        #  entry node is then set as the new value of the enumeration node.
        #
        #  Notice that both the enumeration and the entry nodes are checked for
        #  availability and readability/writability. Enumeration nodes are
        #  generally readable and writable whereas their entry nodes are only
        #  ever readable.
        #
        #  Retrieve enumeration node from nodemap

        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        #
        #  *** NOTES ***
        #  What happens when the camera begins acquiring images depends on the
        #  acquisition mode. Single frame captures only a single image, multi
        #  frame catures a set number of images, and continuous captures a
        #  continuous stream of images. Because the example calls for the
        #  retrieval of 10 images, continuous mode has been set.
        #
        #  *** LATER ***
        #  Image acquisition must be ended when no more images are needed.
        cam.BeginAcquisition()

        print('Acquiring images...')

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Retrieve, convert, and save images
        while True:
            try:

                #  Retrieve next received image
                #
                #  *** NOTES ***
                #  Capturing an image houses images on the camera buffer. Trying
                #  to capture an image that does not exist will hang the camera.
                #
                #  *** LATER ***
                #  Once an image from the buffer is saved and/or no longer
                #  needed, the image must be released in order to keep the
                #  buffer from filling up.
                image_result = cam.GetNextImage()

                #  Ensure image completion
                #
                #  *** NOTES ***
                #  Images can easily be checked for completion. This should be
                #  done whenever a complete image is expected or required.
                #  Further, check image status for a little more insight into
                #  why an image is incomplete.
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:

                    #  Print image information; height and width recorded in pixels
                    #
                    #  *** NOTES ***
                    #  Images have quite a bit of available metadata including
                    #  things such as CRC, image status, and offset values, to
                    #  name a few.
                    # width = image_result.GetWidth()
                    # height = image_result.GetHeight()
                    # print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

                    #  Convert image to mono 8
                    #
                    #  *** NOTES ***
                    #  Images can be converted between pixel formats by using
                    #  the appropriate enumeration value. Unlike the original
                    #  image, the converted one does not need to be released as
                    #  it does not affect the camera buffer.
                    #
                    #  When converting images, color processing algorithm is an
                    #  optional parameter.
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)
                    T = convert_to_temperature(image_converted, row_low,row_high,col_low,col_high)
                    M = np.amax(T)
                    print(M)
                    
                    # if M>30:
                    #     print(M)
                    
                    # # Create a unique filename
                    # if device_serial_number:
                    #     filename = 'Acquisition-%s-%d.tiff' % (device_serial_number, i)
                    # else:  # if serial number is empty
                    #     filename = 'Acquisition-%d.tiff' % i

                    # #  Save image
                    # #
                    # #  *** NOTES ***
                    # #  The standard practice of the examples is to use device
                    # #  serial numbers to keep images of one device from
                    # #  overwriting those of another.
                    # image_converted.Save(filename)
                    # print('Image saved at %s' % filename)

                    #  Release image
                    #
                    #  *** NOTES ***
                    #  Images retrieved directly from the camera (i.e. non-converted
                    #  images) need to be released in order to keep from filling the
                    #  buffer.
                    image_result.Release()
                    

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False
            

        #  End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        cam.EndAcquisition()
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***\n')

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def run_single_camera(cam,row_low, row_high, col_low, col_high):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        
        
        result &= acquire_images(cam, nodemap, nodemap_tldevice,row_low, row_high, col_low, col_high)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False
    except:
        cam.EndAcquisition()
        cam.DeInit()
        result = False

    return result

def convert_to_temperature(image,row_low,row_high,col_low,col_high):
    
    y=image.GetWidth()
    x=image.GetHeight()
    image=image.GetData()
    
    IR=np.reshape(image,[x,y]);
    IR = IR[row_low:row_high,col_low:col_high]
    x = np.shape(IR)[0]
    y = np.shape(IR)[1]
    

    # Adding calibration coefficients from software
    # Coefficients for Counts to Radiance
    Cr_0 = -3.42255e-03
    Cr_1 = 5.01980e-07
    I = np.ones([x,y]) # must coincide with desired size in x or y
    r1 = Cr_0*I
    # Coefficients for Radiance to Temperature
    Ct_0 = -6.32251e+01
    Ct_1 = 3.52488e+04
    Ct_2 = -4.55977e+06
    Ct_3 = 5.02369e+08
    Ct_4 = -3.55013e+10
    Ct_5 = 1.42222e+12
    Ct_6 = -2.45221e+13


    r2 = Cr_1*IR
    R = r1+r2; # Radiance 

    T = Ct_0*np.ones([x,y]) + Ct_1*R + Ct_2*R**2 + Ct_3*R**3 + Ct_4*R**4 + Ct_5*R**5 + Ct_6*R**6
    return T

def convert_to_temperature2(image,row_low,row_high,col_low,col_high):
    y=image.GetWidth()
    x=image.GetHeight()
    image=image.GetData()    
    image=np.reshape(image,[x,y]);
    image = image[row_low:row_high,col_low:col_high]
    
    Emiss = 0.98
    TRefl = 293.15
    TAtm = 293.15
    TAtmC = TAtm - 273.15
    Humidity = 0.55
            
    R = 17496.486328125
    B = 1444.5999755859375
    F = 1.0
    X = 1.899999976158142
    A1 = 0.006568999961018562
    A2 = 0.012620000168681145
    B1 = -0.00227600010111928
    B2 = -0.006670000031590462
    J1 = 68.02445983886719
    J0 = 4458
    
    Dist = 0.8
    ExtOpticsTransmission = 1
    ExtOpticsTemp = TAtm

    H2O = Humidity * np.exp(1.5587 + 0.06939 * TAtmC - 0.00027816 * TAtmC * TAtmC + 0.00000068455 * TAtmC * TAtmC * TAtmC)

    Tau = X * np.exp(-np.sqrt(Dist) * (A1 + B1 * np.sqrt(H2O))) + (1 - X) * np.exp(-np.sqrt(Dist) * (A2 + B2 * np.sqrt(H2O)))

    # Pseudo radiance of the reflected environment
    r1 = ((1 - Emiss) / Emiss) * (R / (np.exp(B / TRefl) - F))

    # Pseudo radiance of the atmosphere
    r2 = ((1 - Tau) / (Emiss * Tau)) * (R / (np.exp(B / TAtm) - F))

    # Pseudo radiance of the external optics
    r3 = ((1 - ExtOpticsTransmission) / (Emiss * Tau * ExtOpticsTransmission)) * (R / (np.exp(B / ExtOpticsTemp) - F))

    K2 = r1 + r2 + r3
    
    image_Radiance = (image - J0) / J1
    image_Temp = (B / np.log(R / ((image_Radiance / Emiss / Tau) - K2) + F)) - 273.15
    # Displaying an image of temperature (degrees Celsius) when streaming mode is set to Radiometric
    # plt.imshow(image_Temp, cmap='inferno', aspect='auto')
    
    return image_Temp