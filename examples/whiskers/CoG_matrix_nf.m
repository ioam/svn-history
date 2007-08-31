%function [pattern] = CoG_matrix(shuf, gang, w)
w=3;
gang=8;
seed=6445;
shuf = shuffle(w,gang,seed);

% Where in the ring network did that barrelette cell come from?
% need to return a matrix the size of the barrelette sheet which holds a
% value between 0 and 1, represnting the preffered deflection of each
% barrelette cell in its location. Something similar to pref_ang_vect but
% specified in range 0 to 2*pi. 

pattern = zeros(gang*w,gang*w);

g=gang^2;
pref_angles = 0:(360/(g-1)):360;
pref_rads = (pref_angles./(2*pi))*360;
p = pref_rads./max(pref_rads);

rates = repmat(p',1,(w^2));
n=gang;

% if shuffle is not being used then project rates to their ordinal reshape co-ordinate
if shuf ==0

    for x = 1:w
        for y = 1:w
            pattern(((x-1)*n)+1:((x-1)*n)+n,((y-1)*n)+1:((y-1)*n)+n) = reshape(rates(:,((x-1)*w)+y),n,n)';
        end
    end

    % if shuffle is being used then rates are sent to a random co-ordinate
else

    shuf_rates = zeros(1,gang^2);

    for x = 1:w
        for y = 1:w
            for i = 1:gang^2
                shuf_rates(i) = rates(shuf(((x-1)*w)+y,i),((x-1)*w)+y);
            end
            pattern(((x-1)*n)+1:((x-1)*n)+n,((y-1)*n)+1:((y-1)*n)+n) = reshape(shuf_rates,n,n)';
        end
    end
end

figure(1)
imagesc(pattern)