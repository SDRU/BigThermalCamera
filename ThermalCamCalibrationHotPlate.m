%%FLIR A655. Calibration test with a hot plate. Camera looking at a hot plate vs set temperature of the plate

close all
clear all

Tp = [30.9,36.1,39.8,45.2,50.1,54.8,60.3,65,70.2,75,80.1,85.2,90.1,95,100,105.1,110,115];

for i=1:18
    filename = ['plate',num2str(i),'.tiff'];
    im = importdata(['c:\Users\Sandra Drusova\Nextcloud\Postdoc\Data\20210804 Thermal camera\',filename]);
    x=size(im,1);
    y=size(im,2);

    %%Adding calibration coefficients from software
    % Coefficients for Counts to Radiance
    Cr_0 = -3.42255e-03;
    Cr_1 = 5.01980e-07;
    I = ones(x,y); %must coincide with desired size in x or y if image is squared
    r1 = Cr_0*I;
    % Coefficients for Radiance to Temperature
    Ct_0 = -6.32251e+01;
    Ct_1 = 3.52488e+04;
    Ct_2 = -4.55977e+06;
    Ct_3 = 5.02369e+08;
    Ct_4 = -3.55013e+10;
    Ct_5 = 1.42222e+12;
    Ct_6 = -2.45221e+13;



    IR1=double(im);
    r2 = Cr_1*IR1;
    R = r1 + r2; %Radiance 
    T = Ct_0*ones(size(IR1)) + Ct_1.*R + Ct_2.*R.^2 + Ct_3.*R.^3 + Ct_4.*R.^4 + Ct_5.*R.^5 + Ct_6.*R.^6;
    % T = T-max(max(T))*ones(size(T));
    
    Mp(i) = mean(T(330:end,:),'all'); % mean plate
    Ma(i) = mean(T(1:100,1:100),'all'); % mean air
    
   
%     figure
%     imshow(T,[20,115])
%     colorbar
end

figure
plot(Tp,Mp,'o-')
hold on
plot(Tp,Tp,'ro-')
hold on
plot(Tp, Ma,'ko-')