function [whiskerbot_rates] = whiskerbot_frame (whiskerbot_x_strains, whiskerbot_y_strains,gain,rectify,gang,time,stim_plot)


%whiskerbot_x_strains=L_x_strain;
%whiskerbot_y_strains=L_y_strain;
%rectify=1;
%gng=8;
%time = 32;
w = 3;

g = gang^2;
whiskerbot_rates = zeros(g,w^2); 

%gain = 3.14;

% just reshape strains to be in the right order
horizontal_strain = zeros(w^2,length(whiskerbot_x_strains));
horizontal_strain(1,:) = whiskerbot_x_strains(3,:).*gain;
horizontal_strain(2,:) = whiskerbot_x_strains(6,:).*gain;
horizontal_strain(3,:) = whiskerbot_x_strains(9,:).*gain;
horizontal_strain(4,:) = whiskerbot_x_strains(2,:).*gain;
horizontal_strain(5,:) = whiskerbot_x_strains(5,:).*gain;
horizontal_strain(6,:) = whiskerbot_x_strains(8,:).*gain;
horizontal_strain(7,:) = whiskerbot_x_strains(1,:).*gain;
horizontal_strain(8,:) = whiskerbot_x_strains(4,:).*gain;
horizontal_strain(9,:) = whiskerbot_x_strains(7,:).*gain;

vertical_strain = zeros(w^2,length(whiskerbot_y_strains));
vertical_strain(1,:) = whiskerbot_y_strains(3,:).*gain;
vertical_strain(2,:) = whiskerbot_y_strains(6,:).*gain;
vertical_strain(3,:) = whiskerbot_y_strains(9,:).*gain;
vertical_strain(4,:) = whiskerbot_y_strains(2,:).*gain;
vertical_strain(5,:) = whiskerbot_y_strains(5,:).*gain;
vertical_strain(6,:) = whiskerbot_y_strains(8,:).*gain;
vertical_strain(7,:) = whiskerbot_y_strains(1,:).*gain;
vertical_strain(8,:) = whiskerbot_y_strains(4,:).*gain;
vertical_strain(9,:) = whiskerbot_y_strains(7,:).*gain;


%INITIALISE GANGLION RING MODEL
pref_angles = 0:(360/(g-1)):360;
pref_ang_vect = repmat(pref_angles,2,1);
pref_ang_vect(1,:) = cosd(pref_ang_vect(1,:));
pref_ang_vect(2,:) = sind(pref_ang_vect(2,:));

stims = zeros(2,w^2);

for a = 1:w;
    for b = 1:w;
        wh = ((a-1)*w)+b;
       
            stim = [horizontal_strain(wh,time);vertical_strain(wh,time)];
            %stim = [(1/speed)*(whiskers(a,b)*((speed)*cosd(t)));(1/speed)*(whiskers(a,b)*((speed)*sind(t)))]; % changed from theta to t
            stims(:,wh) = stim;
            if rectify ==1
                whiskerbot_rates(:,wh) = (max(0,(dot((repmat(stim,1,g)), pref_ang_vect))));
            else
                whiskerbot_rates(:,wh) = dot((repmat(stim,1,g)),pref_ang_vect);
            end
        
    end
end


%if stim_plot==1
    
%    figure(1);
%for j = 1:w^2;
%subplot(w,w,j);plot(pref_ang_vect(1,:),pref_ang_vect(2,:),'o')
%axis([-1 1 -1 1]);
%hold on; plot([0 stims(1,j)],[0 stims(2,j)]); hold off;
%end


%figure(2)
%radians=(pref_angles./360)*(2*pi);
%for j=1:w^2;
%subplot(w,w,j);plot(radians,whiskerbot_rates(:,j));
%axis([0 (2*pi) 0 1]) 
%%axis([0 360 0 1])
%%hold on; plot([0 stims(1,j)],[0 stims(2,j)]); hold off;
%end
%end


 
