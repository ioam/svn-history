function [rates] = sweep_uncor(w,gang,surface,step_size,rectify,speed,t,time,active_whisker)

% INPUT: the route number of whiskers, route ganglion cells, a surface to sweep against,
% a scaling parameter for the size of a step across the surface (allows scaling for surfaces
% defined over more points), rectification (1 = rectify),
% speed of sweep, angle of sweep in degrees, time step during sweep, and
% which whiskers are being stimulated (0 for all of them).
% OUTPUT: firing rates for the ganglion cells associated with each whisker
% (ganglions, whiskers), according to the dot product

% define which whiskers will recieve input
if active_whisker ==0
    active_whisker = (1:w^2);
end

% define parameters
g = gang^2;
whiskers = zeros(w,w); 
rates = zeros(g,w^2); 
surf_size = length(surface);
mid = surf_size/2;

% set step size and pre-sweep co-ordinates
start_radius = mid*step_size; 
start_x = mid; start_y = mid;  

% set the post sweep co-ordinates
new_x = start_x+round(start_radius*speed*time*cosd(t));
new_y = start_y-round(start_radius*speed*time*sind(t)); 

% define MEA's for the ganglion ring network
pref_angles = 0:(360/(g-1)):360;
pref_ang_vect = repmat(pref_angles,2,1);
pref_ang_vect(1,:) = cosd(pref_ang_vect(1,:));
pref_ang_vect(2,:) = sind(pref_ang_vect(2,:));

% set stimulus to surface height at post-sweep position
w_off = (w-1)/2;
whiskers(:,:) = surface((new_y-w_off:new_y+w_off),(new_x-w_off:new_x+w_off));

stims = zeros(2,w^2);

for a = 1:w;
    for b = 1:w;
        wh = ((a-1)*w)+b;
        if any(wh==active_whisker)
            if wh==5;
            stim = [(1/speed)*(whiskers(a,b)*((speed)*cosd(round(rand*360))));(1/speed)*(whiskers(a,b)*((speed)*sind(round(rand*360))))];
            stims(:,wh) = stim;
            else
            stim = [(1/speed)*(whiskers(a,b)*((speed)*cosd(t)));(1/speed)*(whiskers(a,b)*((speed)*sind(t)))];
            stims(:,wh) = stim;
            end
            if rectify ==1
                rates(:,wh) = (max(0,(dot((repmat(stim,1,g)), pref_ang_vect))));
            else
                rates(:,wh) = dot((repmat(stim,1,g)),pref_ang_vect);
            end
        end
    end
end

