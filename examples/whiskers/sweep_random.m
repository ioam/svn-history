function [rates] = sweep_random(w,gang,surface,start_point_scaling,rectify,speed,t,time,active_whisker)

% This is exactly the same as sweep.m (i.e. see that for commentary), but
% the angle is randomised (although directed movement, and therefore
% deflection vector length is not).


if active_whisker ==0
    active_whisker = (1:w^2);
end

g = gang^2;
whiskers = zeros(w,w); 
rates = zeros(g,w^2); 


surf_size = length(surface);
mid = surf_size/2;


start_radius = mid*start_point_scaling; 

start_x = mid; 
start_y = mid; 

new_x = start_x+round(start_radius*speed*time*cosd(t));
new_y = start_y-round(start_radius*speed*time*sind(t)); 


pref_angles = 0:(360/(g-1)):360;
pref_ang_vect = repmat(pref_angles,2,1);
pref_ang_vect(1,:) = cosd(pref_ang_vect(1,:));
pref_ang_vect(2,:) = sind(pref_ang_vect(2,:));


w_off = (w-1)/2;
whiskers(:,:) = surface((new_y-w_off:new_y+w_off),(new_x-w_off:new_x+w_off));


for a = 1:w;
    for b = 1:w;
        wh = ((a-1)*w)+b;
        if any(wh==active_whisker)
            stim = [(1/speed)*(whiskers(a,b)*((speed)*cosd(round(rand*360))));(1/speed)*(whiskers(a,b)*((speed)*sind(round(rand*360))))]; 
            if rectify ==1
                rates(:,wh) = (max(0,(dot((repmat(stim,1,g)), pref_ang_vect))));
            else
                rates(:,wh) = dot((repmat(stim,1,g)),pref_ang_vect);
            end
        end
    end
end
