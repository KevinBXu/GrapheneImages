function [b_x,b_y,scale]=custom_strain(theta, alpha, beta, gamma, n_bubbles, centers, inner_rs, outer_rs, base, bubble_field)

%Based on Stephen Carr's "custom strain simulation"
% Create a shift vector field given a base distortion and a variable number
% of bubbles of other distortions

% arguments:
% theta: twist in degrees
% alpha: isotropic strain
% beta: uniaxial strain
% gamma: shear strain
% n_bubbles: number of bubbles you want to create (int)
% centers: coordinates of centers of bubbles in Angstroms (n_bubblesx2 vector)
% inner_rs: inner radii of bubbles in Angstroms (1xn_bubbles vector)
% outer_rs: outer radii of bubbles in Angstroms (1xn_bubbles vector)
% base: which strain component makes up the bulk of the image (1=cw_rot, 2=iso, 3=uni, 4=shear, 5=ccw_rot)
% bubble_field: which strain component is added to base in each bubble (1xn_bubbles vector, same values as above)

% outputs:
% b_x: x-component of shift vector field
% b_y: y-component of shift vector field
% scale: image scale in nm/pixel

% Example: [b_x,b_y,scale]=custom_strain(4, 0.01, 0.01, 0.01, 2, [0, 50; 0, -30], [30,20], [50,30], 1, [2,3]);

%Example values for the inputs
% theta = 4; % twist, in degrees
% alpha = 0.02; % isotropic 
% beta = 0.01; % uniaxial
% gamma = 0; % shear

%n_bubbles = 2;

% % location of the bubbles
% centers = [0 -70
%            0  60];

% background field
%b_mat_base = cw_rot;

% % inner and outer radii of the bubbles
% inner_rs = [20 30];
% outer_rs = [30 100];


R_mat = [cosd(theta) sind(theta)
        -sind(theta) cosd(theta)];

ccw_rot = -(eye(2) - R_mat);
cw_rot = -(eye(2) - R_mat');
isotropic = [alpha 0 ; 0 alpha];
uniaxial = [beta 0 ; 0 -beta];
shear = [0 gamma; gamma 0];


       
components=cat(3, cw_rot, isotropic, uniaxial, shear, ccw_rot);


b_mat_base=squeeze(components(:,:,base));

% % bubble field
for n=1:n_bubbles
   b_mat_bubbles(n,:,:) = squeeze(components(:,:,bubble_field(n))); 
end


% size of the plotting window, in Ang.
ax_m = 150;
% sampling density for the coloring (RGB lines)
n_pts = 300;

scale = (2*ax_m/10)/n_pts; %scale in nm/pixel


% build a mesh of positions
dx_grid = linspace(-ax_m,ax_m,n_pts);
dx_grid = dx_grid(1:end-1);
[mesh_x, mesh_y] = meshgrid(dx_grid,dx_grid);

r_mesh_x = mesh_x;
r_mesh_y = mesh_y;

% put in the base field
b_mat = b_mat_base;
b_mesh_x0 = b_mat(1,1)*(r_mesh_x) + b_mat(1,2)*(r_mesh_y);
b_mesh_y0 = b_mat(2,1)*(r_mesh_x) + b_mat(2,2)*(r_mesh_y);
b_mesh_xinterp = b_mesh_x0;
b_mesh_yinterp = b_mesh_y0;

% perform the bubble interpolants for additional fields
for idx = 1:n_bubbles

    inner_r = inner_rs(idx);
    outer_r = outer_rs(idx);
    b_mat = squeeze(b_mat_bubbles(idx,:,:));
    
    c = centers(idx,:);
    b_mesh_x_vortex = b_mat(1,1)*(r_mesh_x-c(1)) + b_mat(1,2)*(r_mesh_y-c(2));% - (1/3*(a(1,1) + a(1,2)));
    b_mesh_y_vortex = b_mat(2,1)*(r_mesh_x-c(1)) + b_mat(2,2)*(r_mesh_y-c(2));% - (1/3*(a(2,1) + a(2,2)));


    x_vortex = r_mesh_x - c(1);
    y_vortex = r_mesh_y - c(2);

    r_vortex = sqrt(x_vortex.^2 + y_vortex.^2);

    dr = (outer_r - r_vortex)/(outer_r - inner_r); % 1 (inner) to 0 (outer);
    rot_scale = (tanh(5*(dr - 0.5))+1)/2;

    rot_scale(r_vortex < inner_r) = 1;
    rot_scale(r_vortex > outer_r) = 0;

    b_mesh_xinterp_vortex = rot_scale.*b_mesh_x_vortex;  
    b_mesh_yinterp_vortex = rot_scale.*b_mesh_y_vortex;


    b_mesh_xinterp = b_mesh_xinterp + b_mesh_xinterp_vortex;
    b_mesh_yinterp = b_mesh_yinterp + b_mesh_yinterp_vortex;

end

% % grid spacings for the r-mesh
% r1_dx = r_mesh_x(2,1) - r_mesh_x(1,1);
% r1_dy = r_mesh_y(2,1) - r_mesh_y(1,1);
% r2_dx = r_mesh_x(1,2) - r_mesh_x(1,1);
% r2_dy = r_mesh_y(1,2) - r_mesh_y(1,1);

b_x = b_mesh_xinterp;
b_y = b_mesh_yinterp;


figure()
% quiver plot
quiver_samp = ceil(n_pts/50); % quiver plot density

%splot(1) = subplot(2,1,1);

max_s = size(r_mesh_x,1);
sample_space = 3*quiver_samp;
ds = [1:sample_space:max_s];

quiver(r_mesh_x(ds,ds),r_mesh_y(ds,ds), ...
       b_mesh_xinterp(ds,ds),b_mesh_yinterp(ds,ds),'k');
axis equal
axis([-ax_m ax_m -ax_m ax_m]);
hold on
%set(gca,'xTick',[],'yTick',[])

scatter(centers(:,1), centers(:,2),'xk')

end