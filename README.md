A code to interface thermal camera FLIR A655sc
https://www.flir.eu/products/a655sc/

Paid software to read out images is called ResearchIR. It requires a green USB key.
https://support.flir.com/SwDownload/app/RssSWDownload.aspx?ID=12401


Free software to read out images is called SpinView. When reading out the image, it's difficult to see anything. Set format to Mono16 or Mono8.


Spinnaker SDK library can be downloaded here 
https://flir.app.boxcn.net/v/SpinnakerSDK/folder/68522911814

Calibration coefficients to translate counts to radiance to temperature come from ResearchIR calibration file, –40°C to 150°C range.
