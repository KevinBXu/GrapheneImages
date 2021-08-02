function [rgb_img,cont_img, strainfig]=visualize_strainfield(xcomp, ycomp, a_mag, scale, a_dir_r, a_dir_g)

% Based on a section of Stephen Carr's Custom Strain Simulations
% Given a shift vector field and lattice vectors, create images of domains
% and strain field


% arguments:
% xcomp: x-component of the shift vector field (nxm matrix)
% ycomp: y-component of the shift vector field (nxm matrix)
% a_mag: magnitude of the lattice constant in nm (scalar)
% scale: scale of the image in nm/pixel
% a_dir_r: unit vector in direction of a lattice vector (1x2 vector)
% a_dir_g: unit vector in direction of other lattice vector (1x2 vector)

% outputs:
% rgb_img: simulation of the dark field image with red, green, and blue
% dislocation lines. (nxm matrix)
% cont_img: representation of the shift vector as a continuous color wheel
% strainfig: image of the plots of the four strain components

%a = 2.46*[1 0.5
%          0 -sqrt(3)/2]/scale/10;

a = a_mag/scale*[a_dir_r.',a_dir_g.'];
      
     % Definitions of the RGB lines
%line_1: a*x + b*y = 0; a = a_sc(1,1), b = a_sc(2,1)
a1 =  a(2,1);
b1 = -a(1,1);
d_l1 = @(r) abs(a1*r(1) + b1*r(2))/sqrt(a1^2 + b1^2); %Distance from point r to line1 

%line_2: a*x + b*y = 0; a = a_sc(1,2), b = a_sc(2,2)
a2 =  -a(2,2);
b2 =  a(1,2);
d_l2 = @(r) abs(a2*r(1) + b2*r(2))/sqrt(a2^2 + b2^2);

%line_3: 
a3 =  -a1-a2;
b3 =  -b1-b2;
d_l3 = @(r) abs(a3*r(1) + b3*r(2))/sqrt(a3^2 + b3^2);
   
sigma = 0.2; % smearing of colored segments

      
inv_a = a^-1;

array_size=size(xcomp);
[r_mesh_x,r_mesh_y] = meshgrid(1:array_size(2),1:array_size(1));

b_x=xcomp;
b_y=ycomp;

% smoothing =5;
% b_x = imgaussfilt(xcomp,smoothing);
% b_y = imgaussfilt(ycomp, smoothing);

% grid spacings for the r-mesh
r1_dx = r_mesh_x(2,1) - r_mesh_x(1,1);
r1_dy = r_mesh_y(2,1) - r_mesh_y(1,1);
r2_dx = r_mesh_x(1,2) - r_mesh_x(1,1);
r2_dy = r_mesh_y(1,2) - r_mesh_y(1,1);

for x_idx = r_mesh_x(1,:)
    for y_idx = r_mesh_y(:,1)'
        b_h = [b_x(x_idx,y_idx);b_y(x_idx,y_idx)];
        b_h_mod = a*mod(inv_a*b_h,1);
        d1_h = 999;
        d2_h = 999;
        d3_h = 999;

        for sc_dx = -1:1
            for sc_dy = -1:1
                sc_h = sc_dx*a(:,1) + sc_dy*a(:,2);
                d1_h = min(d_l1(b_h_mod+sc_h),d1_h);
                d2_h = min(d_l2(b_h_mod+sc_h),d2_h);
                d3_h = min(d_l3(b_h_mod+sc_h),d3_h);
            end
        end
%         rgb_h = [1 - exp(-min(d2_h,d3_h).^2/sigma.^2)
%                  1 - exp(-min(d3_h,d1_h).^2/sigma.^2)
%                  1 - exp(-min(d1_h,d2_h).^2/sigma.^2)];
        
        
%         rgb_h = [exp(-d1_h.^2/sigma.^2)
%                  exp(-d2_h.^2/sigma.^2)
%                  exp(-d3_h.^2/sigma.^2)];
            
        rgb_h = [cutoff(d1_h)
                 cutoff(d2_h)
                 cutoff(d3_h)];
             
        
       %Create a rainbow coloring for the vector
       b_h_hex=round(inv_a*b_h);
       m=b_h_hex(1);
       n=b_h_hex(2);
       remainder = b_h - a(:,1)*m - a(:,2)*n;
       
       
       sat = exp(-(norm(remainder)/(0.5*a_mag/scale))^2); %norm(remainder)/3; %/(a_mag/scale);
       hue = (atan2(remainder(2),remainder(1))+pi)/(2*pi);
       cont_col = hsv2rgb([hue, sat, 1]);
       
       rgb_img(x_idx,y_idx,:)=rgb_h; %red green and blue domain wall lines
       cont_img(x_idx,y_idx,:)=cont_col; %continuous color distribution around the circle

       
       
       
    end
end
[uni, iso, shear, twist, strainfig]=strain_from_u(xcomp, ycomp);

end

function [color] = cutoff(x)
if x <= 0.1
    color = 255;
else
    color = 0;
end
end