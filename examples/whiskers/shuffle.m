function [r] = shuffle(w,g,seed)

% Returns a random permutation of ganglion locations for each whisker, i.e.
% randomise like this once in a model and keep the locations the same
% thoughout training. * Only Randomise Once *

rand('twister', seed);

r = zeros(w^2,g^2);

for p = 1:w^2
    r(p,:) = randperm(g^2);
end