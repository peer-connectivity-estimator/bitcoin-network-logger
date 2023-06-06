filePath = 'GoodScoreIndividualPeerInfo.csv'

font_size = 20
line_width = 2
use_pseudonyms = 1
onlyFocusOnNumPeers = 0 % Zero for all peers
legendPosition = 'EastOutside' %'EastOutside'
legendNumColumns = 3
legendFontSize = 12
colors = {'#747E7E', '#72F2EB', '#00CCBF', '#3F7C85', '#405952', '#9C9B7A', '#FFD393', '#FF974F', '#F54F29', '#FF7DD4'}
figure('Position', [100 100 1500 600])

data = readmatrix(filePath);
data_str = readtable(filePath);
addresses = []
fid = fopen(filePath);
textscan(fid,'%[^,\r\n],', 1); % Skip the first cell
i = 1
while true
    cell0 = textscan(fid,'%[^,\r\n],', 1)
    cell = cell0{1}{1};
    if endsWith(cell, ' Score')
        if use_pseudonyms == 1
            addresses{i} = strcat("Node ", num2str(i))
        else
            addresses{i} = cell(1:end-6)
        end
        if onlyFocusOnNumPeers > 0 && onlyFocusOnNumPeers + 1 == i
            break
        end
        i = i + 1
    else
        break
    end
end
fclose(fid);

hold on;
x = data(:, 1)
for i=1:length(addresses)-1
    y = data(:, i + 1)
    if i <= length(colors)
        plot(x, y, '.', 'LineWidth', line_width, 'Color', colors{i})
    else
        plot(x, y, '.', 'LineWidth', line_width)
    end
end

xlabel('Epoch Timestamp (s)')
ylabel('Computed Score')

grid on;
box on;
set(gca, 'FontSize', font_size);
set(gca, 'XMinorTick','on', 'XMinorGrid','off', 'YMinorTick','on', 'YMinorGrid','on');
%set(gca, 'YScale', 'log')
xlim([min(x), max(x)])
%xtickangle(45)

legend(addresses, 'Location', legendPosition, 'NumColumns', legendNumColumns, 'FontSize', legendFontSize)