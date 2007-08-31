function [surface] = pipe (surf_size,sigma_ON,sigma_OFF,OFF_MAX,w)

% Generates a stimululs surface by rotating 1D the profile 'stim' around the
% centre of a 2D array using trig

sig_ON = surf_size*sigma_ON;
sig_OFF = surf_size*sigma_OFF;

surf_mid = (surf_size/2);
surface = zeros(surf_size,surf_size);

stim_length = surf_size;
stim = zeros(1,stim_length);
stim_sigma_ON = stim_length/sig_ON;
stim_sigma_OFF = stim_length/sig_OFF;

centre_dist = w+3;
RA_SA_dist =surf_size*0.2;

stim (centre_dist:stim_length)= exp(-0.5.*(((0:stim_length-centre_dist).^2)./(stim_sigma_ON.^2)));
stim (RA_SA_dist:stim_length)= OFF_MAX*(exp(-0.5.*(((0:stim_length-RA_SA_dist).^2)./(stim_sigma_OFF.^2))));


max_distance = sqrt(2*((surf_mid)^2)); 

for i = 1:surf_size;
    for j = 1:surf_size;
    
        distance = sqrt( (surf_mid-i)^2 + (surf_mid-j)^2);
        if distance < 1; distance = 1; end
        surface(i,j) = stim(ceil((distance/max_distance)*length(stim)));
      
    end
end

