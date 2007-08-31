function [rates] = test_deflections(w,gang,rectify,speed,t,active_whisker)

% The same as sweep.m but with stimulus set always to 1 (i.e. no surface)

if active_whisker ==0
    active_whisker = (1:w^2);
end

g = gang^2;
whiskers = ones(w,w); 
rates = zeros(g,w^2); 

pref_angles = 0:(360/(g-1)):360;
pref_ang_vect = repmat(pref_angles,2,1);
pref_ang_vect(1,:) = cosd(pref_ang_vect(1,:));
pref_ang_vect(2,:) = sind(pref_ang_vect(2,:));

stims = zeros(2,w^2);

for a = 1:w;
    for b = 1:w;
        wh = ((a-1)*w)+b;
        if any(wh==active_whisker)
            stim = [(1/speed)*(whiskers(a,b)*((speed)*cosd(t)));(1/speed)*(whiskers(a,b)*((speed)*sind(t)))]; % changed from theta to t
            stims(:,wh) = stim;
            if rectify ==1
                rates(:,wh) = (max(0,(dot((repmat(stim,1,g)), pref_ang_vect))));
            else
                rates(:,wh) = dot((repmat(stim,1,g)),pref_ang_vect);
            end
        end
    end
end
