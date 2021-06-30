function [uni, iso, shear, twist, strainfig]=strain_from_u(xcomp, ycomp)

% Plot the four strain components given a shift vector field

% arguments:
% xcomp: x-component of the shift vector field (nxm matrix)
% ycomp: y-component of the shift vector field (nxm matrix)

% outputs:
% uni, iso, shear, twist: four strain components (n-1xm-1 matrix each) 
% strainfig: image of the four subplots of the strain components


uxx=diff(xcomp,1,2);
uxy=diff(xcomp,1,1);
uyx=diff(ycomp,1,2);
uyy=diff(ycomp,1,1);

limts=size(xcomp)-1;

uni = (uxx(1:limts(1),1:limts(2))-uyy(1:limts(1),1:limts(2)))/2;
shear = (uxy(1:limts(1),1:limts(2))+uyx(1:limts(1),1:limts(2)))/2;
twist = asin((uxy(1:limts(1),1:limts(2))-uyx(1:limts(1),1:limts(2)))/2);    
iso = (uxx(1:limts(1),1:limts(2))+uyy(1:limts(1),1:limts(2)))/2-cos(twist)+1;

%Plot strain components
figure()
subplot(2,2,1)
imagesc(iso*100)
title('isotropic (%)')
caxis([-0.5,0.5])
colorbar
subplot(2,2,2)
imagesc(uni*100)
title('uniaxial (%)')
caxis([-0.5,0.5])
colorbar
subplot(2,2,3)
imagesc(shear*100)
title('shear (%)')
caxis([-0.5,0.5])
colorbar
subplot(2,2,4)
imagesc(twist*360/6.28)
title('twist (deg)')
caxis([-3,3])
colorbar

colormap bluewhitered

F = getframe(gcf);
[strainfig, Map] = frame2im(F);

end